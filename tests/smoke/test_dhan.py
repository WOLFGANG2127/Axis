import os
from dotenv import load_dotenv

from dhanhq import DhanContext
from dhanhq import dhanhq

load_dotenv()

client_id = os.getenv("DHAN_CLIENT_ID")
access_token = os.getenv("DHAN_ACCESS_TOKEN")

if not client_id:
    raise ValueError("DHAN_CLIENT_ID missing")

if not access_token:
    raise ValueError("DHAN_ACCESS_TOKEN missing")

print("✅ Client ID Loaded")
print("✅ Access Token Loaded")

try:
    dhan_context = DhanContext(client_id, access_token)

    dhan = dhanhq(dhan_context)

    print("\n✅ DhanContext Created Successfully")
    print("✅ SDK Initialized")

except Exception as e:
    print("\n❌ Initialization Failed")
    print(e)