# --------------------------------------
# 1. Locates the repository root.

# 2. Locates the NGINX executable.

# 3. Starts Uvicorn on 127.0.0.1:8000 using HTTP.

# 4. Tests the NGINX configuration.

# 5. Starts NGINX using the repository's nginx/nginx.conf.

# 6. Monitors both processes.

# 7. Shuts down both processes when the user stops the script.
# --------------------------------------

"""
Start the local FastAPI application behind NGINX.

Starts:
    1. Uvicorn on 127.0.0.1:8000 (HTTP only)
    2. NGINX on 127.0.0.1:80 and 127.0.0.1:443

NGINX is discovered through PATH by default.

An alternative executable location can be supplied through:
    - NGINX_BINARY environment variable
    - --nginx-executable command-line argument
"""

import argparse
import os
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path


# ============================================================
# PROJECT CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

NGINX_DIR = PROJECT_ROOT / "nginx"
NGINX_CONFIG = NGINX_DIR / "nginx.conf"
NGINX_LOG_DIR = NGINX_DIR / "logs"
NGINX_TEMP_DIR = NGINX_DIR / "temp"

CERT_FILE = PROJECT_ROOT / "certs" / "localhost.pem"
KEY_FILE = PROJECT_ROOT / "certs" / "localhost-key.pem"

UVICORN_HOST = "127.0.0.1"
UVICORN_PORT = 8000

# Keep this consistent with the ASGI application used by 'scripts/run_server.py'.
#
# The public GitHub version currently uses "app.main:app".
# If your local application uses app.main_file:app instead, change this value accordingly.
APP_IMPORT = "app.main:app"


# ============================================================
# NGINX EXECUTABLE DISCOVERY
# ============================================================

def find_nginx(explicit_path = None):

    # Priority 1: Explicit command-line argument.
    # Priority 2: NGINX_BINARY environment variable.
    # Priority 3: Operating system PATH.

    candidates = [
        explicit_path,
        os.environ.get("NGINX_BINARY"),
        os.environ.get("NGINX_HOME"),
    ]

    for candidate in candidates:

        if not candidate:
            continue

        path = Path(candidate).expanduser()

        # NGINX_HOME is a directory, whereas NGINX_BINARY is expected to be an executable.
        if path.is_dir():
            path = path / ("nginx.exe" if os.name == "nt" else "nginx")

        if path.is_file():
            return path.resolve()

    executable = shutil.which("nginx.exe" if os.name == "nt" else "nginx")

    if executable:
        return Path(executable).resolve()

    raise FileNotFoundError(
        "NGINX executable was not found.\n"
        "Check PATH, NGINX_HOME or NGINX_BINARY."
    )


# ============================================================
# NGINX COMMAND CONSTRUCTION
# ============================================================

def nginx_command(executable):

    # Use forward slashes for NGINX paths.
    # This also handles Windows paths containing spaces.

    # Set NGINX's prefix to the project's nginx/ directory.
    prefix = NGINX_DIR.as_posix().rstrip("/") + "/"

    # The configuration file is directly inside the prefix.
    config = "nginx.conf"

    return [
        str(executable),
        "-p", prefix,
        "-c", config,
    ]


# ============================================================
# PRE-FLIGHT CHECKS
# ============================================================

def check_port_available(host, port):

    try:
        with socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        ) as sock:

            sock.bind((host, port))

    except OSError as exc:
        raise RuntimeError(
            f"Port {port} is unavailable on {host}.\n"
            "Another application may already be using it, "
            "or you may lack permission to bind to it.\n"
            f"Details: {exc}"
        ) from exc


def wait_for_port(process, host, port, timeout = 20):

    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:

        if process.poll() is not None:
            raise RuntimeError(
                f"A server process exited unexpectedly "
                f"while waiting for port {port}."
            )

        try:
            with socket.create_connection(
                (host, port),
                timeout = 0.5
            ):
                return

        except OSError:
            time.sleep(0.25)

    raise TimeoutError(
        f"Server did not become available on "
        f"{host}:{port} within {timeout} seconds."
    )


def validate_configuration(executable):

    # Ensure all required project files exist.

    required_files = [
        NGINX_CONFIG,
        CERT_FILE,
        KEY_FILE,
    ]

    for file in required_files:
        if not file.is_file():
            raise FileNotFoundError(
                f"Required file not found: {file}"
            )

    NGINX_LOG_DIR.mkdir(
        parents = True,
        exist_ok = True
    )

    # Create NGINX temporary directories.
    # NGINX expects these directories to exist when validating its configuration on Windows.
    nginx_temp_directories = [
        "client_body_temp",
        "proxy_temp",
        "fastcgi_temp",
        "uwsgi_temp",
        "scgi_temp",
    ]

    for directory in nginx_temp_directories:
        (NGINX_TEMP_DIR / directory).mkdir(
            parents = True,
            exist_ok = True
        )

    print("\nTesting NGINX configuration...\n")

    command = nginx_command(executable)
    command.append("-t")

    result = subprocess.run(
        command,
        cwd = PROJECT_ROOT,
        check = False
    )

    if result.returncode != 0:
        raise RuntimeError(
            "NGINX configuration validation failed. "
            "Check nginx/logs/error.log."
        )

    print("\nNGINX configuration is valid.\n")


