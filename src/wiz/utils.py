import sys
import subprocess
import time
from wiz.styles import console, print_line

BUILTIN_MODULES = set(sys.builtin_module_names) | {
    "time", "os", "sys", "math", "random", "json", "re", "datetime", 
    "collections", "itertools", "functools", "pathlib", "shutil", "ssl",
    "urllib", "subprocess", "csv", "hashlib", "logging", "pickle"
}

def get_close_matches(word, possibilities):
    matches = []
    word = word.lower()
    for p in possibilities:
        p_low = p.lower()
        if p_low.startswith(word) or word.startswith(p_low):
            matches.append(p)
    return matches

def validate_package(package_name):
    if not package_name: 
        return False
    if package_name.lower() in BUILTIN_MODULES:
        print_line("[bold #F85149]STATUS: FAILED[/bold #F85149]")
        print_line(f"[#F85149]Error: '{package_name}' is a core system standard module.[/#F85149]")
        return False
    return True

def run_pip_with_progress(args, target_action):
    full_cmd = [sys.executable, "-m", "pip"] + args
    
    with console.status("[#8B949E]│[/#8B949E]  [bold #C9D1D9]Connecting to index servers...[/bold #C9D1D9]", spinner="simpleDotsScrolling"):
        time.sleep(0.4)
        
    with console.status(f"[#8B949E]│[/#8B949E]  [bold #C9D1D9]{target_action.capitalize()}ing packages...[/bold #C9D1D9]", spinner="simpleDotsScrolling"):
        result = subprocess.run(full_cmd, capture_output=True, text=True)
        
    if result.returncode == 0:
        print_line(f"[bold #3FB950]STATUS: SUCCESS[/bold #3FB950] - Finished {target_action} routine.")
        if result.stdout.strip():
            for line in result.stdout.strip().split('\n'):
                if not line.lower().startswith("notice:"):
                    print_line(f"[#8B949E]{line}[/#8B949E]")
    else:
        print_line("[bold #F85149]STATUS: FAILED[/bold #F85149]")
        for line in result.stderr.strip().split('\n'):
            print_line(f"[#F85149]{line}[/#F85149]")
