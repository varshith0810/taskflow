"""
TaskFlow Root Entrypoint.
Enables running the application directly from the root workspace directory:
    python main.py
"""
import os
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Change current working directory to backend so relative paths work uniformly
os.chdir(str(backend_dir))

import uvicorn

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "127.0.0.1")
    print(f"[*] Starting TaskFlow server at http://{host}:{port}")
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
