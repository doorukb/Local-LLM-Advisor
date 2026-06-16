#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/doorukb/Local-LLM-Advisor.git"
DEFAULT_BRANCH="main"
PYTHON_DOWNLOAD_URL="https://www.python.org/downloads/"

WORK_DIR=""
BOOTSTRAP_REMOTE=""

die() {
  echo "Error: $*" >&2
  exit 1
}

cleanup_work_dir() {
  if [[ -n "$WORK_DIR" && -d "$WORK_DIR" ]]; then
    rm -rf "$WORK_DIR"
  fi
}

resolve_script_dir() {
  local source_path="${BASH_SOURCE[0]}"

  if [[ -n "$source_path" && -f "$source_path" ]]; then
    cd "$(dirname "$source_path")"
    SCRIPT_DIR="$(pwd)"
    BOOTSTRAP_REMOTE=""
    return 0
  fi

  if ! command -v git >/dev/null 2>&1; then
    die "git is required for remote bootstrap (curl | bash). Install git or clone the repository and run ./launch.sh instead."
  fi

  WORK_DIR="$(mktemp -d)" || die "Failed to create a temporary work directory."
  trap cleanup_work_dir EXIT

  local branch="${LLM_ADVISOR_BRANCH:-$DEFAULT_BRANCH}"
  if ! git clone --depth 1 --branch "$branch" "$REPO_URL" "$WORK_DIR"; then
    die "Failed to clone $REPO_URL (branch: $branch). Check your network connection and branch name."
  fi

  SCRIPT_DIR="$WORK_DIR"
  BOOTSTRAP_REMOTE=1
}

find_python() {
  local cmd version_output

  for cmd in python3 python; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
      continue
    fi

    if "$cmd" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' >/dev/null 2>&1; then
      PYTHON="$cmd"
      return 0
    fi

    version_output="$("$cmd" -c 'import sys; print(".".join(map(str, sys.version_info[:3])))' 2>/dev/null || true)"
    if [[ -n "$version_output" ]]; then
      die "Python 3.9 or later is required; found $cmd version $version_output. Install Python from $PYTHON_DOWNLOAD_URL"
    fi
  done

  die "Python 3.9 or later was not found on your system. Install Python from $PYTHON_DOWNLOAD_URL"
}

resolve_script_dir

REQUIREMENTS_FILE="$SCRIPT_DIR/requirements.txt"
ADVISOR_FILE="$SCRIPT_DIR/src/advisor.py"

[[ -f "$REQUIREMENTS_FILE" ]] || die "Missing requirements file: $REQUIREMENTS_FILE"
[[ -f "$ADVISOR_FILE" ]] || die "Missing advisor entrypoint: $ADVISOR_FILE"

find_python

VENV_DIR="$(mktemp -d "${TMPDIR:-/tmp}/llm-advisor-venv.XXXXXX")" || die "Failed to create a temporary virtual environment directory."
if ! "$PYTHON" -m venv "$VENV_DIR"; then
  die "Failed to create virtual environment. On Debian/Ubuntu, install the python3-venv package and try again."
fi

VENV_PYTHON="$VENV_DIR/bin/python"
if ! "$VENV_PYTHON" -m pip install -r "$REQUIREMENTS_FILE"; then
  die "Failed to install dependencies from $REQUIREMENTS_FILE"
fi

# LLM_ADVISOR_VENV_DIR is read by src/advisor.py --reset to remove this bootstrap venv
export LLM_ADVISOR_VENV_DIR="$VENV_DIR"

if [[ -n "$BOOTSTRAP_REMOTE" ]]; then
  CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/local-llm-advisor"
  mkdir -p "$CONFIG_DIR"
  export LLM_ADVISOR_CONFIG_PATH="$CONFIG_DIR/config.json"
fi

# WORK_DIR (the git clone) is removed by trap cleanup_work_dir EXIT; VENV_DIR is intentionally not trapped so --reset can remove it later
exec "$VENV_PYTHON" "$ADVISOR_FILE" "$@"