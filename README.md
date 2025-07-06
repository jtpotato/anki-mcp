# anki-mcp

anki-mcp is a Model Context Protocol (MCP) server that provides programmatic access to your Anki decks. It allows you to read the status of your Anki decks, including the number of due and new cards, by connecting directly to your Anki database.

## Features

- List all decks in your Anki collection
- Show the number of due and new cards for each deck

## Requirements

- Python 3.12+
- Anki desktop (for access to the local database)
- [mcp](https://github.com/modelcontext/mcp) Python package

## Installation

Add this to your client.

```json
{
  "anki-mcp": {
    "command": "uvx",
    "args": [
      "--from",
      "git+https://github.com/jtpotato/anki-mcp@main",
      "anki-mcp"
    ]
  }
}
```

By default, it will connect to your Anki database at:

```
~/Library/Application Support/Anki2/User 1/collection.anki2
```
