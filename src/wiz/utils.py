import os
import sys
import json
import subprocess
import time
from pathlib import Path
from wiz.styles import console, print_line

CONFIG_DIR = Path.home() / ".wiz"
CONFIG_FILE = CONFIG_DIR / "wiz.json"
HISTORY_FILE = CONFIG_DIR / "wiz_history"

BUILTIN_MODULES = set(sys.builtin_module_names) | {
    "time", "os", "sys", "math", "random", "json", "re", "datetime",
    "collections", "itertools", "functools", "pathlib", "shutil", "ssl",
    "urllib", "subprocess", "csv", "hashlib", "logging", "pickle"
}

def ensure_config_dir():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def load_config():
    ensure_config_dir()
    default_config = {
        "default_engine": "uv",
        "max_history": 5,
        "theme_color": "cyan"
    }
    if not CONFIG_FILE.exists():
        save_config(default_config)
        return default_config
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return {**default_config, **json.load(f)}
    except Exception:
        return default_config

def save_config(config_data):
    ensure_config_dir()
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4)
    except Exception as e:
        console.print(f"[red]Warning: Could not save configuration: {e}[/red]")

def load_history():
    ensure_config_dir()
    if not HISTORY_FILE.exists():
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except Exception:
        return []

def save_history(script_path, flags):
    ensure_config_dir()
    config = load_config()
    max_history = config.get("max_history", 5)
    try:
        entry = f"{script_path} {flags}".strip() if flags else script_path
        history = load_history()
        if entry in history:
            history.remove(entry)
        history.insert(0, entry)
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            for item in history[:max_history]:
                f.write(f"{item}\n")
    except Exception as e:
        console.print(f"[red]Warning: Could not save run history: {e}[/red]")

def validate_package(package_name):
    if not package_name:
        return False
    pkg_clean = package_name.strip().split("==")[0].split(">=")[0].split("<=")[0]
    if pkg_clean.lower() in BUILTIN_MODULES:
        print_line("[bold #F85149]STATUS: FAILED[/bold #F85149]")
        print_line(f"[#F85149]Error: '{pkg_clean}' is a built-in Python standard library module.[/#F85149]")
        return False
    return True

def run_pip_with_progress(args, target_action="install", engine_name="uv"):
    full_cmd = args
    engine_label = "Fast Engine (uv)" if engine_name == "uv" else "Standard Engine (pip)"
    
    with console.status(f"[#8B949E]│[/#8B949E] [bold #C9D1D9][{engine_label}] Resolving index & dependencies...[/bold #C9D1D9]", spinner="simpleDotsScrolling"):
        time.sleep(0.2)

    with console.status(f"[#8B949E]│[/#8B949E] [bold #C9D1D9][{engine_label}] Executing {target_action}...[/bold #C9D1D9]", spinner="simpleDotsScrolling"):
        result = subprocess.run(full_cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print_line(f"[bold #3FB950]STATUS: SUCCESS[/bold #3FB950] - Finished {target_action} using {engine_label}.")
        if result.stdout.strip():
            for line in result.stdout.strip().split('\n'):
                if not line.lower().startswith("notice:"):
                    print_line(f"[#8B949E]{line}[/#8B949E]")
        return True
    else:
        print_line(f"[bold #F85149]STATUS: FAILED ({engine_label})[/bold #F85149]")
        for line in result.stderr.strip().split('\n'):
            print_line(f"[#F85149]{line}[/#F85149]")
        return False
