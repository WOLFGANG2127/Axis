import subprocess
import sys
from fastapi import FastAPI

app = FastAPI()

# FIX: Changed from direct path to module execution (-m) with dot notation
subprocess.Popen([sys.executable, "-m", "src.scheduling.no_trade_summary"])

@app.get("/")
def home():
    return {"status": "AXIS backend pipeline is actively executing in the background."}

@app.get("/api/health")
def health():
    return {"status": "ok"}