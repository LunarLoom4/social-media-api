import argparse
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CERT_DIR = PROJECT_ROOT / "certs"

parser = argparse.ArgumentParser(description = "Run the FastAPI development server.")
parser.add_argument("mode", choices = ["http", "https"], help = "Server protocol")
args = parser.parse_args()

command = [
    sys.executable, "-m", "uvicorn",
    "app.main:app",
    "--reload",
    "--host", "127.0.0.1",
    "--port", "8000",
]

if args.mode == "https":
    cert = CERT_DIR / "localhost.pem"
    key = CERT_DIR / "localhost-key.pem"

    if not cert.is_file() or not key.is_file():
        parser.error(
            "Local certificates not found. Generate them using mkcert first."
        )

    command.extend([
        "--ssl-certfile", str(cert),
        "--ssl-keyfile", str(key),
    ])

subprocess.run(command, cwd=PROJECT_ROOT)
