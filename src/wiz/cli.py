import os
import sys
import subprocess
from pathlib import Path
import questionary

from wiz.styles import console, theme, print_line
from wiz.utils import (
    load_history, save_history, load_config, save_config,
    validate_package, run_pip_with_progress
)

def run_cmd(cmd, use_status=True, status_msg="Running...", is_script=False):
    """Unified runner supporting both raw pip and uv commands cleanly"""
    try:
        if is_script and len(cmd) >= 3:
            target_path = Path(cmd[2]).resolve()
            cli_path = Path(__file__).resolve()
            main_path = (cli_path.parent / "__main__.py").resolve()

            if target_path in (cli_path, main_path):
                console.print("[bold yellow]\nRefreshing Wiz interface session...[/bold yellow]\n")
                os.system('cls' if os.name == 'nt' else 'clear')
                return "RESTART"

        if not use_status:
            subprocess.run(cmd, check=True)
        else:
            with console.status(f"[bold yellow]{status_msg} ({' '.join(cmd)})...[/bold yellow]"):
                subprocess.run(cmd, check=True)
        return True
    except FileNotFoundError:
        console.print(f"\n[bold red]Error: Component '{cmd[0]}' not found in system PATH.[/bold red]")
        return False
    except subprocess.CalledProcessError as e:
        console.print(f"\n[bold red]Process returned failure code ({e.returncode})[/bold red]")
        return False

def browse_for_file(extension=".py", prompt_text="Select a file:"):
    current_dir = Path.cwd().resolve()
    while True:
        try:
            items = list(current_dir.iterdir())
        except Exception as e:
            console.print(f"[red]Error reading directory: {e}[/red]")
            return None

        choices = []
        is_root = current_dir.parent == current_dir
        if not is_root:
            choices.append(".. (Up One Directory)")

        dirs = [d.name for d in items if d.is_dir() and not d.name.startswith(".")]
        files = [f.name for f in items if f.is_file() and f.name.endswith(extension)]
        
        choices.extend([f"[Dir] {d}" for d in sorted(dirs)])
        choices.extend(sorted(files))
        choices.append("[Cancel Selection]")

        selected = questionary.select(
            f"Current Dir: {current_dir}\n{prompt_text}",
            choices=choices,
            style=theme
        ).ask()

        if selected == "[Cancel Selection]" or selected is None:
            return None
        elif selected == ".. (Up One Directory)":
            current_dir = current_dir.parent
        elif selected.startswith("[Dir] "):
            current_dir = current_dir / selected.replace("[Dir] ", "")
        else:
            selected_file = current_dir / selected
            try:
                return str(selected_file.relative_to(Path.cwd()))
            except ValueError:
                return str(selected_file)

