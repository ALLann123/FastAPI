"""
Step 3: the finished decision graph.

    START -> setup -> observe --(game over / flagged / draw claim)--------> END
                         |
                         +--(opponent's turn)--> opponent ------------------+
                         |                                                  v
                         +--(bot's turn)--> book --hit---------------------> play
                                              |                              ^
                                              +--miss--> probe --obvious/----+
                                                           |     decisive -> choose
                                                           +--contested--> deep_think -> choose
    play -> observe   (the loop)

  book        instant move from the opening book (no engine)
  probe       a quick, cheap Stockfish look at the top 3 moves
  deep_think  a longer look, only when the position is contested
  choose      picks the move: best score, with a repetition guard

Run (from the folder containing chess_mcp_server.py):
    python chess_agent.py
"""
import asyncio
import random
import time
from pathlib import Path
from typing import TypedDict

from fastmcp import Client
from langgraph.graph import END, START, StateGraph

# ---------------------------------------------------------------------------
# Settings you can play with
# ---------------------------------------------------------------------------
SERVER_PATH = Path(__file__).parent / "chess_mcp_server.py"
BOT_COLOR = "white"          # which side our agent plays
PRINT_GRAPH = False          # True prints the graph as Mermaid text

# Simulated clock for the bot (a "1 minute game"). None = no clock.
BOT_CLOCK_START: float | None = 60.0
INCREMENT = 0.0              # seconds added after each bot move

# Opponent: "random" plays random legal moves; "engine" plays Stockfish.
OPPONENT_MODE = "engine"
OPPONENT_ELO: int | None = 1500   # None = full strength (min useful value ~1320)
OPPONENT_THINK_TIME = 0.1

MAX_PLIES = 400              # safety stop (a ply is one half-move)

# Decision thresholds, in centipawns (100 cp is roughly one pawn).
OBVIOUS_GAP = 150            # best move beats #2 by this much -> don't overthink
DECISIVE = 400               # game already won/lost -> don't overthink
NOT_LOSING = -50             # above this we avoid repeating positions
REPEAT_TOLERANCE = 25        # accept a non-repeating move at most this much worse


class GameState(TypedDict, total=False):
    fen: str
    turn: str                    # "white" / "black"
    game_over: bool
    can_claim_draw: bool
    result: str | None
    history_san: str
    ply: int                     # half-moves played
    pending_move: str | None     # chosen move (UCI) waiting to be played
    candidates: list[dict]       # Stockfish's candidate moves, best first
    source: str                  # "book" / "probe" / "deep": where the move came from
    bot_clock: float | None      # seconds the bot has left
    spent: float                 # seconds spent thinking on the current move


