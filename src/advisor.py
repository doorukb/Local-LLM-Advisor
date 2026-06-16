from __future__ import annotations
import sys
from collections.abc import Callable
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.constants import STATUS_FETCHING, STATUS_GENERATING
from src.fetch import fetch_all
from src.config import reset_config, schedule_bootstrap_venv_removal
from src.gemini import generate_report
from src.hardware import detect_hardware
from src.prompt import HardwareSnapshot, UserSelections, build_prompt

def run_pipeline(hardware: HardwareSnapshot, selections: UserSelections, on_status: Callable[[str], None] | None = None) -> str:
    if on_status is not None:
        on_status(STATUS_FETCHING)
    fetch_result = fetch_all()
    system_prompt, user_prompt = build_prompt(hardware, selections, fetch_result)
    if on_status is not None:
        on_status(STATUS_GENERATING)
    return generate_report(system_prompt, user_prompt)

# reset and exit the config and virtual environment when you want to start fresh
def reset_and_exit() -> None:
    config_deleted = reset_config()
    venv_scheduled = schedule_bootstrap_venv_removal()
    if config_deleted:
        print("Removed stored API key (config.json deleted).")
    else:
        print("No config.json found.")
    if venv_scheduled:
        print("Removed bootstrap virtual environment.")
    sys.exit(0)

def main() -> None:
    hardware = detect_hardware()
    from gui import run_gui

    def analyze(selections: UserSelections, on_status: Callable[[str], None] | None = None) -> str:
        return run_pipeline(hardware, selections, on_status=on_status)
    run_gui(analyze_callback=analyze)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        reset_and_exit()
    main()