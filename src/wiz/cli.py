import os
import sys
import subprocess
import questionary
from rich.console import Console

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

def run_uv(args, is_script=False):
    try:
        cmd = ["uv"] + args
        if is_script and len(args) >= 2 and args[0] == "run" and args[1].endswith(".py"):
            target_script = args[1]
            script_flags = args[2:]
            
            if "__main__.py" in target_script or "cli.py" in target_script:
                console.print("[bold yellow]\nRefreshing Wiz interface session...[/bold yellow]\n")
                # Clear screen cleanly and return a specific indicator instead of pulling the process out from under the shell
                os.system('cls' if os.name == 'nt' else 'clear')
                return "RESTART"
            else:
                cmd = [sys.executable, target_script] + script_flags

        if is_script:
            subprocess.run(cmd, check=True)
        else:
            with console.status(f"[bold yellow]Wiz running: {' '.join(cmd)}...[/bold yellow]"):
                subprocess.run(cmd, check=True)
        return True
    except FileNotFoundError:
        console.print("\n[bold red]✗ Error: Process execution failed. Component not found.[/bold red]")
        return False
    except subprocess.CalledProcessError as e:
        console.print(f"\n[bold red]✗ Failed ({e.returncode})[/bold red]")
        return False

def browse_for_file():
    current_dir = os.getcwd()
    while True:
        try:
            items = os.listdir(current_dir)
        except Exception as e:
            console.print(f"[red]Error reading directory: {e}[/red]")
            return None

        choices = [".. (Up One Directory)"]
        dirs = [f for f in items if os.path.isdir(os.path.join(current_dir, f)) and not f.startswith(".")]
        pys = [f for f in items if f.endswith(".py")]
        
        choices.extend([f"[Dir] {d}" for d in sorted(dirs)])
        choices.extend(sorted(pys))
        choices.append("[Cancel Selection]")

        selected = questionary.select(
            f"Current Dir: {current_dir}\nSelect a file to run:",
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
        console.print("\n[bold magenta]* WIZ: ADVANCED UV DRIVER[/bold magenta]\n" + "-" * 40)
        choice = questionary.select(
            "Select action:",
            choices=[
                "1. Initialize Virtual Env (uv venv)",
                "2. Install Package (uv pip install)",
                "3. Install Python Version (uv python install)",
                "4. Run Script via Navigator (uv run)",
                "5. Re-run Recent Script (History)",
                "6. List Python Versions (uv python list)",
                "Exit"
            ]
        ).ask()

        if choice == "Exit" or choice is None:
            break
            
        elif "1." in choice:
            path = questionary.text("Target directory path (Press enter for default '.venv'):").ask()
            ver = questionary.text("Python version (optional, e.g. 3.12):").ask()
            
            args = ["venv"]
            if path.strip(): args.append(path.strip())
            if ver.strip(): args.extend(["--python", ver.strip()])
            
            if run_uv(args) == True:
                target_env = path.strip() if path.strip() else ".venv"
                console.print(f"\n[bold cyan]💡 To activate this environment in PowerShell run:[/bold cyan]")
                console.print(f"[yellow].\\{target_env}\\Scripts\\activate[/yellow]")

        elif "2." in choice:
            pkg = questionary.text("Package name:").ask()
            if pkg: run_uv(["pip", "install"] + pkg.split())
            
        elif "3." in choice:
            ver = questionary.text("Python version (e.g. 3.12):").ask()
            if ver: run_uv(["python", "install", ver])
            
        elif "4." in choice:
            scr = browse_for_file()
            if scr:
                flags = questionary.text("Append command flags (optional, e.g. --debug -v):").ask()
                flags = flags.strip() if flags else ""
                
                save_history(scr, flags)
                
                console.print(f"[green]Executing selected file: {scr} {flags}[/green]")
                args = ["run", scr]
                if flags:
                    args.extend(flags.split())
                
                status = run_uv(args, is_script=True)
                if status == "RESTART":
                    continue
                
        elif "5." in choice:
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
                
                console.print(f"[green]Re-executing from history: {scr} {flags}[/green]")
                args = ["run", scr]
                if flags:
                    args.extend(flags.split())
                
                status = run_uv(args, is_script=True)
                if status == "RESTART":
                    continue

        elif "6." in choice:
            run_uv(["python", "list"])
            
        console.print("-" * 40)

if __name__ == "__main__":
    main()
