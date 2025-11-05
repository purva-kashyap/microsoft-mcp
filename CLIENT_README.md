# Microsoft MCP Client

Simple Python client to connect to the Microsoft MCP server via streamable-http transport.

## Prerequisites

1. Make sure the MCP server is running:
   ```bash
   MICROSOFT_MCP_CLIENT_ID=your-client-id PORT=8001 uv run microsoft-mcp
   ```

2. Install client dependencies:
   ```bash
   pip install -r client-requirements.txt
   ```

## Usage

Run the client:
```bash
python client.py
```

The client will:
1. Connect to the MCP server at `http://127.0.0.1:8001/mcp/v1/`
2. Check for existing authenticated accounts
3. If no accounts exist, start the device flow authentication:
   - Display a URL and code
   - Wait for you to authenticate in your browser
   - Complete the authentication
4. List your latest 5 emails from the inbox

## What it does

- **Connects** to the streamable-http MCP server
- **Authenticates** using Microsoft device flow (if needed)
- **Lists** your inbox emails with subject, sender, and date
- **Displays** read status and attachment indicators

## Customization

Edit `client.py` to:
- Change the server URL (default: `http://127.0.0.1:8001/mcp/v1/`)
- Adjust email limit or folder
- Enable `include_body: True` to get full email content
- Use other MCP tools like `send_email`, `list_calendar_events`, etc.
