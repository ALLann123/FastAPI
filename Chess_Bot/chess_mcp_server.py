#!/usr/bin/python3
"""
Chess MCP server (Step 3).

Wraps python-chess (rules) and Stockfish (engine) as MCP tools.

New in Step 3:
  * book_move()    - instant opening moves from a built-in opening book
  * engine_move()  - a single engine move, optionally Elo-limited (weaker opponent)
  * analyse()      - candidates now carry a `repeats` flag (for the repetition guard)
  * get_state()    - now reports `can_claim_draw`

Setup:
    pip install fastmcp python-chess
    Stockfish binary path: set STOCKFISH_PATH, or edit DEFAULT_STOCKFISH_PATH below.

NOTE: this server talks to its client over stdout (stdio transport), so never
use print() to stdout in here. Debug output goes to stderr.
"""
import atexit
import os
import random
import sys

import chess
import chess.engine
from fastmcp import FastMCP

# Fallback used when STOCKFISH_PATH is not visible to the server
# (MCP clients often launch servers with a filtered environment).
DEFAULT_STOCKFISH_PATH = r"J:\14_talk_back\stockfish\stockfish-windows-x86-64-universal.exe"

mcp = FastMCP("chess-server")

# One game held in memory (fine for now; we can key by game_id later).
board = chess.Board()

# Stockfish is launched lazily, so the server starts even if it is missing.
_engine: chess.engine.SimpleEngine | None = None


def _get_engine() -> chess.engine.SimpleEngine:
    """Return the running Stockfish engine, starting it on first use."""
    global _engine
    if _engine is None:
        path = os.getenv("STOCKFISH_PATH", DEFAULT_STOCKFISH_PATH)
        _engine = chess.engine.SimpleEngine.popen_uci(path)
    return _engine


@atexit.register
def _shutdown() -> None:
    """Cleanly stop the Stockfish subprocess when the server exits."""
    if _engine is not None:
        _engine.quit()


