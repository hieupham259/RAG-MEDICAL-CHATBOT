# main.py
import os
import sys
import time
import threading
import subprocess
import runpy
from dotenv import load_dotenv
from app.common.logger import get_logger
from app.common.custom_exception import CustomException

logger = get_logger(__name__)

load_dotenv()

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

def run_backend():
    try:
        logger.info("Starting backend server (uvicorn)...")
        # ensure using same python executable as this script
        cmd = [sys.executable, "-m", "uvicorn", "app.backend.api:app", "--host", "127.0.0.1", "--port", "9999"]
        subprocess.run(cmd, check=True, cwd=PROJECT_ROOT)
    except Exception as e:
        logger.exception("Backend server failed to start")
        raise CustomException("Backend server failed to start", error_detail=e)

def run_frontend_in_same_process():
    """
    Run Streamlit CLI inside this process (no separate python subprocess),
    after changing cwd to project root so imports like `from app...` work.
    This preserves the Python environment and sys.path behavior (sys.path[0] -> cwd).
    """
    try:
        logger.info("Starting frontend (Streamlit) in current process...")
        # set argv as if running: streamlit run run_ui.py
        run_ui_path = os.path.join(PROJECT_ROOT, "run_ui.py")
        sys.argv = ["streamlit", "run", run_ui_path]

        # run Streamlit CLI module in this process (blocks)
        # This avoids Streamlit spawning another python that might change import context.
        runpy.run_module("streamlit.web.cli", run_name="__main__")
    except Exception as e:
        logger.exception("Frontend failed to start in current process")
        raise CustomException("Frontend failed to start", error_detail=e)

if __name__ == "__main__":
    try:
        # change working directory to project root (do NOT touch sys.path)
        os.chdir(PROJECT_ROOT)
        logger.info("CWD set to project root: %s", PROJECT_ROOT)

        # start backend in a daemon thread (it will spawn uvicorn subprocess)
        backend_thread = threading.Thread(target=run_backend, daemon=True)
        backend_thread.start()

        # give backend a short moment to start
        time.sleep(2)

        # run frontend in the same process (this will block until Streamlit exits)
        run_frontend_in_same_process()
        # run_backend()
    except CustomException as e:
        logger.exception("CustomException occurred: %s", str(e))
    except KeyboardInterrupt:
        logger.info("Shutting down due to KeyboardInterrupt")
        # uvicorn subprocess will be terminated when main process exits (daemon thread)
