import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(
    host=os.environ.get("DB_HOST"),
    port=os.environ.get("DB_PORT"),
    user=os.environ.get("DB_USERNAME"),
    password=os.environ.get("DB_PASSWORD"),
    dbname=os.environ.get("DB_NAME")
)
cur = conn.cursor()

try:
    cur.execute("SELECT * FROM cron.job")
    jobs = cur.fetchall()
    print("=== cron.job ===")
    for row in jobs:
        print(row)
except Exception as e:
    print("cron.job query failed:", e)

try:
    cur.execute("SELECT * FROM cron.job_run_details ORDER BY start_time DESC LIMIT 30")
    runs = cur.fetchall()
    print("=== cron.job_run_details ===")
    for row in runs:
        print(row)
except Exception as e:
    print("cron.job_run_details query failed:", e)

conn.close()