# ---------------------------------------------------------------------------
# Opening book
# ---------------------------------------------------------------------------
# Each line is a sequence of SAN moves from the starting position. We turn the
# lines into a lookup table: position -> list of book moves. A move that
# appears in several lines is listed several times, so popular moves get
# picked more often by random.choice.
OPENING_LINES = [
    # --- 1.e4 e5 ---
    "e4 e5 Nf3 Nc6 Bb5 a6 Ba4 Nf6 O-O Be7 Re1 b5 Bb3 d6 c3 O-O h3",         # Ruy Lopez
    "e4 e5 Nf3 Nc6 Bb5 Nf6 O-O Nxe4 d4 Nd6 Bxc6 dxc6 dxe5 Nf5 Qxd8+ Kxd8",   # Berlin
    "e4 e5 Nf3 Nc6 Bc4 Bc5 c3 Nf6 d3 d6 O-O O-O Re1 a6",                     # Italian
    "e4 e5 Nf3 Nc6 Bc4 Nf6 d4 exd4 O-O Nxe4 Re1 d5 Bxd5 Qxd5 Nc3 Qa5",       # Two Knights
    "e4 e5 Nf3 Nc6 d4 exd4 Nxd4 Nf6 Nxc6 bxc6 e5 Qe7 Qe2 Nd5 c4 Ba6",        # Scotch
    "e4 e5 Nf3 Nf6 Nxe5 d6 Nf3 Nxe4 d4 d5 Bd3 Nc6 O-O Be7 c4 Nb4",           # Petroff
    # --- Sicilian ---
    "e4 c5 Nf3 d6 d4 cxd4 Nxd4 Nf6 Nc3 a6 Be3 e5 Nb3 Be6 f3 Be7 Qd2 O-O O-O-O Nbd7",  # Najdorf
    "e4 c5 Nf3 d6 d4 cxd4 Nxd4 Nf6 Nc3 g6 Be3 Bg7 f3 O-O Qd2 Nc6 Bc4 Bd7 O-O-O Rc8",  # Dragon
    "e4 c5 Nf3 Nc6 d4 cxd4 Nxd4 Nf6 Nc3 d6 Bg5 e6 Qd2 a6 O-O-O Bd7",         # Richter-Rauzer
    "e4 c5 Nf3 Nc6 d4 cxd4 Nxd4 Nf6 Nc3 e5 Ndb5 d6 Bg5 a6 Na3 b5 Nd5 Be7",   # Sveshnikov
    # --- Other 1.e4 defences ---
    "e4 e6 d4 d5 Nc3 Nf6 Bg5 Be7 e5 Nfd7 Bxe7 Qxe7 f4 O-O Nf3 c5",           # French Classical
    "e4 e6 d4 d5 Nd2 Nf6 e5 Nfd7 Bd3 c5 c3 Nc6 Ne2 cxd4 cxd4 f6",            # French Tarrasch
    "e4 c6 d4 d5 Nc3 dxe4 Nxe4 Bf5 Ng3 Bg6 h4 h6 Nf3 Nd7 h5 Bh7 Bd3 Bxd3 Qxd3 e6",  # Caro-Kann
    "e4 c6 d4 d5 e5 Bf5 Nf3 e6 Be2 c5 Be3 Qb6 Nbd2 Nc6",                     # Caro-Kann Advance
    "e4 d5 exd5 Qxd5 Nc3 Qa5 d4 Nf6 Nf3 c6 Bc4 Bf5 Bd2 e6",                  # Scandinavian
    "e4 d6 d4 Nf6 Nc3 g6 Nf3 Bg7 Be2 O-O O-O c6",                             # Pirc
    # --- 1.d4 ---
    "d4 d5 c4 e6 Nc3 Nf6 Bg5 Be7 e3 O-O Nf3 h6 Bh4 b6",                      # QGD
    "d4 d5 c4 dxc4 Nf3 Nf6 e3 e6 Bxc4 c5 O-O a6",                             # QGA
    "d4 d5 c4 c6 Nf3 Nf6 Nc3 dxc4 a4 Bf5 e3 e6 Bxc4 Bb4 O-O Nbd7",           # Slav
    "d4 Nf6 c4 g6 Nc3 Bg7 e4 d6 Nf3 O-O Be2 e5 O-O Nc6 d5 Ne7",              # King's Indian
    "d4 Nf6 c4 e6 Nc3 Bb4 e3 O-O Bd3 d5 Nf3 c5 O-O Nc6 a3 Bxc3 bxc3 dxc4 Bxc4 Qc7",  # Nimzo-Indian
    "d4 Nf6 c4 g6 Nc3 d5 cxd5 Nxd5 e4 Nxc3 bxc3 Bg7 Nf3 c5 Be3 Qa5 Qd2 O-O",  # Grunfeld
    "d4 Nf6 c4 e6 g3 d5 Bg2 Be7 Nf3 O-O O-O dxc4 Qc2 a6 Qxc4 b5",            # Catalan
    "d4 Nf6 c4 e6 Nf3 b6 g3 Ba6 b3 Bb4+ Bd2 Be7 Bg2 c6 Bc3 d5",              # Queen's Indian
    "d4 d5 Bf4 Nf6 e3 c5 c3 Nc6 Nd2 e6 Ngf3 Bd6 Bg3 O-O",                    # London
    "d4 f5 g3 Nf6 Bg2 e6 Nf3 Be7 O-O O-O c4 d6",                              # Dutch
    # --- Flank openings ---
    "c4 e5 Nc3 Nf6 Nf3 Nc6 g3 d5 cxd5 Nxd5 Bg2 Nb6 O-O Be7",                 # English
    "c4 c5 Nc3 Nc6 g3 g6 Bg2 Bg7 Nf3 e6 O-O Nge7",                            # English Symmetrical
    "Nf3 d5 g3 Nf6 Bg2 e6 O-O Be7 d3 O-O Nbd2 c5",                            # Reti
]


def _build_book() -> dict[str, list[str]]:
    """Replay every line and record the move played from each position."""
    book: dict[str, list[str]] = {}
    for line in OPENING_LINES:
        b = chess.Board()
        try:
            for san in line.split():
                mv = b.parse_san(san)
                # epd() = position + side to move + castling + en passant,
                # without move counters, so transpositions share an entry.
                book.setdefault(b.epd(), []).append(mv.uci())
                b.push(mv)
        except ValueError as e:
            # Don't crash the server over one bad line; just skip its remainder.
            print(f"[book] skipped rest of line {line!r}: {e}", file=sys.stderr)
    return book


_BOOK = _build_book()


