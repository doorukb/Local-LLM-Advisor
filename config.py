from __future__ import annotations
import json
import os
from pathlib import Path

GEMINI_API_KEY_ENV = "GEMINI_API_KEY"
_PROJECT_DIR = Path(__file__).resolve().parent
DEFAULT_CONFIG_PATH = _PROJECT_DIR / "config.json"

# raised when no gemini api key is available from env or config.json
class GeminiApiKeyNotFoundError(Exception):
    pass

# read the api key from the config file
def _read_config_api_key(config_path: Path) -> str | None:
    if not config_path.is_file():
        return None
    raw = config_path.read_text(encoding="utf-8").strip()
    if not raw:
        return None
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    api_key = data.get("api_key")
    if api_key and str(api_key).strip():
        return str(api_key).strip()
    return None

def has_api_key(config_path: Path = DEFAULT_CONFIG_PATH) -> bool:
    env_key = os.environ.get(GEMINI_API_KEY_ENV)
    if env_key and env_key.strip():
        return True
    return _read_config_api_key(config_path) is not None

def load_api_key(config_path: Path = DEFAULT_CONFIG_PATH) -> str:
    env_key = os.environ.get(GEMINI_API_KEY_ENV)
    if env_key and env_key.strip():
        return env_key.strip()
    stored = _read_config_api_key(config_path)
    if stored is not None:
        return stored
    raise GeminiApiKeyNotFoundError("No Gemini API key found. Set GEMINI_API_KEY or add api_key to config.json.")

def save_api_key(api_key: str, config_path: Path = DEFAULT_CONFIG_PATH) -> None:
    key = api_key.strip()
    if not key:
        raise ValueError("API key cannot be empty.")
    config_path.write_text(json.dumps({"api_key": key}, indent=2) + "\n", encoding="utf-8")