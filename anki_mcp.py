import os
import sqlite3
import time
from typing import List

from mcp.server.fastmcp import FastMCP

mcp: FastMCP = FastMCP("anki-mcp")

ANKI_DB_PATH = os.path.expanduser(
    "~/Library/Application Support/Anki2/User 1/collection.anki2"
)


@mcp.tool()
def read_decks() -> str:
    """Read and print the due/new cards of each deck in the Anki database."""
    result: List[str] = []

    print("Reading deck status from Anki database...")

    if not os.path.exists(ANKI_DB_PATH):
        return f"Database not found at {ANKI_DB_PATH}"
    conn = sqlite3.connect(ANKI_DB_PATH)
    cursor = conn.cursor()
    try:
        # Get all decks (id, name)
        cursor.execute("SELECT id, name FROM decks;")
        decks = cursor.fetchall()
        if not decks:
            conn.close()
            return "No decks found."
        # Get current day (days since epoch)
        current_day = int(time.time() // 86400)
        # For each deck, count due and new cards
        for deck_id, deck_name in decks:
            # Due cards: queue=2 (review) or queue=1 (learning), due <= current_day
            cursor.execute(
                """
                SELECT COUNT(*) FROM cards
                WHERE did = ? AND queue IN (1,2) AND due <= ?
                """,
                (deck_id, current_day),
            )
            due_count = cursor.fetchone()[0]
            # New cards: queue=0 (new)
            cursor.execute(
                """
                SELECT COUNT(*) FROM cards
                WHERE did = ? AND queue = 0
                """,
                (deck_id,),
            )
            new_count = cursor.fetchone()[0]
            result.append(f"Deck: {deck_name}")
            result.append(f"  Due cards: {due_count}")
            result.append(f"  New cards: {new_count}")
            result.append("")
    except sqlite3.Error as e:
        conn.close()
        return f"Error reading decks: {e}"
    conn.close()
    return "\n".join(result)


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
