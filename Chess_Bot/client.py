"""
Smoke test for chess_mcp_server.py.
Run from the same folder:  python test_client.py
"""
import asyncio

from fastmcp import Client


async def main():
    # Passing a .py path makes FastMCP launch the server as a stdio subprocess.
    async with Client("chess_mcp_server.py") as client:
        # 1. Confirm the server exposes our tools.
        tools = await client.list_tools()
        print("Tools:", [t.name for t in tools])

        # 2. Start a game and play 1. e4.
        await client.call_tool("new_game", {})
        move = await client.call_tool("make_move", {"move": "e4"})
        print("Played:", move.data["played"])

        # 3. Ask Stockfish for Black's best replies (this also proves the
        #    Stockfish path is correct).
        result = await client.call_tool("analyse", {"think_time": 0.3})
        print("Black's candidates:")
        for c in result.data:
            print(f"  {c['san']:6} cp={c['cp']:5} depth={c['depth']}")


asyncio.run(main())

"""
Chess_Bot>python client.py
Tools: ['new_game', 'get_state', 'legal_moves', 'make_move', 'undo_move', 'analyse']
Played: e4
Black's candidates:
  c5     cp=  -35 depth=11
  e5     cp=  -35 depth=11
  d6     cp=  -41 depth=10

"""