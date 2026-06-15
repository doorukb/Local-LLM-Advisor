from __future__ import annotations
from collections.abc import Callable
from fetch import fetch_all
from config import GeminiApiKeyNotFoundError
from gemini import generate_report
from hardware import detect_hardware
from prompt import HardwareSnapshot, UserSelections, build_prompt

STATUS_FETCHING = "Fetching current model data..."
STATUS_GENERATING = "Generating report..."

def run_pipeline(hardware: HardwareSnapshot, selections: UserSelections, on_status: Callable[[str], None] | None = None) -> str:
    try:
        if on_status is not None:
            on_status(STATUS_FETCHING)
        fetch_result = fetch_all()
        system_prompt, user_prompt = build_prompt(hardware, selections, fetch_result)
        if on_status is not None:
            on_status(STATUS_GENERATING)
        return generate_report(system_prompt, user_prompt)
    except GeminiApiKeyNotFoundError as exc:
        return str(exc)

def main() -> None:
    hardware = detect_hardware()
    from gui import run_gui

    def analyze(selections: UserSelections, on_status: Callable[[str], None] | None = None) -> str:
        return run_pipeline(hardware, selections, on_status=on_status)
    run_gui(analyze_callback=analyze)

if __name__ == "__main__":
    main()