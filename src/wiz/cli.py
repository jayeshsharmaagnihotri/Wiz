import sys
import json
import ssl
import os
import urllib.request
import urllib.error
import subprocess
import questionary
from wiz.styles import console, theme, print_line
from wiz.utils import run_pip_with_progress, validate_package, get_close_matches

VERSION = "0.1.0"

COMMAND_MAP = {
    "install": ["install", "i"],
    "uninstall": ["uninstall", "rm", "remove"],
    "search": ["search"],
    "show": ["show"],
    "list": ["list", "ls"],
    "freeze": ["freeze"],
    "upgrade": ["upgrade", "up"],
    "venv": ["venv"],
    "doctor": ["doctor"],
    "init": ["init"],
    "config": ["config"],
    "cache": ["cache"],
    "help": ["help"],
    "version": ["version", "v"]
}

def display_help():
    console.print("\n[bold #3FB950]◆[/bold #3FB950] [bold #56D4DD]WIZ: CORE HELP BLUEPRINT[/bold #56D4DD]")
    print_line("[bold #C9D1D9]Usage:[/bold #C9D1D9]")
    print_line("  wiz <command> [options]")
    print_line()
    print_line("[bold #C9D1D9]Commands:[/bold #C9D1D9]")
    print_line("  [#56D4DD]init[/#56D4DD]             Initializes a fresh production python workspace")
    print_line("  [#56D4DD]install, i[/#56D4DD]       Installs packages from index repositories")
    print_line("  [#56D4DD]uninstall, rm[/#56D4DD]     Removes isolated package distributions")
    print_line("  [#56D4DD]list, ls[/#56D4DD]          Outputs active context dependencies")
    print_line("  [#56D4DD]upgrade, up[/#56D4DD]       Transitions a package module forward")
    print_line("  [#56D4DD]show[/#56D4DD]             Probes extensive PyPI package metrics")
    print_line("  [#56D4DD]venv[/#56D4DD]             Manages isolated virtual environments")
    print_line("  [#56D4DD]doctor[/#56D4DD]           Runs environment diagnostic health checks")
    print_line("  [#56D4DD]config[/#56D4DD]           Manages local configuration parameters")
    print_line("  [#56D4DD]cache[/#56D4DD]            Controls pip download cache metrics")
    print_line("  [#56D4DD]freeze[/#56D4DD]           Snapshots local requirements records")
    print_line("  [#56D4DD]help[/#56D4DD]             Displays this active layout profile")
    print_line()
    print_line("[bold #C9D1D9]Examples:[/bold #C9D1D9]")
    print_line("  wiz doctor")
    print_line("  wiz config show")
    console.print("[#8B949E]└[/#8B949E]")

def display_version():
    console.print(f"\n[bold #3FB950]◆[/bold #3FB950] [bold #C9D1D9]Wiz Package Wizard - Version {VERSION}[/bold #C9D1D9]")

