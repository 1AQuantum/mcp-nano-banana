import sys
from .nano_banana_server import mcp


def main() -> None:
    # Always run as stdio for MCP portability
    mcp.run("stdio")


if __name__ == "__main__":
    main()


