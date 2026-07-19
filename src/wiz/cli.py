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
    except FileNotFoundError:
        console.print("\n[bold red]✗ Error: 'uv' not found in PATH.[/bold red]")
    except subprocess.CalledProcessError as e:
        console.print(f"\n[bold red]✗ Failed ({e.returncode})[/bold red]\n[red]{e.stderr.strip()}[/red]")

def main():
    console.print("\n[bold magenta]◆ WIZ: UV MANAGER[/bold magenta]\n" + "─" * 40)
    while True:
        choice = questionary.select(
            "Select action:",
            choices=[
                "1. Initialize Virtual Env (uv venv)",
                "2. Install Package (uv pip install)",
                "3. Install Python Version (uv python install)",
                "4. Run Script Safely (uv run)",
                "5. List Python Versions (uv python list)",
                "Exit"
            ]
        ).ask()

        if choice == "Exit" or choice is None:
            break
        elif "1." in choice:
            ver = questionary.text("Python version (optional):").ask()
            run_uv(["venv", "--python", ver] if ver else ["venv"])
        elif "2." in choice:
            pkg = questionary.text("Package name:").ask()
            if pkg: run_uv(["pip", "install"] + pkg.split())
        elif "3." in choice:
            ver = questionary.text("Python version (e.g. 3.12):").ask()
            if ver: run_uv(["python", "install", ver])
        elif "4." in choice:
            scr = questionary.text("Script path (e.g. main.py):").ask()
            if scr: run_uv(["run", scr])
        elif "5." in choice:
            run_uv(["python", "list"])
        console.print("─" * 40)

if __name__ == "__main__":
    main()