# ============================================================
# PROCESS SHUTDOWN
# ============================================================

def stop_nginx(executable, process):

    if process is None or process.poll() is not None:
        return

    print("\nStopping NGINX...\n")

    try:
        command = nginx_command(executable)
        command.extend(["-s", "quit"])

        subprocess.run(
            command,
            cwd = PROJECT_ROOT,
            check = False,
            timeout = 5
        )

        process.wait(timeout = 10)

    except (subprocess.TimeoutExpired, OSError):

        print("Graceful NGINX shutdown failed. "
              "Attempting process termination.")

        process.terminate()

        try:
            process.wait(timeout = 5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()

    print("\nNGINX stopped.")



def stop_uvicorn(process):

    if process is None:
        print("\nUvicorn was never started.")
        return

    # Check whether Uvicorn has already terminated.
    exit_code = process.poll()

    if exit_code is not None:
        print(
            f"\nUvicorn had already stopped "
            f"(exit code: {exit_code}).\n"
        )
        return

    print("\nStopping Uvicorn...")

    process.terminate()

    try:
        process.wait(timeout=10)

    except subprocess.TimeoutExpired:

        print("Uvicorn did not stop within 10 seconds.")
        print("Forcing termination...\n")

        process.kill()
        process.wait()

    print("\nUvicorn stopped.\n")


# ============================================================
# MAIN APPLICATION
# ============================================================

def main():

    print(f"Project root: {PROJECT_ROOT}")

    parser = argparse.ArgumentParser(
        description = "Run FastAPI behind a local NGINX reverse proxy."
    )

    parser.add_argument(
        "--nginx-executable",
        help = "Optional path to the NGINX executable."
    )

    args = parser.parse_args()

    uvicorn_process = None
    nginx_process = None
    nginx_executable = None

    return_code = 0

    try:

        # ----------------------------------------------------
        # 1. Locate NGINX
        # ----------------------------------------------------

        nginx_executable = find_nginx(
            args.nginx_executable
        )

        print(f"NGINX executable: {nginx_executable}")

        # ----------------------------------------------------
        # 2. Check whether required ports are available
        # ----------------------------------------------------

        for port in (80, 443, UVICORN_PORT):
            check_port_available("127.0.0.1", port)

        # ----------------------------------------------------
        # 3. Validate NGINX configuration and certificates
        # ----------------------------------------------------

        validate_configuration(nginx_executable)

        # ----------------------------------------------------
        # 4. Start Uvicorn (HTTP only)
        # ----------------------------------------------------

        print("\nStarting Uvicorn...\n")

        uvicorn_command = [
            sys.executable,
            "-m",
            "uvicorn",
            APP_IMPORT,
            "--host", UVICORN_HOST,
            "--port", str(UVICORN_PORT),
            "--proxy-headers",
            "--forwarded-allow-ips=127.0.0.1",
        ]

        uvicorn_process = subprocess.Popen(
            uvicorn_command,
            cwd = PROJECT_ROOT
        )

        wait_for_port(
            uvicorn_process,
            UVICORN_HOST,
            UVICORN_PORT
        )

        print("\nUvicorn is running.\n")

        # ----------------------------------------------------
        # 5. Start NGINX
        # ----------------------------------------------------

        print("\nStarting NGINX...")

        nginx_process = subprocess.Popen(
            nginx_command(nginx_executable),
            cwd = PROJECT_ROOT
        )

        wait_for_port(
            nginx_process,
            "127.0.0.1",
            443
        )

        print("\nNGINX is running.\n")

        # ----------------------------------------------------
        # 6. Display available URLs
        # ----------------------------------------------------

        print("\n" + "=" * 55)
        print("LOCAL DEVELOPMENT ENVIRONMENT IS RUNNING")
        print("=" * 55)

        print("\nHTTP  : http://localhost")
        print("HTTPS : https://localhost")
        print("DOCS  : https://localhost/docs")
        print("REDOC : https://localhost/redoc")

        print("\nUvicorn : 127.0.0.1:8000 (HTTP)")
        print("NGINX   : 127.0.0.1:80 and 127.0.0.1:443")

        print("\nPress CTRL+C to stop both servers.")
        print("=" * 55 + "\n")

        # ----------------------------------------------------
        # 7. Monitor both server processes
        # ----------------------------------------------------

        while True:

            if uvicorn_process.poll() is not None:
                raise RuntimeError(
                    "Uvicorn stopped unexpectedly."
                )

            if nginx_process.poll() is not None:
                raise RuntimeError(
                    "NGINX stopped unexpectedly."
                )

            time.sleep(0.5)

    except KeyboardInterrupt:

        print("\nShutdown requested by user.")
        return_code = 0

    except Exception as exc:

        print(f"\nERROR: {exc}")
        return_code = 1

    finally:

        # Stop NGINX first, then Uvicorn.
        # This prevents NGINX from forwarding requests to a backend that has already been stopped.

        if nginx_executable:
            stop_nginx(
                nginx_executable,
                nginx_process
            )

        stop_uvicorn(uvicorn_process)

    return return_code


if __name__ == "__main__":
    sys.exit(main())