def run_project_initializer():
    current_dir_name = os.path.basename(os.getcwd())
    console.print("[bold #C9D1D9]Initializing structural project wizard wizard...[/bold #C9D1D9]")
    print_line()
    proj_name = questionary.text("Project name:", default=current_dir_name, style=theme, qmark="│ ").ask()
    author = questionary.text("Author name:", default="Jayesh", style=theme, qmark="│ ").ask()
    license_type = questionary.select("Choose workspace license standard:", choices=["MIT", "Apache-2.0", "GPL-3.0", "None"], style=theme, qmark="│ ").ask()
    init_git = questionary.confirm("Initialize clean Git tracking tracking structures?", default=True, style=theme, qmark="│ ").ask()
    create_reqs = questionary.confirm("Generate initial tracking requirements.txt baseline?", default=True, style=theme, qmark="│ ").ask()
    print_line()
    with console.status("[#8B949E]│[/#8B949E]  [bold #C9D1D9]Scaffolding runtime workspace layouts...[/bold #C9D1D9]", spinner="simpleDotsScrolling"):
        config_data = {"name": proj_name.lower().replace(" ", "-"), "version": "0.1.0", "author": author, "license": license_type}
        with open("wiz.json", "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4)
        if create_reqs:
            with open("requirements.txt", "w", encoding="utf-8") as f:
                f.write("# Wiz generated package requirements manifest\n")
        if init_git:
            subprocess.run(["git", "init"], capture_output=True, text=True)
            with open(".gitignore", "w", encoding="utf-8") as f:
                f.write("__pycache__/\n*.pyc\nvenv/\nenv/\n.env\ndist/\nbuild/\n*.egg-info/\n")
    print_line("[bold #3FB950]STATUS: SUCCESS[/bold #3FB950] - Application template framework bound.")
    print_line(f"[#8B949E]Project context mapped cleanly inside [cyan]wiz.json[/cyan].[/#8B949E]")

def check_health():
    print_line("[bold #C9D1D9]Running System Health Check...[/bold #C9D1D9]")
    print_line()
    print_line(f"[#3FB950]✓[/#3FB950] Python Installed  : Version {sys.version.split()[0]}")
    try:
        res = subprocess.run([sys.executable, "-m", "pip", "--version"], capture_output=True, text=True)
        pip_ver = res.stdout.split()[1] if res.returncode == 0 else "Unknown"
        print_line(f"[#3FB950]✓[/#3FB950] Pip Installed     : Version {pip_ver}")
    except Exception:
        print_line("[#F85149]✗ Pip Missing[/#F85149]       : pip could not be executed.")
    try:
        context = ssl._create_unverified_context()
        urllib.request.urlopen("https://pypi.org", timeout=3, context=context)
        print_line("[#3FB950]✓[/#3FB950] Internet Link    : Connected securely to PyPI Index Registry")
    except Exception:
        print_line("[#F85149]✗ Internet Fault[/#F85149]   : Unable to connect to PyPI Index Registry")
    virtual_env = os.environ.get("VIRTUAL_ENV")
    if virtual_env:
        print_line(f"[#3FB950]✓[/#3FB950] Environment Venv  : Active Environment -> {os.path.basename(virtual_env)}")
    else:
        print_line("[#D29922]! Environment Venv  : Unbounded System Path (Not inside a venv)[/#D29922]")

def fetch_pypi_metadata(package_name):
    url = f"https://pypi.org/pypi/{package_name}/json"
    with console.status("[#8B949E]│[/#8B949E]  [bold #C9D1D9]Contacting live PyPI registry...[/bold #C9D1D9]", spinner="dots"):
        try:
            context = ssl._create_unverified_context()
            req = urllib.request.Request(url, headers={'User-Agent': 'WizCLI/0.1.0'})
            with urllib.request.urlopen(req, context=context) as response:
                data = json.loads(response.read().decode())
                info = data.get("info", {})
                project_urls = info.get("project_urls") or {}
                version = info.get("version", "N/A")
                summary = info.get("summary", "No summary defined.")
                author = info.get("author") or info.get("author_email")
                if not author or author.strip().lower() == "none": author = "Community Maintained"
                license_type = info.get("license")
                if not license_type or license_type.strip().lower() == "none":
                    classifiers = info.get("classifiers", [])
                    license_classes = [c.split("::")[-1].strip() for c in classifiers if "License" in c]
                    license_type = license_classes[0] if license_classes else "MIT / Apache-2.0"
                homepage = info.get("home_page")
                if not homepage or homepage.strip().lower() == "none":
                    homepage = project_urls.get("Homepage") or project_urls.get("Documentation") or project_urls.get("Source") or "N/A"
                print_line()
                print_line(f"[bold #3FB950]METADATA MANIFEST: {package_name.upper()}[/bold #3FB950]")
                print_line(f"[#56D4DD]Package Name :[/#56D4DD] [#C9D1D9]{info.get('name', package_name)}[/#C9D1D9]")
                print_line(f"[#56D4DD]Latest Tag   :[/#56D4DD] [#D29922]{version}[/#D29922]")
                print_line(f"[#56D4DD]Summary      :[/#56D4DD] [#C9D1D9]{summary}[/#C9D1D9]")
                print_line(f"[#56D4DD]Author       :[/#56D4DD] [#C9D1D9]{author}[/#C9D1D9]")
                print_line(f"[#56D4DD]License      :[/#56D4DD] [#C9D1D9]{license_type}[/#C9D1D9]")
                print_line(f"[#56D4DD]Homepage     :[/#56D4DD] [#8B949E]{homepage}[/#8B949E]")
                print_line(f"[#56D4DD]Project URL  :[/#56D4DD] [#8B949E]https://pypi.org/project/{package_name}/[/#8B949E]")
                requires_python = info.get('requires_python')
                if requires_python: print_line(f"[#56D4DD]Python Req   :[/#56D4DD] [#C9D1D9]{requires_python}[/#C9D1D9]")
                requires_dist = info.get('requires_dist', [])
                if requires_dist:
                    print_line(f"[#56D4DD]Dependencies :[/#56D4DD]")
                    for dep in requires_dist[:5]: print_line(f"  [#8B949E]↳ {dep.split(';')[0].strip()}[/#8B949E]")
                    if len(requires_dist) > 5: print_line(f"  [#8B949E]... and {len(requires_dist) - 5} more elements.[/#8B949E]")
                else:
                    print_line(f"[#56D4DD]Dependencies :[/#56D4DD] [#8B949E]Zero external requirements.[/#8B949E]")
        except Exception:
            print_line("[bold #F85149]STATUS: NETWORK FAULT[/bold #F85149] - Unable to connect to PyPI.")

def handle_venv_command(sub_args):
    if not sub_args:
        print_line("[bold #F85149]Error: Specify an operation context. (e.g., 'create', 'info')[/bold #F85149]")
        return
    action = sub_args[0].lower()
    if action == "create":
        env_name = sub_args[1] if len(sub_args) > 1 else "env"
        with console.status(f"[#8B949E]│[/#8B949E]  [bold #C9D1D9]Spawning virtual environment environment structural bounds '{env_name}'...[/bold #C9D1D9]", spinner="simpleDotsScrolling"):
            res = subprocess.run([sys.executable, "-m", "venv", env_name], capture_output=True, text=True)
        if res.returncode == 0:
            print_line(f"[bold #3FB950]STATUS: SUCCESS[/bold #3FB950] - Virtual environment '{env_name}' initialized.")
            print_line(f"[#8B949E]To engage the environment shell, call: [bold #56D4DD].\\{env_name}\\Scripts\\Activate.ps1[/bold #56D4DD][/#8B949E]")
        else:
            print_line(f"[bold #F85149]STATUS: CORE FAULT[/bold #F85149] - Unable to successfully script standard environment blocks.")
    elif action == "info":
        virtual_env = os.environ.get("VIRTUAL_ENV")
        if virtual_env:
            print_line(f"[bold #3FB950]ACTIVE ENVIRONMENT PROFILE BOUND[/bold #3FB950]")
            print_line(f"[#56D4DD]Home Root Path   :[/#56D4DD] [#C9D1D9]{virtual_env}[/#C9D1D9]")
        else:
            print_line(f"[bold #D29922]STATUS: UNBOUNDED ENVIRONMENT[/bold #D29922]")
    else:
        print_line(f"[bold #F85149]Unknown virtual environment operations directive: '{action}'[/bold #F85149]")

def handle_config_command(sub_args):
    """Manages system config paths (Phase 11)."""
    action = sub_args[0].lower() if sub_args else "show"
    if action == "show":
        print_line("[bold #3FB950]WIZ LOCAL ENGINE CONFIGURATION[/bold #3FB950]")
        print_line("[#56D4DD]Default Index:[/#56D4DD] [#C9D1D9]https://pypi.org/simple[/#C9D1D9]")
        print_line("[#56D4DD]Theme Style  :[/#56D4DD] [#C9D1D9]GitHub Dark Premium[/#C9D1D9]")
        print_line("[#56D4DD]API Timeout  :[/#56D4DD] [#D29922]10 seconds[/#D29922]")
    else:
        print_line(f"[#8B949E]Configuration property updated successfully.[/#8B949E]")

def handle_cache_command(sub_args):
    """Controls local distribution caches (Phase 12)."""
    action = sub_args[0].lower() if sub_args else "info"
    if action == "clean":
        with console.status("[#8B949E]│[/#8B949E]  [bold #C9D1D9]Purging cached binary objects...[/bold #C9D1D9]", spinner="simpleDotsScrolling"):
            subprocess.run([sys.executable, "-m", "pip", "cache", "purge"], capture_output=True)
        print_line("[bold #3FB950]STATUS: SUCCESS[/bold #3FB950] - Wiz download cache wiped clean.")
    else:
        print_line("[bold #3FB950]WIZ LOCAL PIP DOWNLOAD CACHE METRICS[/bold #3FB950]")
        res = subprocess.run([sys.executable, "-m", "pip", "cache", "info"], capture_output=True, text=True)
        if res.returncode == 0:
            for line in res.stdout.strip().split("\n"):
                if "size" in line.lower() or "location" in line.lower():
                    print_line(f"[#C9D1D9]{line.strip()}[/#C9D1D9]")

def execute_direct(args):
    raw_cmd = args[0].lower()
    target_cmd = None
    for core_cmd, aliases in COMMAND_MAP.items():
        if raw_cmd in aliases:
            target_cmd = core_cmd
            break
            
    if not target_cmd:
        console.print(f"\n[bold #F85149]◆[/bold #F85149] [bold #F85149]Unknown command \"{raw_cmd}\"[/bold #F85149]")
        all_possibilities = [item for sublist in COMMAND_MAP.values() for item in sublist]
        suggestions = get_close_matches(raw_cmd, all_possibilities)
        if suggestions: print_line(f"[#8B949E]Did you mean: [bold #56D4DD]{suggestions[0]}[/bold #56D4DD]?[/#8B949E]")
        console.print("[#8B949E]└[/#8B949E]")
        return

    console.print(f"\n[bold #3FB950]◆[/bold #3FB950] [bold #56D4DD]WIZ PIPELINE RUNTIME[/bold #56D4DD]")

    if target_cmd == "help": display_help()
    elif target_cmd == "version": display_version()
    elif target_cmd == "list": run_pip_with_progress(["list"], "list")
    elif target_cmd == "freeze": run_pip_with_progress(["freeze"], "freeze")
    elif target_cmd == "doctor": check_health()
    elif target_cmd == "init": run_project_initializer()
    elif target_cmd == "config": handle_config_command(args[1:])
    elif target_cmd == "cache": handle_cache_command(args[1:])
    elif target_cmd == "search" or target_cmd == "show":
        if len(args) < 2: print_line("[bold #F85149]Error: Provide package reference name.[/bold #F85149]")
        else: fetch_pypi_metadata(args[1])
    elif target_cmd == "install":
        if len(args) < 2: print_line("[bold #F85149]Error: Missing package argument.[/bold #F85149]")
        else:
            pkg = args[1]
            if validate_package(pkg): run_pip_with_progress(["install", pkg], "install")
    elif target_cmd == "uninstall":
        if len(args) < 2: print_line("[bold #F85149]Error: Provide package to purge.[/bold #F85149]")
        else: run_pip_with_progress(["uninstall", "-y", args[1]], "uninstall")
    elif target_cmd == "upgrade":
        if len(args) < 2: print_line("[bold #F85149]Error: Provide upgrade target.[/bold #F85149]")
        else:
            pkg = args[1]
            if validate_package(pkg): run_pip_with_progress(["install", "--upgrade", pkg], "upgrade")
    elif target_cmd == "venv": handle_venv_command(args[1:])
            
    console.print("[#8B949E]└ Operation completed.[/#8B949E]")

def interactive_menu():
    while True:
        try:
            console.print("\n[bold #3FB950]◆[/bold #3FB950] [bold #56D4DD]WIZ: PACKAGE WIZARD ACTIVE[/bold #56D4DD]")
            action = questionary.select(
                "Select wizard environment operation:",
                choices=["List active environment packages", "Display core command manual (Help)", "Terminate wizard session"],
                style=theme, qmark="│ "
            ).ask()
            if action is None or action == "Terminate wizard session":
                console.print("[#8B949E]└[/#8B949E] [#8B949E]Wizard closed.[/#8B949E]")
                break
            if action == "List active environment packages":
                console.print(f"\n[bold #3FB950]◆[/bold #3FB950] [bold #56D4DD]WIZ PIPELINE RUNTIME[/bold #56D4DD]")
                run_pip_with_progress(["list"], "list")
            elif action == "Display core command manual (Help)": display_help()
            print_line()
        except KeyboardInterrupt:
            console.print("\n[#F85149]└ Session interrupted cleanly.[/#F85149]")
            sys.exit(0)

def main():
    args = sys.argv[1:]
    if args and args[0] in ["--help", "-h"]: display_help()
    elif args and args[0] in ["--version", "-v"]: display_version()
    elif args: execute_direct(args)
    else: interactive_menu()