# ---------------------------------------------------------------------------
# State snapshot
# ---------------------------------------------------------------------------
def _state() -> dict:
    """Build a JSON-friendly snapshot of the game, returned by several tools."""
    return {
        "fen": board.fen(),
        "turn": "white" if board.turn == chess.WHITE else "black",
        "move_number": board.fullmove_number,
        "history_san": chess.Board().variation_san(board.move_stack)
        if board.move_stack
        else "",
        "in_check": board.is_check(),
        "game_over": board.is_game_over(),
        "result": board.result() if board.is_game_over() else None,
        # True when threefold repetition or the 50-move rule lets a player
        # claim a draw (the game isn't "over" until someone claims).
        "can_claim_draw": board.can_claim_draw(),
        "ascii": str(board),
    }


# ---------------------------------------------------------------------------
# MCP tools
# ---------------------------------------------------------------------------
@mcp.tool
def new_game(fen: str | None = None) -> dict:
    """Start a new game from the standard position, or from a given FEN."""
    global board
    board = chess.Board(fen) if fen else chess.Board()
    return _state()


@mcp.tool
def get_state() -> dict:
    """Return the current position: FEN, side to move, history, game status."""
    return _state()


@mcp.tool
def legal_moves() -> list[dict]:
    """List all legal moves for the side to move, in UCI and SAN."""
    return [{"uci": m.uci(), "san": board.san(m)} for m in board.legal_moves]


@mcp.tool
def make_move(move: str) -> dict:
    """Play a move given in UCI (e2e4) or SAN (e4, Nf3). Rejects illegal moves."""
    try:
        try:
            mv = board.parse_uci(move)
        except ValueError:
            mv = board.parse_san(move)
    except ValueError:
        return {"ok": False, "error": f"Illegal or unparseable move: {move}"}
    san = board.san(mv)  # SAN must be computed BEFORE pushing
    board.push(mv)
    return {"ok": True, "played": san, "state": _state()}


@mcp.tool
def undo_move() -> dict:
    """Take back the last move."""
    if not board.move_stack:
        return {"ok": False, "error": "No moves to undo"}
    board.pop()
    return {"ok": True, "state": _state()}


@mcp.tool
def book_move() -> dict:
    """
    Look up the current position in the opening book.
    Returns {"found": True, "uci": ..., "san": ...} or {"found": False}.
    Does NOT play the move; call make_move for that.
    """
    options = _BOOK.get(board.epd())
    if not options:
        return {"found": False}
    uci = random.choice(options)  # popular moves appear more often in the list
    return {"found": True, "uci": uci, "san": board.san(chess.Move.from_uci(uci))}


@mcp.tool
def analyse(think_time: float = 0.5, candidates: int = 3) -> list[dict]:
    """
    Ask Stockfish for the best candidate moves (does not play anything).
    cp is in centipawns from the side-to-move's point of view; mate scores are
    huge numbers and `mate_in` is set. `repeats` is True if the move would
    repeat a position that has already occurred.
    """
    if board.is_game_over():
        return []
    infos = _get_engine().analyse(
        board,
        chess.engine.Limit(time=max(0.01, think_time)),
        multipv=max(1, candidates),
    )
    results = []
    for info in infos:
        pv = info.get("pv")
        if not pv:
            continue
        score = info["score"].pov(board.turn)
        san = board.san(pv[0])  # before pushing
        # Try the move, ask whether it repeats a position, then undo it.
        board.push(pv[0])
        repeats = board.is_repetition(2)
        board.pop()
        results.append(
            {
                "uci": pv[0].uci(),
                "san": san,
                "cp": score.score(mate_score=100_000),
                "mate_in": score.mate(),
                "depth": info.get("depth"),
                "repeats": repeats,
            }
        )
    return results


@mcp.tool
def engine_move(think_time: float = 0.1, elo: int | None = None) -> dict:
    """
    Get ONE move from Stockfish (does not play it). If `elo` is given
    (about 1320-3190), Stockfish deliberately plays at that strength, which
    makes a handy weaker opponent. This uses engine.play(), because Stockfish
    only weakens its chosen move, not the analysis lines that analyse() reads.
    """
    if board.is_game_over():
        return {"ok": False, "error": "Game is over"}
    engine = _get_engine()
    if elo is not None:
        engine.configure(
            {"UCI_LimitStrength": True, "UCI_Elo": max(1320, min(3190, elo))}
        )
    try:
        result = engine.play(board, chess.engine.Limit(time=max(0.01, think_time)))
    finally:
        if elo is not None:
            engine.configure({"UCI_LimitStrength": False})  # back to full strength
    return {"ok": True, "uci": result.move.uci(), "san": board.san(result.move)}


if __name__ == "__main__":
    mcp.run()