import os
import sys
from .tools import mcp


def main() -> None:
    if not os.getenv("MICROSOFT_MCP_CLIENT_ID"):
        print(
            "Error: MICROSOFT_MCP_CLIENT_ID environment variable is required",
            file=sys.stderr,
        )
        sys.exit(1)

    # Run with streamable HTTP transport
    # Default host is 0.0.0.0 and port is 8000
    # You can override with HOST and PORT environment variables
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8001"))
    
    print(f"Starting Microsoft MCP server with streamable-http transport on {host}:{port}", file=sys.stderr)
    print(f"Server will be available at: http://{host}:{port}/mcp/v1/", file=sys.stderr)
    
    mcp.run(transport="streamable-http", host=host, port=port)


if __name__ == "__main__":
    main()
