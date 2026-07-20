import sys
import subprocess
from pathlib import Path
from wiz.styles import console
from wiz.quality.templates import RUFF_CONFIG, PYRIGHT_CONFIG, PRECOMMIT_CONFIG, CUSTOM_AST_CHECKER

def init_quality_configs(target_dir="."):
    """Generates standard configurations for Ruff, Pyright, Pre-Commit, and Custom AST checks."""
    target_path = Path(target_dir).resolve()
    
    ruff_file = target_path / "ruff.toml"
    pyright_file = target_path / "pyrightconfig.json"
    precommit_file = target_path / ".pre-commit-config.yaml"
    tools_dir = target_path / "tools" / "architecture"
    ast_checker_file = tools_dir / "check_architecture.py"

    if not ruff_file.exists():
        ruff_file.write_text(RUFF_CONFIG, encoding="utf-8")
        console.print("[green]Created ruff.toml[/green]")

    if not pyright_file.exists():
        pyright_file.write_text(PYRIGHT_CONFIG, encoding="utf-8")
        console.print("[green]Created pyrightconfig.json[/green]")

    if not precommit_file.exists():
        precommit_file.write_text(PRECOMMIT_CONFIG, encoding="utf-8")
        console.print("[green]Created .pre-commit-config.yaml[/green]")

    if not ast_checker_file.exists():
        tools_dir.mkdir(parents=True, exist_ok=True)
        ast_checker_file.write_text(CUSTOM_AST_CHECKER, encoding="utf-8")
        console.print("[green]Created tools/architecture/check_architecture.py[/green]")

    return True

def run_quality_pipeline(target_dir=".", fix=False, types_only=False, strict=False):
    """Executes the Python Quality Platform sequential pipeline."""
    target_path = Path(target_dir).resolve()

    if types_only:
        return _run_type_checks(target_path)

    # Phase 1: Ruff Formatting & Linting
    console.print("[bold yellow]Phase 1: Running Ruff (Lint & Format)...[/bold yellow]")
    ruff_cmd = ["uv", "run", "ruff", "check", str(target_path)]
    if fix:
        ruff_cmd.append("--fix")

    ruff_res = subprocess.run(ruff_cmd, capture_output=True, text=True)
    if ruff_res.returncode != 0:
        # Fallback to direct executable if uv run fails
        ruff_cmd[0:2] = ["ruff"]
        ruff_res = subprocess.run(ruff_cmd, capture_output=True, text=True)

    if ruff_res.returncode != 0:
        console.print("[red]Phase 1 Failed: Ruff lint issues found.[/red]")
        console.print(f"[red]{ruff_res.stdout or ruff_res.stderr}[/red]")
        return False
    console.print("[green]Phase 1 Passed: Ruff checks cleared.[/green]")

    # Phase 2: Type Analysis (Pyright or Mypy)
    type_passed = _run_type_checks(target_path)
    if not type_passed:
        return False

    # Phase 3: Custom AST Checks
    console.print("[bold yellow]Phase 3: Running Custom AST Architecture Rules...[/bold yellow]")
    ast_file = target_path / "tools" / "architecture" / "check_architecture.py"
    if ast_file.exists():
        ast_res = subprocess.run([sys.executable, str(ast_file), str(target_path / "src")], capture_output=True, text=True)
        if ast_res.returncode != 0:
            console.print("[red]Phase 3 Failed: AST architecture rules violated.[/red]")
            console.print(f"[red]{ast_res.stdout or ast_res.stderr}[/red]")
            return False
        console.print("[green]Phase 3 Passed: Custom AST rules cleared.[/green]")
    else:
        console.print("[yellow]Phase 3 Skipped: Custom AST checker not found (run 'wiz init --quality' to generate).[/yellow]")

    # Phase 4: Optional Deep Static Analysis (Pylint if strict)
    if strict:
        console.print("[bold yellow]Phase 4: Running Deep Static Analysis (Pylint)...[/bold yellow]")
        pylint_res = subprocess.run(["pylint", str(target_path / "src")], capture_output=True, text=True)
        if pylint_res.returncode != 0:
            console.print("[red]Phase 4 Failed: Pylint issues found.[/red]")
            console.print(f"[red]{pylint_res.stdout or pylint_res.stderr}[/red]")
            return False
        console.print("[green]Phase 4 Passed: Pylint checks cleared.[/green]")

    console.print("\n[bold green]Success: All quality gates passed successfully![/bold green]")
    return True

def _run_type_checks(target_path):
    console.print("[bold yellow]Phase 2: Running Type Analysis (Pyright/Mypy)...[/bold yellow]")
    type_cmd = ["pyright", str(target_path)]
    type_res = subprocess.run(type_cmd, capture_output=True, text=True)

    if type_res.returncode != 0:
        # Fallback to mypy
        type_cmd = ["mypy", str(target_path)]
        type_res = subprocess.run(type_cmd, capture_output=True, text=True)

    if type_res.returncode != 0:
        console.print("[red]Phase 2 Failed: Type analysis issues found.[/red]")
        console.print(f"[red]{type_res.stdout or type_res.stderr}[/red]")
        return False

    console.print("[green]Phase 2 Passed: Type analysis cleared.[/green]")
    return True
