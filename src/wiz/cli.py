import os
import sys
import subprocess
import questionary
from rich.console import Console
from rich.table import Table

console = Console()
HISTORY_FILE = ".wiz_history"
MAX_HISTORY = 5

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except Exception:
        return []

def save_history(script_path, flags):
    try:
        entry = f"{script_path} {flags}".strip() if flags else script_path
        history = load_history()
        if entry in history:
            history.remove(entry)
        history.insert(0, entry)
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            for item in history[:MAX_HISTORY]:
                f.write(f"{item}\n")
    except Exception as e:
        console.print(f"[red]Warning: Could not save run history: {e}[/red]")

def run_cmd(cmd, use_status=True, status_msg="Running...", is_script=False):
    """Unified runner supporting both raw pip and uv commands cleanly"""
    try:
        if is_script and len(cmd) >= 3 and cmd[0] == "uv" and cmd[1] == "run" and cmd[2].endswith(".py"):
            target_script = cmd[2]
            script_flags = cmd[3:]
            if "__main__.py" in target_script or "cli.py" in target_script:
                console.print("[bold yellow]\nRefreshing Wiz interface session...[/bold yellow]\n")
                os.system('cls' if os.name == 'nt' else 'clear')
                return "RESTART"
            else:
                cmd = [sys.executable, target_script] + script_flags

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
    current_dir = os.getcwd()
    while True:
        try:
            items = os.listdir(current_dir)
        except Exception as e:
            console.print(f"[red]Error reading directory: {e}[/red]")
            return None

        choices = [".. (Up One Directory)"]
        dirs = [f for f in items if os.path.isdir(os.path.join(current_dir, f)) and not f.startswith(".")]
        files = [f for f in items if f.endswith(extension)]
        
        choices.extend([f"[Dir] {d}" for d in sorted(dirs)])
        choices.extend(sorted(files))
        choices.append("[Cancel Selection]")

        selected = questionary.select(
            f"Current Dir: {current_dir}\n{prompt_text}",
            choices=choices
        ).ask()

        if selected == "[Cancel Selection]" or selected is None:
            return None
        elif selected == ".. (Up One Directory)":
            current_dir = os.path.dirname(current_dir)
        elif selected.startswith("[Dir] "):
            current_dir = os.path.join(current_dir, selected.replace("[Dir] ", ""))
        else:
            return os.path.relpath(os.path.join(current_dir, selected))

def main():
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
                "Exit"
            ]
        ).ask()

        if choice == "Exit" or choice is None:
            break
            
        elif "Initialize Virtual Env" in choice:
            path = questionary.text("Target env directory path (Press enter for '.venv'):").ask()
            ver = questionary.text("Python version (optional, e.g. 3.12):").ask()
            cmd = ["uv", "venv"]
            if path.strip(): cmd.append(path.strip())
            if ver.strip(): cmd.extend(["--python", ver.strip()])
            
            if run_cmd(cmd, status_msg="Configuring virtual environment") == True:
                target_env = path.strip() if path.strip() else ".venv"
                console.print(f"\n[bold cyan]Environment ready! To activate in PowerShell run:[/bold cyan]")
                console.print(f"[yellow].\\{target_env}\\Scripts\\activate[/yellow]")

        elif "Run Script via Navigator" in choice:
            scr = browse_for_file(extension=".py", prompt_text="Select a python script to run:")
            if scr:
                flags = questionary.text("Append command flags (optional, e.g. --debug):").ask()
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
                choices=history + ["[Cancel]"]
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
            pkg = questionary.text("Enter package name(s) to install:").ask()
            if pkg:
                engine = questionary.select(
                    "Choose engine tool:",
                    choices=["1. Fast Mode (uv pip install)", "2. Standard Mode (pip install)"]
                ).ask()
                
                base_cmd = ["uv", "pip", "install"] if "Fast Mode" in engine else ["pip", "install"]
                run_cmd(base_cmd + pkg.split(), status_msg=f"Installing {pkg}")
            
        elif "Install from requirements.txt" in choice:
            req_file = browse_for_file(extension=".txt", prompt_text="Select your requirements file:")
            if req_file:
                engine = questionary.select(
                    "Choose engine tool:",
                    choices=["1. Fast Mode (uv pip install -r)", "2. Standard Mode (pip install -r)"]
                ).ask()
                
                base_cmd = ["uv", "pip", "install", "-r", req_file] if "Fast Mode" in engine else ["pip", "install", "-r", req_file]
                run_cmd(base_cmd, status_msg="Processing dependencies")

        elif "Freeze Environment Requirements" in choice:
            engine = questionary.select(
                "Choose freeze format:",
                choices=["1. Fast Compile (uv pip compile)", "2. Classic Freeze (pip freeze)"]
            ).ask()
            
            output_file = questionary.text("Output file name (Press enter for 'requirements.txt'):").ask()
            output_file = output_file.strip() if output_file.strip() else "requirements.txt"
            
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
            
        console.print("-" * 55)

if __name__ == "__main__":
    main()
