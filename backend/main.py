"""
TaskFlow Backend Entrypoint.
Enables running the backend server directly with:
    python main.py
"""
import os
import sys
from pathlib import Path

# Ensure the backend directory is in sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import uvicorn

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "127.0.0.1")
    print(f"[*] Starting TaskFlow backend at http://{host}:{port}")
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
