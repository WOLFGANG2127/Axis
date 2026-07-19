import os
import pytest
from dotenv import load_dotenv
from supabase import create_client

# Force load from .env and OVERRIDE any cached pytest variables
load_dotenv(override=True)

def test_supabase_connection_is_live():
    """Verify backend can authenticate and read from live Supabase."""
    raw_url = os.getenv("SUPABASE_URL")
    raw_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    assert raw_url is not None, "Missing SUPABASE_URL in environment"
    assert raw_key is not None, "Missing SUPABASE_SERVICE_ROLE_KEY in environment"
    
    # Strip any invisible spaces or quotes that might break DNS
    url = raw_url.strip().strip("'").strip('"')
    key = raw_key.strip().strip("'").strip('"')
    
    print(f"\n[DEBUG] Pytest is attempting to connect to: '{url}'")
    
    # Initialize client and test a read operation
    supabase = create_client(url, key)
    response = supabase.table("strategies").select("*").limit(1).execute()
    
    assert response is not None
    assert type(response.data) is list