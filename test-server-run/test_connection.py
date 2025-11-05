#!/usr/bin/env python3
"""Simple connection test"""
import asyncio
from fastmcp import Client

async def main():
    print("Attempting to connect...")
    try:
        # Set a timeout
        async with asyncio.timeout(10):
            async with Client("http://0.0.0.0:8001/mcp/") as client:
                print("✅ Connected!")
                tools = await client.list_tools()
                print(f"Found {len(tools)} tools")
    except asyncio.TimeoutError:
        print("❌ Timeout - server took too long to respond")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(main())
