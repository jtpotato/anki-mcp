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
        # Get current day (days since collection creation)
        now_unix = int(time.time())
        today_unix_day = now_unix // 86400
        cursor.execute("SELECT crt FROM col;")
        col_row = cursor.fetchone()
        if not col_row:
            conn.close()
            return "Could not read collection creation date."
        col_crt_sec = col_row[0]  # seconds since Unix epoch
        col_crt_day = int(col_crt_sec // 86400)
        current_day = int(today_unix_day - col_crt_day)
        # print(current_day, "current day since collection creation")
        # For each deck, count due and new cards
        for deck_id, deck_name in decks:
            # Query 1: All review cards (queue = 2), show due and front text for debugging
            cursor.execute(
                """
                SELECT cards.id, cards.due, notes.flds
                FROM cards
                JOIN notes ON cards.nid = notes.id
                WHERE cards.did = ? AND cards.queue = 2 AND cards.type = 2
                """,
                (deck_id,),
            )
            all_review_cards = cursor.fetchall()
            debug_info = []
            review_due = 0
            for card_id, due, flds in all_review_cards:
                front = flds.split("\x1f")[0] if flds else ""
                if due <= current_day:
                    # print(due, current_day)
                    review_due += 1
                # debug_info.append(f"(id={card_id}, due={due}, front='{front}')")
            # result.append(f"  Debug: All review cards: {debug_info}")

            # Query 2: Learning cards (queue = 1), due in seconds (Unix time)
            cursor.execute(
                """
                SELECT COUNT(*) FROM cards
                WHERE did = ? AND queue = 1 AND due <= ?
                """,
                (deck_id, now_unix),
            )
            learning_due = cursor.fetchone()[0]

            # Query 3: New cards (queue = 0)
            cursor.execute(
                """
                SELECT COUNT(*) FROM cards
                WHERE did = ? AND queue = 0
                """,
                (deck_id,),
            )
            new_count = cursor.fetchone()[0]
            result.append(f"Deck: {deck_name}")
            result.append(f"  Review due: {review_due}")
            result.append(f"  Learning due: {learning_due}")
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
    # main()
    print(read_decks())
