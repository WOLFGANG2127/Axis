import os
import requests

def test_anon_access():
    supabase_url = "https://siutlouqtpzppavyvqoj.supabase.co"
    anon_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNpdXRsb3VxdHB6cHBhdnl2cW9qIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODMwODE2OTIsImV4cCI6MjA5ODY1NzY5Mn0.rVx2TR04SEwYVYipWRMaeWrW6SMaFUpUE39s0kFyJXc"
    
    headers = {
        "apikey": anon_key,
        "Authorization": f"Bearer {anon_key}",
        "Content-Type": "application/json"
    }
    
    res = requests.get(f"{supabase_url}/rest/v1/strategies?select=*", headers=headers)
    print("Status Code:", res.status_code)
    print("Response:", res.text)

if __name__ == "__main__":
    test_anon_access()
