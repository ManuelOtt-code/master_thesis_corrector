"""Convenience script to run the Streamlit UI."""
import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    ui_path = Path(__file__).parent / "ui" / "app.py"
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(ui_path)])











