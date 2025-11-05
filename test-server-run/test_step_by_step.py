#!/usr/bin/env python3
"""Step by step client test"""
import asyncio
import json
from fastmcp import Client

async def main():
    print("🚀 Starting MCP client...")
    
    try:
        print("📡 Connecting to server...")
        async with Client("http://0.0.0.0:8001/mcp/") as client:
            print("✅ Connected!")
            
            print("\n🔧 Listing tools...")
            tools = await client.list_tools()
            print(f"✅ Found {len(tools)} tools")
            
            print("\n👥 Calling list_accounts...")
            accounts_result = await client.call_tool("list_accounts", {})
            print(f"✅ Got result: {accounts_result}")
            
            if accounts_result.content:
                accounts_text = accounts_result.content[0].text
                print(f"📄 Accounts data: {accounts_text}")
                accounts = json.loads(accounts_text)
                print(f"✅ Parsed {len(accounts) if isinstance(accounts, list) else 'dict'} accounts")
            
            print("\n✅ All tests passed!")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(main())
