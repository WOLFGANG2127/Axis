import os
import requests
import json

def fetch_strategies():
    supabase_url = "https://siutlouqtpzppavyvqoj.supabase.co"
    service_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNpdXRsb3VxdHB6cHBhdnl2cW9qIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MzA4MTY5MiwiZXhwIjoyMDk4NjU3NjkyfQ.tPGlP1lHLlkUFZ1cpkn9W7lv0pCYyyZfNZJiJ7LI0I8"
    
    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json"
    }
    
    # 1. Fetch exact rows to prove the data exists
    res = requests.get(f"{supabase_url}/rest/v1/strategies?select=*", headers=headers)
    print("=== DATA INTERROGATION (SERVICE ROLE) ===")
    print("Status Code:", res.status_code)
    try:
        data = res.json()
        print(json.dumps(data, indent=2))
    except Exception as e:
        print("Error parsing JSON:", e)
        print("Raw text:", res.text)
        
    # 2. Fetch using ANON key to prove RLS is blocking
    anon_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNpdXRsb3VxdHB6cHBhdnl2cW9qIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODMwODE2OTIsImV4cCI6MjA5ODY1NzY5Mn0.rVx2TR04SEwYVYipWRMaeWrW6SMaFUpUE39s0kFyJXc"
    headers_anon = {
        "apikey": anon_key,
        "Authorization": f"Bearer {anon_key}",
        "Content-Type": "application/json"
    }
    res_anon = requests.get(f"{supabase_url}/rest/v1/strategies?select=*", headers=headers_anon)
    print("\n=== DATA INTERROGATION (ANON ROLE - RLS TEST) ===")
    print("Status Code:", res_anon.status_code)
    print("Data:", res_anon.text)

if __name__ == "__main__":
    fetch_strategies()
