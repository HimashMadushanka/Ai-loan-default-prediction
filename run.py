"""
Single-command launcher for AI Loan Default Prediction project.
Runs both the FastAPI backend and Streamlit frontend together,
automatically selecting .venv Python, freeing busy ports, and launching the browser UI.

Usage:
    python run.py
"""

import os
import sys
import time
import socket
import urllib.request
import subprocess
import webbrowser

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
API_HOST = "127.0.0.1"
API_PORT = 8000
STREAMLIT_PORT = 8501


def get_python_executable() -> str:
    """Detect and prefer virtual environment python if it exists."""
    if sys.platform == "win32":
        venv_py = os.path.join(PROJECT_ROOT, ".venv", "Scripts", "python.exe")
    else:
        venv_py = os.path.join(PROJECT_ROOT, ".venv", "bin", "python")

    if os.path.isfile(venv_py):
        return venv_py
    return sys.executable


def is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    """Check if a TCP port is currently open and accepting connections."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0


def kill_process_on_port(port: int):
    """Terminate any process listening on the given port (Windows & cross-platform)."""
    if not is_port_in_use(port):
        return

    print(f"🔄 Port {port} is occupied. Cleaning up stale process...")
    try:
        if sys.platform == "win32":
            cmd = f'powershell -Command "Get-NetTCPConnection -LocalPort {port} -ErrorAction SilentlyContinue | ForEach-Object {{ Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }}"'
            subprocess.run(cmd, shell=True, capture_output=True, timeout=5)
        else:
            cmd = f"fuser -k {port}/tcp"
            subprocess.run(cmd, shell=True, capture_output=True, timeout=5)
        time.sleep(1.0)
    except Exception as e:
        print(f"⚠️ Could not automatically free port {port}: {e}")


def wait_for_api(api_process: subprocess.Popen, timeout: float = 20.0) -> bool:
    """Wait until the FastAPI endpoint responds to HTTP requests."""
    start_time = time.time()
    url = f"http://{API_HOST}:{API_PORT}/docs"
    while time.time() - start_time < timeout:
        if api_process.poll() is not None:
            return False  # API process crashed
        try:
            with urllib.request.urlopen(url, timeout=1.0) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            pass
        time.sleep(0.5)
    return False


def wait_for_port(port: int, host: str = "127.0.0.1", timeout: float = 20.0) -> bool:
    """Wait until the port becomes active and accepts connections."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if is_port_in_use(port, host):
            return True
        time.sleep(0.5)
    return False


def main():
    print("=" * 60)
    print("  🚀 Starting AI Loan Default Prediction Ecosystem")
    print("=" * 60)

    # Automatically select the project's virtualenv Python
    py_executable = get_python_executable()
    if ".venv" in py_executable:
        print(f"📦 Using virtual environment: {py_executable}")
    else:
        print(f"⚠️ Using global Python: {py_executable}")

    # 0. Clean up stale processes holding ports
    kill_process_on_port(STREAMLIT_PORT)
    kill_process_on_port(API_PORT)

    # 1. Start FastAPI backend (uvicorn)
    print(f"\n📡 [1/2] Starting FastAPI Backend on http://{API_HOST}:{API_PORT} ...")
    api_cmd = [
        py_executable,
        "-m",
        "uvicorn",
        "api.main:app",
        "--host",
        API_HOST,
        "--port",
        str(API_PORT),
    ]

    api_process = subprocess.Popen(
        api_cmd,
        cwd=PROJECT_ROOT,
    )

    print("⏳ Waiting for API backend to initialize...")
    if wait_for_api(api_process):
        print("✅ FastAPI backend is live!")
    else:
        if api_process.poll() is not None:
            print("❌ Error: FastAPI process exited unexpectedly. Check requirements/dependencies.")
            return
        else:
            print("⚠️ API is taking longer than usual, proceeding to frontend...")

    # 2. Start Streamlit frontend
    print(f"\n🖥️  [2/2] Starting Streamlit Frontend on http://localhost:{STREAMLIT_PORT} ...")
    streamlit_cmd = [
        py_executable,
        "-m",
        "streamlit",
        "run",
        os.path.join("app", "app.py"),
        "--server.port",
        str(STREAMLIT_PORT),
        "--server.headless",
        "false",
    ]

    streamlit_process = None
    try:
        streamlit_process = subprocess.Popen(
            streamlit_cmd,
            cwd=PROJECT_ROOT,
        )

        # Wait for Streamlit to be accessible, then automatically open in browser
        if wait_for_port(STREAMLIT_PORT, timeout=15.0):
            print(f"\n✨ Application is ready! Opening in your browser...")
            webbrowser.open(f"http://localhost:{STREAMLIT_PORT}")
            print(f"👉 Frontend: http://localhost:{STREAMLIT_PORT}")
            print(f"👉 Backend API Docs: http://{API_HOST}:{API_PORT}/docs")
            print("\n(Press Ctrl+C in this terminal to stop both servers)\n")

        # Keep running until user stops
        streamlit_process.wait()

    except KeyboardInterrupt:
        print("\n🛑 Received stop signal. Shutting down...")
    finally:
        # Graceful cleanup
        if streamlit_process and streamlit_process.poll() is None:
            try:
                streamlit_process.terminate()
                streamlit_process.wait(timeout=2)
            except Exception:
                streamlit_process.kill()

        if api_process and api_process.poll() is None:
            print("🛑 Stopping FastAPI backend...")
            try:
                api_process.terminate()
                api_process.wait(timeout=2)
            except Exception:
                api_process.kill()

        print("👋 All services stopped cleanly.")


if __name__ == "__main__":
    main()
