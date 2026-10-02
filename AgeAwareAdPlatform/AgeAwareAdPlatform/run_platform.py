import sys
import os
import subprocess
import argparse
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def run_backend(port: int = 8000):
    print(f"[SafeAd Platform] Starting FastAPI Backend on http://127.0.0.1:{port}...")
    backend_main = BASE_DIR / "backend" / "app" / "main.py"
    cmd = [sys.executable, "-m", "uvicorn", "backend.app.main:app", "--host", "127.0.0.1", "--port", str(port)]
    return subprocess.Popen(cmd, cwd=str(BASE_DIR))

def run_frontend(port: int = 8501):
    print(f"[SafeAd Platform] Starting Multi-Portal Web Application on http://127.0.0.1:{port}...")
    frontend_app = BASE_DIR / "frontend" / "app.py"
    cmd = [sys.executable, "-m", "streamlit", "run", str(frontend_app), "--server.port", str(port), "--server.headless", "true"]
    return subprocess.Popen(cmd, cwd=str(BASE_DIR))

def run_tests():
    print("[SafeAd Platform] Executing Platform Test Suite...")
    test_script = BASE_DIR / "tests" / "test_suite.py"
    cmd = [sys.executable, str(test_script)]
    res = subprocess.run(cmd, cwd=str(BASE_DIR))
    sys.exit(res.returncode)

def main():
    parser = argparse.ArgumentParser(description="Age-Aware Advertisement Platform Launcher")
    parser.add_argument("--backend-only", action="store_true", help="Launch FastAPI backend only")
    parser.add_argument("--frontend-only", action="store_true", help="Launch Streamlit frontend only")
    parser.add_argument("--test", action="store_true", help="Execute complete automated test suite")
    parser.add_argument("--backend-port", type=int, default=8000, help="Backend port")
    parser.add_argument("--frontend-port", type=int, default=8501, help="Frontend port")
    
    args = parser.parse_args()

    if args.test:
        run_tests()
        return

    procs = []
    try:
        if args.backend_only:
            p = run_backend(args.backend_port)
            procs.append(p)
            p.wait()
        elif args.frontend_only:
            p = run_frontend(args.frontend_port)
            procs.append(p)
            p.wait()
        else:
            p_back = run_backend(args.backend_port)
            procs.append(p_back)
            time.sleep(2)  # Give backend 2s to initialize
            p_front = run_frontend(args.frontend_port)
            procs.append(p_front)
            print("\n=================================================================")
            print("[SafeAd Platform] Age-Aware Advertisement Moderation & Delivery Platform Online!")
            print(f"Backend REST API:  http://127.0.0.1:{args.backend_port}")
            print(f"Web Portals:       http://127.0.0.1:{args.frontend_port}")
            print("=================================================================\n")
            print("Press Ctrl+C to stop all platform servers.\n")
            p_front.wait()
    except KeyboardInterrupt:
        print("\n[SafeAd Platform] Shutting down all processes...")
    finally:
        for p in procs:
            try:
                p.terminate()
            except Exception:
                pass

if __name__ == "__main__":
    main()