def time_budget(clock: float | None, ply: int) -> float:
    """Seconds we can afford for a 'normal' move."""
    if clock is None:
        return 0.5
    # Assume ~40 moves remain at the start, never fewer than 20: spend roughly
    # clock/moves_left, capped at 2s. This shrinks as the clock shrinks, so
    # the bot can't run itself out of time by thinking too much.
    moves_left = max(20, 40 - ply // 2)
    return max(0.05, min(clock / moves_left, 2.0))


def build_graph(client: Client):
    """Build the graph. Nodes are closures so they can share the MCP client."""

    async def call(tool: str, args: dict | None = None):
        """Call an MCP tool and return its data."""
        return (await client.call_tool(tool, args or {})).data

    # --- Nodes --------------------------------------------------------------

    async def setup(state: GameState) -> dict:
        await call("new_game")
        return {
            "ply": 0,
            "pending_move": None,
            "bot_clock": BOT_CLOCK_START,
            "spent": 0.0,
        }

    async def observe(state: GameState) -> dict:
        s = await call("get_state")
        return {
            "fen": s["fen"],
            "turn": s["turn"],
            "game_over": s["game_over"],
            "can_claim_draw": s["can_claim_draw"],
            "result": s["result"],
            "history_san": s["history_san"],
        }

    async def book(state: GameState) -> dict:
        """Opening book: an instant move if we know this position."""
        hit = await call("book_move")
        if hit["found"]:
            print(f"      book: {hit['san']}")
            return {"pending_move": hit["uci"], "source": "book"}
        return {"pending_move": None}

    async def probe(state: GameState) -> dict:
        """Quick look: top 3 moves for a fraction of the normal budget."""
        base = time_budget(state.get("bot_clock"), state["ply"])
        t0 = time.perf_counter()
        cands = await call(
            "analyse", {"think_time": max(0.05, base * 0.25), "candidates": 3}
        )
        spent = state.get("spent", 0.0) + (time.perf_counter() - t0)
        cands.sort(key=lambda c: c["cp"], reverse=True)
        return {"candidates": cands, "source": "probe", "spent": spent}

    async def deep_think(state: GameState) -> dict:
        """Longer look, used only when the position is contested."""
        clock = state.get("bot_clock")
        t = time_budget(clock, state["ply"]) * 2.5
        if clock is not None:
            t = min(t, max(0.1, clock * 0.15))  # never burn >15% of the clock
        t0 = time.perf_counter()
        cands = await call("analyse", {"think_time": t, "candidates": 3})
        spent = state.get("spent", 0.0) + (time.perf_counter() - t0)
        cands.sort(key=lambda c: c["cp"], reverse=True)
        return {"candidates": cands, "source": "deep", "spent": spent}

    async def choose(state: GameState) -> dict:
        """Pick the move: the best-scoring one, unless it needlessly repeats."""
        cands = state["candidates"]
        pick = cands[0]
        # Repetition guard: if we're not losing and the best move repeats a
        # position, prefer a nearly-as-good move that doesn't.
        if pick["cp"] > NOT_LOSING and pick["repeats"]:
            for c in cands[1:]:
                if pick["cp"] - c["cp"] <= REPEAT_TOLERANCE and not c["repeats"]:
                    pick = c
                    break

        # Charge the thinking time to our clock (and add the increment).
        clock = state.get("bot_clock")
        if clock is not None:
            clock = clock - state.get("spent", 0.0) + INCREMENT

        shown = ", ".join(f"{c['san']} ({c['cp']:+d})" for c in cands)
        clock_txt = f"  clock={clock:.1f}s" if clock is not None else ""
        print(f"      {state['source']}: {shown}{clock_txt}")
        return {"pending_move": pick["uci"], "bot_clock": clock, "spent": 0.0}

    async def opponent(state: GameState) -> dict:
        if OPPONENT_MODE == "random":
            moves = await call("legal_moves")
            return {"pending_move": random.choice(moves)["uci"]}
        m = await call(
            "engine_move", {"think_time": OPPONENT_THINK_TIME, "elo": OPPONENT_ELO}
        )
        return {"pending_move": m["uci"]}

    async def play(state: GameState) -> dict:
        data = await call("make_move", {"move": state["pending_move"]})
        if not data["ok"]:
            raise RuntimeError(f"Server rejected move: {data['error']}")
        ply = state["ply"] + 1
        print(f"{ply:3}. {state['turn']:5} plays {data['played']}")
        return {"ply": ply, "pending_move": None}

    # --- Routing ------------------------------------------------------------

    def after_observe(state: GameState) -> str:
        clock = state.get("bot_clock")
        if state["game_over"] or state["can_claim_draw"] or state["ply"] >= MAX_PLIES:
            return "end"
        if clock is not None and clock <= 0:
            return "end"  # the bot ran out of time
        return "book" if state["turn"] == BOT_COLOR else "opponent"

    def after_book(state: GameState) -> str:
        return "play" if state.get("pending_move") else "probe"

    def after_probe(state: GameState) -> str:
        c = state["candidates"]
        if len(c) < 2:
            return "choose"  # only one legal move
        if c[0]["cp"] - c[1]["cp"] >= OBVIOUS_GAP:
            return "choose"  # one clearly best move
        if abs(c[0]["cp"]) >= DECISIVE:
            return "choose"  # already decided: don't waste clock
        return "deep"        # contested: this is where thinking time pays off

    # --- Wiring -------------------------------------------------------------

    g = StateGraph(GameState)
    for name, fn in [
        ("setup", setup), ("observe", observe), ("book", book), ("probe", probe),
        ("deep_think", deep_think), ("choose", choose),
        ("opponent", opponent), ("play", play),
    ]:
        g.add_node(name, fn)

    g.add_edge(START, "setup")
    g.add_edge("setup", "observe")
    g.add_conditional_edges(
        "observe", after_observe, {"book": "book", "opponent": "opponent", "end": END}
    )
    g.add_conditional_edges("book", after_book, {"play": "play", "probe": "probe"})
    g.add_conditional_edges(
        "probe", after_probe, {"choose": "choose", "deep": "deep_think"}
    )
    g.add_edge("deep_think", "choose")
    g.add_edge("choose", "play")
    g.add_edge("opponent", "play")
    g.add_edge("play", "observe")
    return g.compile()


async def main() -> None:
    async with Client(SERVER_PATH) as client:
        graph = build_graph(client)
        if PRINT_GRAPH:
            print(graph.get_graph().draw_mermaid())

        # A game is ~4 graph steps per move, so raise LangGraph's default limit of 25.
        final = await graph.ainvoke({"ply": 0}, config={"recursion_limit": 3000})

        print("\nGame over.")
        if final.get("game_over"):
            print("Result:", final["result"])
        elif final.get("can_claim_draw"):
            print("Result: draw claimed (repetition or 50-move rule)")
        elif final.get("bot_clock") is not None and final["bot_clock"] <= 0:
            print("Result: the bot lost on time")
        else:
            print("Stopped at MAX_PLIES")
        print("Moves:", final["history_san"])


if __name__ == "__main__":
    asyncio.run(main())