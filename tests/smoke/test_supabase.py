import os
import pytest
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables for local testing
load_dotenv()

def test_supabase_connection_is_live():
    """Verify backend can authenticate and read from live Supabase."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    assert url is not None, "Missing SUPABASE_URL in environment"
    assert key is not None, "Missing SUPABASE_SERVICE_ROLE_KEY in environment"
    
    # Initialize client and test a read operation
    supabase = create_client(url, key)
    response = supabase.table("strategies").select("*").limit(1).execute()
    
    # If the table doesn't exist or auth fails, this will throw an error.
    # If it passes, we have a guaranteed live connection.
    assert response is not None
    assert type(response.data) is list