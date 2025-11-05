#!/usr/bin/env python3
"""
MCP Client for Microsoft MCP Server
Connects via streamable-http (HTTP POST with JSON-RPC), authenticates a user, and retrieves emails
"""
import asyncio
import sys
import httpx
import json


class SimpleMCPClient:
    """Simple MCP client for streamable-http transport"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=60.0)
        self.request_id = 0
        self.session_id = None
        
    async def initialize(self):
        """Initialize the MCP session"""
        result = await self._request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "simple-mcp-client",
                "version": "1.0.0"
            }
        })
        return result
        
    async def list_tools(self):
        """List available tools"""
        return await self._request("tools/list", {})
        
    async def call_tool(self, tool_name: str, arguments: dict):
        """Call a tool with arguments"""
        return await self._request("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })
        
    async def _request(self, method: str, params: dict):
        """Make a JSON-RPC request"""
        self.request_id += 1
        payload = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        
        # Add session ID to headers if we have one
        if self.session_id:
            headers["MCP-Session-Id"] = self.session_id
        
        response = await self.client.post(
            f"{self.base_url}/messages",
            json=payload,
            headers=headers
        )
        
        # Capture session ID from response headers
        if "MCP-Session-Id" in response.headers:
            self.session_id = response.headers["MCP-Session-Id"]
        
        if response.status_code != 200:
            raise Exception(f"HTTP {response.status_code}: {response.text}")
        
        # Handle SSE response (text/event-stream)
        if "text/event-stream" in response.headers.get("content-type", ""):
            # Parse SSE format
            text = response.text.strip()
            lines = text.split('\n')
            
            # Debug: print response
            print(f"DEBUG: SSE Response ({len(lines)} lines):")
            for i, line in enumerate(lines[:5]):  # Show first 5 lines
                print(f"  Line {i}: {repr(line)}")
            
            for line in lines:
                if line.startswith('data: '):
                    data_str = line[6:]  # Remove 'data: ' prefix
                    if data_str.strip() and data_str.strip() != '[DONE]':
                        result = json.loads(data_str)
                        if "error" in result:
                            raise Exception(f"MCP Error: {result['error']}")
                        return result.get("result", {})
            raise Exception(f"No valid data found in SSE response. Got {len(lines)} lines")
        else:
            # Handle JSON response
            result = response.json()
            if "error" in result:
                raise Exception(f"MCP Error: {result['error']}")
            return result.get("result", {})
        
    async def close(self):
        await self.client.aclose()


async def main():
    server_url = "http://127.0.0.1:8001"
    
    print(f"🔌 Connecting to MCP server at {server_url}...")
    
    client = SimpleMCPClient(server_url)
    
    try:
        # Initialize the connection
        await client.initialize()
        
        print("✅ Connected to server successfully!")
        
        # List available tools
        tools_result = await client.list_tools()
        tools = tools_result.get("tools", [])
        print(f"\n🛠️  Available tools ({len(tools)}):")
        for tool in tools[:5]:  # Show first 5
            print(f"  - {tool['name']}: {tool.get('description', 'No description')}")
        if len(tools) > 5:
            print(f"  ... and {len(tools) - 5} more")
        
        # Check if user already has accounts
        print("\n🔍 Checking for existing accounts...")
        list_accounts_result = await client.call_tool("list_accounts", {})
        
        # Extract the content from the tool result
        content = list_accounts_result.get("content", [])
        if content and len(content) > 0:
            accounts_text = content[0].get("text", "[]")
        else:
            accounts_text = "[]"
            
        print(f"Existing accounts: {accounts_text}")
        accounts_list = json.loads(accounts_text)
        
        if not accounts_list:
            print("\n🔐 No accounts found. Starting authentication flow...")
            
            # Start authentication
            auth_result = await client.call_tool("authenticate_account", {})
            auth_content = auth_result.get("content", [])
            if not auth_content:
                print("❌ No authentication data returned")
                return
                
            auth_data = json.loads(auth_content[0].get("text", "{}"))
            
            print(f"\n📱 Authentication Required:")
            print(f"  1. Visit: {auth_data['verification_url']}")
            print(f"  2. Enter code: {auth_data['device_code']}")
            print(f"  3. Sign in with your Microsoft account")
            print(f"\n⏳ Waiting for you to complete authentication...")
            print(f"   (Code expires in {auth_data['expires_in']} seconds)")
            
            # Wait for user to authenticate
            input("\nPress Enter after you've completed authentication in your browser...")
            
            # Complete authentication
            print("\n🔄 Completing authentication...")
            complete_result = await client.call_tool(
                "complete_authentication",
                {"flow_cache": auth_data["_flow_cache"]}
            )
            complete_content = complete_result.get("content", [])
            if not complete_content:
                print("❌ No completion data returned")
                return
                
            complete_data = json.loads(complete_content[0].get("text", "{}"))
            
            if complete_data.get("status") == "success":
                print(f"✅ Authentication successful!")
                print(f"   Username: {complete_data['username']}")
                print(f"   Account ID: {complete_data['account_id']}")
                account_id = complete_data["account_id"]
            elif complete_data.get("status") == "pending":
                print(f"⚠️  Authentication still pending. Please complete the process and try again.")
                return
            else:
                print(f"❌ Authentication failed: {complete_data.get('message')}")
                return
        else:
            print(f"✅ Found {len(accounts_list)} existing account(s)")
            account_id = accounts_list[0]["account_id"]
            print(f"   Using account: {accounts_list[0]['username']}")
        
        # Get emails
        print(f"\n📧 Retrieving emails for account {account_id}...")
        emails_result = await client.call_tool(
            "list_emails",
            {
                "account_id": account_id,
                "folder": "inbox",
                "limit": 5,
                "include_body": False
            }
        )
        
        emails_content = emails_result.get("content", [])
        if not emails_content:
            print("❌ No email data returned")
            return
            
        emails = json.loads(emails_content[0].get("text", "[]"))
        print(f"\n📬 Latest {len(emails)} emails:")
        for i, email in enumerate(emails, 1):
            print(f"\n  {i}. Subject: {email['subject']}")
            print(f"     From: {email['from']['emailAddress']['address']}")
            print(f"     Date: {email['receivedDateTime']}")
            print(f"     Read: {'Yes' if email['isRead'] else 'No'}")
            if email.get('hasAttachments'):
                print(f"     📎 Has attachments")
        
        print("\n✅ Done! Successfully retrieved emails from Microsoft MCP server.")
        
    finally:
        await client.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user")
        sys.exit(0)
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
