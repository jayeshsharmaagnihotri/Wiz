import os
import sys
import json
import re
import subprocess
from pathlib import Path

# Paths
CONFIG_DIR = Path.home() / ".wiz"
CONFIG_FILE = CONFIG_DIR / "wiz.json"
HISTORY_FILE = CONFIG_DIR / "wiz_history"

BUILTIN_MODULES = sys.builtin_module_names

DEFAULT_CONFIG = {
    "default_engine": "uv",
    "max_history": 5,
    "theme_color": "cyan"
}

def ensure_config_dir():
    """Ensures ~/.wiz directory exists"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def load_config():
    ensure_config_dir()
    if not CONFIG_FILE.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            config = DEFAULT_CONFIG.copy()
            config.update(data)
            return config
    except Exception:
        return DEFAULT_CONFIG.copy()

def save_config(config):
    ensure_config_dir()
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

def load_history():
    ensure_config_dir()
    if not HISTORY_FILE.exists():
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    except Exception:
        return []

def save_history(script, flags=""):
    ensure_config_dir()
    config = load_config()
    max_h = config.get("max_history", 5)
    
    entry = f"{script} {flags}".strip()
    history = load_history()
    
    if entry in history:
        history.remove(entry)
    history.insert(0, entry)
    
    history = history[:max_h]
    
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        for item in history:
            f.write(f"{item}\n")

def validate_package(package_name):
    clean_name = re.split(r'[<>=!~;]', package_name)[0].strip()
    if clean_name.lower() in BUILTIN_MODULES:
        print(f"Error: '{clean_name}' is a standard Python module.")
        return False
    return True

def run_pip_with_progress(cmd, target_action="action", engine_name="uv"):
    from wiz.styles import console
    
    status_label = f"Executing {target_action} via {engine_name.upper()}..."
    try:
        with console.status(f"[bold yellow]{status_label}[/bold yellow]"):
            result = subprocess.run(cmd, capture_output=True, text=True)
            
        if result.returncode == 0:
            console.print(f"\n[bold green]Success: {target_action} completed via [{engine_name.upper()}] engine![/bold green]")
            return True
        else:
            console.print(f"\n[bold red]Error during {target_action} ({engine_name.upper()}):[/bold red]")
            console.print(f"[red]{result.stderr.strip()}[/red]")
            return False
    except Exception as e:
        console.print(f"\n[bold red]Failed to run execution command: {e}[/bold red]")
        return False

def get_git_user_info():
    """Detects author name and email from git config if available"""
    name, email = "Developer", "developer@example.com"
    try:
        n = subprocess.run(["git", "config", "user.name"], capture_output=True, text=True)
        if n.returncode == 0 and n.stdout.strip():
            name = n.stdout.strip()
        e = subprocess.run(["git", "config", "user.email"], capture_output=True, text=True)
        if e.returncode == 0 and e.stdout.strip():
            email = e.stdout.strip()
    except Exception:
        pass
    return name, email

def init_project_config(target_dir="."):
    """Generates a PEP 621 & PEP 518 compliant pyproject.toml instantly"""
    from wiz.styles import console

    target_path = Path(target_dir).resolve()
    pyproject_file = target_path / "pyproject.toml"

    if pyproject_file.exists():
        console.print(f"[bold yellow]Notice: 'pyproject.toml' already exists in {target_path}. Skipping creation.[/bold yellow]")
        return False

    project_name = target_path.name.lower().replace(" ", "-").replace("_", "-")
    author_name, author_email = get_git_user_info()
    has_src = (target_path / "src").is_dir()

    toml_content = f'''[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "{project_name}"
version = "0.1.0"
description = "A production-grade Python package"
readme = "README.md"
requires-python = ">=3.8"
license = {{ text = "MIT" }}
authors = [
    {{ name = "{author_name}", email = "{author_email}" }}
]
keywords = ["python", "utility"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
dependencies = []

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "build>=1.0.0",
]

[project.scripts]
# {project_name} = "{project_name.replace('-', '_')}.cli:main"
'''

    if has_src:
        toml_content += '''
[tool.setuptools.packages.find]
where = ["src"]
'''

    try:
        with open(pyproject_file, "w", encoding="utf-8") as f:
            f.write(toml_content.strip() + "\n")
        console.print(f"[bold green]Success: Created PEP 621 compliant pyproject.toml in {target_path}[/bold green]")
        return True
    except Exception as e:
        console.print(f"[bold red]Failed to write pyproject.toml: {e}[/bold red]")
        return False
