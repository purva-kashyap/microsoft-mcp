import asyncio
import json
from fastmcp import Client

async def main():
    print("🚀 Starting MCP client...")
    try:
        async with Client("http://0.0.0.0:8001/mcp/") as client:
            # List available tools
            print("📡 Connecting to server...")
            tools = await client.list_tools()
            tool_count = len(tools) if isinstance(tools, list) else len(tools.tools)
            print(f"✅ Connected! Found {tool_count} tools\n")

            # Check if user already has accounts
            print("🔍 Checking for existing accounts...")
            try:
                accounts_result = await client.call_tool("list_accounts", {})
                
                # Extract the content from CallToolResult
                if accounts_result.content and len(accounts_result.content) > 0:
                    account_list_text = accounts_result.content[0].text
                    account_list = json.loads(account_list_text)
                    
                    print(f"[DEBUG] Account list type: {type(account_list)}")
                    print(f"[DEBUG] Account list: {account_list}")
                    
                    # Check if account_list is empty (could be a list or dict)
                    if isinstance(account_list, list):
                        has_accounts = len(account_list) > 0
                    else:
                        has_accounts = bool(account_list)
                    
                    print(f"[DEBUG] has_accounts: {has_accounts}")
                else:
                    has_accounts = False
                    print("[DEBUG] No content in accounts_result")
            except Exception as e:
                print(f"⚠️  Error checking accounts: {e}")
                import traceback
                traceback.print_exc()
                has_accounts = False
            
            if not has_accounts:
                print("❌ No accounts found. Starting authentication...\n")
                
                # Start authentication
                print("🔄 Requesting device code from server...")
                auth_result = await client.call_tool("authenticate_account", {})
                print(f"📦 Raw auth result: {auth_result}")
                auth_data = json.loads(auth_result.content[0].text)
                print(f"📄 Parsed auth data: {auth_data}")
                
                print("\n" + "="*60)
                print("📱 MICROSOFT AUTHENTICATION REQUIRED")
                print("="*60)
                print(f"\n🌐 Step 1: Open this URL in your browser:")
                print(f"   {auth_data['verification_url']}")
                print(f"\n🔑 Step 2: Enter this code:")
                print(f"   {auth_data['device_code']}")
                print(f"\n👤 Step 3: Sign in with your Microsoft account")
                print(f"\n⏰ This code expires in {auth_data['expires_in']} seconds")
                print("="*60)
                
                # Wait for user to authenticate
                input("\n👉 Press Enter after you've completed authentication in your browser...")
                
                # Complete authentication
                print("\n🔄 Completing authentication...")
                complete_result = await client.call_tool(
                    "complete_authentication",
                    {"flow_cache": auth_data["_flow_cache"]}
                )
                complete_data = json.loads(complete_result.content[0].text)
                
                if complete_data.get("status") == "success":
                    print(f"✅ Authentication successful!")
                    print(f"   Username: {complete_data['username']}")
                    account_id = complete_data["account_id"]
                    username = complete_data["username"]
                elif complete_data.get("status") == "pending":
                    print("⚠️  Authentication still pending. Please complete it and try again.")
                    return
                else:
                    print(f"❌ Authentication failed: {complete_data.get('message')}")
                    return
            else:
                # Use existing account
                print(f"✅ Found {len(account_list) if isinstance(account_list, list) else 1} existing account(s)")
                account_data = account_list[0] if isinstance(account_list, list) else account_list
                account_id = account_data["account_id"]
                username = account_data["username"]
                print(f"   Using account: {username}\n")
            
            # Get emails
            print(f"📧 Retrieving emails for {username}...")
            emails_result = await client.call_tool("list_emails", {
                "account_id": account_id,
                "folder": "inbox",
                "limit": 5,
                "include_body": True
            })
            
            # The result is in content[0].text as a JSON string
            emails_text = emails_result.content[0].text
            emails_data = json.loads(emails_text)
            
            # Check if it's wrapped in a structure or is the direct list
            if isinstance(emails_data, dict):
                # Might be wrapped - look for common keys
                if 'value' in emails_data:
                    emails = emails_data['value']
                elif '@odata.etag' in emails_data:
                    # Single email object, wrap it in a list
                    emails = [emails_data]
                else:
                    # Unknown structure, try to find the list
                    print(f"[DEBUG] Unexpected dict structure. Keys: {list(emails_data.keys())}")
                    emails = [emails_data]
            elif isinstance(emails_data, list):
                emails = emails_data
            else:
                raise ValueError(f"Unexpected data type: {type(emails_data)}")
            
            print(f"\n📬 Latest {len(emails)} emails:")
            for i, email in enumerate(emails, 1):
                print(f"\n  {i}. Subject: {email.get('subject', 'No subject')}")
                if 'from' in email and 'emailAddress' in email['from']:
                    print(f"     From: {email['from']['emailAddress']['address']}")
                print(f"     Date: {email.get('receivedDateTime', 'Unknown')}")
                print(f"     Read: {'Yes' if email.get('isRead', False) else 'No'}")
                if email.get('hasAttachments'):
                    print(f"     📎 Has attachments")
                
                # Show email body if available
                if 'body' in email and 'content' in email['body']:
                    body_content = email['body']['content']
                    # Truncate long bodies
                    if len(body_content) > 500:
                        body_content = body_content[:500] + "..."
                    print(f"\n     📄 Body:\n     {body_content}\n")
            
            print("\n✅ Done!")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


asyncio.run(main())