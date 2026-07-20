# 🪄 Wiz: Interactive TUI & Automation Engine for Python Environments

Wiz is a Python environment, package management, and code quality orchestration tool built on top of `uv`, `pip`, and `ruff`. It runs as an interactive TUI wizard when launched with no arguments, and as a set of scriptable, non-interactive subcommands when used in scripts, Makefiles, or CI/CD pipelines.

![Wiz Icon](assets/logo.png)

##  Key Features

* **Dual-Mode Interface:** Launches an interactive wizard with `wiz`, or runs non-interactively with subcommands (`wiz init`, `wiz quality`, `wiz install`, `wiz venv`, `wiz run`, `wiz list`) for scripting and CI.
* **Python Quality Platform Engine (`wiz quality`):** Orchestrates multi-phase quality checks in sequence—Phase 1 (Ruff lint/format/safe-fixes), Phase 2 (Pyright/Mypy type checking), Phase 3 (Custom AST architecture rules), and Phase 4 (Pylint deep static analysis).
* **Instant PEP 621 Config Generation:** `wiz init` creates a production-grade `pyproject.toml` following official PyPA standards. Use `--quality` to instantly generate `ruff.toml`, `pyrightconfig.json`, `.pre-commit-config.yaml`, and custom AST rules.
* **Persistent Global Configuration:** Settings (default engine, max history) live in `~/.wiz/wiz.json` and are read by both the wizard and CLI subcommands.
* **Global Run History:** Recently run scripts are stored in `~/.wiz/wiz_history`, shared across every project instead of tied to one directory.
* **Dual Engine Support:** Every install/freeze action can go through `uv` (fast) or `pip` (standard), per-command or as a saved default.
* **Package Validation:** Rejects attempts to install Python builtin modules before shelling out to pip.
* **Tested & CI''d:** Hermetic `pytest` suite runs on every push across Ubuntu, Windows, and macOS on Python 3.10–3.12.

##  Tech Stack

* **Language:** Python (3.8+)
* **CLI Parsing:** `argparse`
* **Interactive UI:** `questionary`, `rich`
* **Quality Engine:** `ruff`, `pyright` / `mypy`, Python `ast` parser, `pylint`
* **Storage:** JSON-based persistent configuration (`~/.wiz/wiz.json`)
* **Testing/CI:** `pytest`, GitHub Actions (cross-platform matrix)

---

##  Installation

Wiz can be installed directly from source using `pip` or `pipx`:

```bash
git clone [https://github.com/jayeshsharmaagnihotri/Wiz.git](https://github.com/jayeshsharmaagnihotri/Wiz.git)
cd Wiz
pip install -e .
