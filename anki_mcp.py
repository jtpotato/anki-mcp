import os
import sqlite3
import argparse
import time

ANKI_DB_PATH = os.path.expanduser(
    "~/Library/Application Support/Anki2/User 1/collection.anki2"
)


def read_decks():
    print("Reading deck status from Anki database...")
    if not os.path.exists(ANKI_DB_PATH):
        print(f"Database not found at {ANKI_DB_PATH}")
        return
    conn = sqlite3.connect(ANKI_DB_PATH)
    cursor = conn.cursor()
    try:
        # Get all decks (id, name)
        cursor.execute("SELECT id, name FROM decks;")
        decks = cursor.fetchall()
        if not decks:
            print("No decks found.")
            conn.close()
            return
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
            print(f"Deck: {deck_name}")
            print(f"  Due cards: {due_count}")
            print(f"  New cards: {new_count}")
            print()
    except sqlite3.Error as e:
        print(f"Error reading decks: {e}")
    conn.close()


def main():
    parser = argparse.ArgumentParser(description="Anki MCP Utility")
    parser.add_argument(
        "--read", action="store_true", help="Read and print the status of each deck"
    )
    args = parser.parse_args()

    if args.read:
        read_decks()
    else:
        print("Opening Anki SQLite database...")
        if not os.path.exists(ANKI_DB_PATH):
            print(f"Database not found at {ANKI_DB_PATH}")
            return
        conn = sqlite3.connect(ANKI_DB_PATH)
        cursor = conn.cursor()
        print("Tables in the database:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for table in tables:
            print(f"- {table[0]}")
        conn.close()


if __name__ == "__main__":
    main()
