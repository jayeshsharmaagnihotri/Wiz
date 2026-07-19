import os
import subprocess
import questionary
from rich.console import Console

console = Console()

def run_uv(args):
    try:
        cmd = ["uv"] + args
        with console.status(f"[bold yellow]Wiz running: {' '.join(cmd)}...[/bold yellow]"):
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        console.print("\n[bold green]✓ Success[/bold green]")
        if result.stdout:
            console.print(result.stdout.strip())
        return True
    except FileNotFoundError:
        console.print("\n[bold red]✗ Error: 'uv' not found in PATH.[/bold red]")
        return False
    except subprocess.CalledProcessError as e:
        console.print(f"\n[bold red]✗ Failed ({e.returncode})[/bold red]\n[red]{e.stderr.strip()}[/red]")
        return False

def browse_for_file():
    """Terminal file navigator that lets users select a Python file from the current directory."""
    current_dir = os.getcwd()
    while True:
        try:
            items = os.listdir(current_dir)
        except Exception as e:
            console.print(f"[red]Error reading directory: {e}[/red]")
            return None

        # Filter to directories and .py files for cleaner navigation
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
    console.print("\n[bold magenta]◆ WIZ: ADVANCED UV DRIVER[/bold magenta]\n" + "─" * 40)
    while True:
        choice = questionary.select(
            "Select action:",
            choices=[
                "1. Initialize Virtual Env (uv venv)",
                "2. Install Package (uv pip install)",
                "3. Install Python Version (uv python install)",
                "4. Run Script via Navigator (uv run)",
                "5. List Python Versions (uv python list)",
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
            
            if run_uv(args):
                # Print explicit shell instructions to easily activate the environment
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
                console.print(f"[green]Executing selected file: {scr}[/green]")
                run_uv(["run", scr])
                
        elif "5." in choice:
            run_uv(["python", "list"])
            
        console.print("─" * 40)

if __name__ == "__main__":
    main()