def main():
    config = load_config()

    while True:
        console.print("\n[bold magenta]* WIZ: UNIFIED ENVIRONMENT ENGINE (UV & PIP)[/bold magenta]\n" + "-" * 55)
        choice = questionary.select(
            "Select action category:",
            choices=[
                "[UV] Initialize Virtual Env (uv venv)",
                "[UV] Run Script via Navigator (uv run)",
                "[UV] Re-run Recent Script (History)",
                "[PIP] Install Package (uv pip install / pip)",
                "[PIP] Install from requirements.txt",
                "[PIP] Freeze Environment Requirements",
                "[System] List Python Versions (uv python list)",
                "[Config] Manage Wiz Settings",
                "Exit"
            ],
            style=theme
        ).ask()

        if choice == "Exit" or choice is None:
            break
            
        elif "Initialize Virtual Env" in choice:
            path = questionary.text("Target env directory path (Press enter for '.venv'):", style=theme).ask()
            ver = questionary.text("Python version (optional, e.g. 3.12):", style=theme).ask()
            cmd = ["uv", "venv"]
            if path and path.strip(): cmd.append(path.strip())
            if ver and ver.strip(): cmd.extend(["--python", ver.strip()])
            
            if run_cmd(cmd, status_msg="Configuring virtual environment") == True:
                target_env = path.strip() if (path and path.strip()) else ".venv"
                console.print(f"\n[bold cyan]Environment ready! To activate in PowerShell run:[/bold cyan]")
                console.print(f"[yellow].\\{target_env}\\Scripts\\activate[/yellow]")

        elif "Run Script via Navigator" in choice:
            scr = browse_for_file(extension=".py", prompt_text="Select a python script to run:")
            if scr:
                flags = questionary.text("Append command flags (optional, e.g. --debug):", style=theme).ask()
                flags = flags.strip() if flags else ""
                save_history(scr, flags)
                
                console.print(f"[green]Executing script: {scr} {flags}[/green]")
                cmd = ["uv", "run", scr]
                if flags: cmd.extend(flags.split())
                
                if run_cmd(cmd, use_status=False, is_script=True) == "RESTART":
                    continue
                
        elif "Re-run Recent Script" in choice:
            history = load_history()
            if not history:
                console.print("[yellow]No recent script execution history found.[/yellow]")
                continue
                
            selected_history = questionary.select(
                "Select a recent run to re-execute:",
                choices=history + ["[Cancel]"],
                style=theme
            ).ask()
            
            if selected_history and selected_history != "[Cancel]":
                parts = selected_history.split(" ")
                scr = parts[0]
                flags = " ".join(parts[1:]) if len(parts) > 1 else ""
                save_history(scr, flags)
                
                console.print(f"[green]Re-executing: {scr} {flags}[/green]")
                cmd = ["uv", "run", scr]
                if flags: cmd.extend(flags.split())
                
                if run_cmd(cmd, use_status=False, is_script=True) == "RESTART":
                    continue

        elif "Install Package" in choice:
            pkg_input = questionary.text("Enter package name(s) to install:", style=theme).ask()
            if pkg_input:
                packages = pkg_input.split()
                valid_packages = [p for p in packages if validate_package(p)]
                if not valid_packages:
                    continue

                engine = questionary.select(
                    "Choose engine tool:",
                    choices=["1. Fast Mode (uv pip install)", "2. Standard Mode (pip install)"],
                    style=theme
                ).ask()
                
                base_cmd = ["uv", "pip", "install"] if "Fast Mode" in engine else ["pip", "install"]
                run_pip_with_progress(base_cmd + valid_packages, target_action="install")
            
        elif "Install from requirements.txt" in choice:
            req_file = browse_for_file(extension=".txt", prompt_text="Select your requirements file:")
            if req_file:
                engine = questionary.select(
                    "Choose engine tool:",
                    choices=["1. Fast Mode (uv pip install -r)", "2. Standard Mode (pip install -r)"],
                    style=theme
                ).ask()
                
                base_cmd = ["uv", "pip", "install", "-r", req_file] if "Fast Mode" in engine else ["pip", "install", "-r", req_file]
                run_pip_with_progress(base_cmd, target_action="requirements installation")

        elif "Freeze Environment Requirements" in choice:
            engine = questionary.select(
                "Choose freeze format:",
                choices=["1. Fast Compile (uv pip compile)", "2. Classic Freeze (pip freeze)"],
                style=theme
            ).ask()
            
            output_file = questionary.text("Output file name (Press enter for 'requirements.txt'):", style=theme).ask()
            output_file = output_file.strip() if (output_file and output_file.strip()) else "requirements.txt"
            
            if "Fast Compile" in engine:
                cmd = ["uv", "pip", "compile", "pyproject.toml", "-o", output_file] if os.path.exists("pyproject.toml") else ["uv", "pip", "freeze"]
            else:
                cmd = ["pip", "freeze"]
                
            try:
                with console.status("[bold yellow]Compiling environment state...[/bold yellow]"):
                    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                    
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(result.stdout)
                console.print(f"[bold green]Successfully generated locks inside: {output_file}[/bold green]")
            except Exception as e:
                console.print(f"[bold red]Failed to export freeze schema: {e}[/bold red]")

        elif "List Python Versions" in choice:
            run_cmd(["uv", "python", "list"], status_msg="Gathering engine runtimes")

        elif "Manage Wiz Settings" in choice:
            opt = questionary.select(
                "Select setting to update:",
                choices=[
                    f"Default Engine (Current: {config.get('default_engine', 'uv')})",
                    f"Max History Entries (Current: {config.get('max_history', 5)})",
                    "[Back]"
                ],
                style=theme
            ).ask()
            
            if opt and "[Back]" not in opt:
                if "Default Engine" in opt:
                    new_engine = questionary.select("Select default engine:", choices=["uv", "pip"], style=theme).ask()
                    if new_engine: config["default_engine"] = new_engine
                elif "Max History Entries" in opt:
                    new_max = questionary.text("Enter max history count (1-20):", style=theme).ask()
                    if new_max and new_max.isdigit(): config["max_history"] = int(new_max)
                save_config(config)
                console.print("[bold green]Settings updated successfully![/bold green]")

        console.print("-" * 55)

if __name__ == "__main__":
    main()
