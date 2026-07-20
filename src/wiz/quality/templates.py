RUFF_CONFIG = """[lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # Pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "PL",  # Pylint rules implemented by Ruff
    "UP",  # pyupgrade
]
ignore = []

[lint.per-file-ignores]
"tests/*" = ["S101"]

[format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
line-ending = "auto"
"""

PYRIGHT_CONFIG = """{
  "include": [
    "src",
    "tests"
  ],
  "exclude": [
    "**/node_modules",
    "**/__pycache__"
  ],
  "pythonVersion": "3.10",
  "typeCheckingMode": "basic",
  "reportMissingImports": true,
  "reportMissingTypeStubs": false
}
"""

PRECOMMIT_CONFIG = """repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.3.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
"""

CUSTOM_AST_CHECKER = """import ast
import sys
from pathlib import Path

class ArchitectureChecker(ast.NodeVisitor):
    def __init__(self, filepath):
        self.filepath = filepath
        self.errors = []

    def visit_Import(self, node):
        for alias in node.names:
            if "database" in self.filepath.parts and "ui" in alias.name:
                self.errors.append(f"{self.filepath}:{node.lineno}: Database layer should not import UI modules ({alias.name})")
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module and "database" in self.filepath.parts and "ui" in node.module:
            self.errors.append(f"{self.filepath}:{node.lineno}: Database layer should not import UI modules ({node.module})")
        self.generic_visit(node)

def run_ast_checks(target_dir="src"):
    target_path = Path(target_dir)
    if not target_path.exists():
        return True

    errors = []
    for py_file in target_path.rglob("*.py"):
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
            checker = ArchitectureChecker(py_file)
            checker.visit(tree)
            errors.extend(checker.errors)
        except Exception as e:
            errors.append(f"Failed to parse {py_file}: {e}")

    if errors:
        print("[AST Checker] Architecture violations found:")
        for err in errors:
            print(f"  - {err}")
        return False

    print("[AST Checker] All custom architecture rules passed.")
    return True

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "src"
    success = run_ast_checks(target)
    sys.exit(0 if success else 1)
"""
