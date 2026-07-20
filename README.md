# 🪄 Wiz: Interactive TUI & Automation Engine for Python Environments

Wiz is a Python environment and package management tool built on top of `uv` and `pip`. It runs as an interactive TUI wizard when launched with no arguments, and as a set of scriptable, non-interactive subcommands when used in scripts, Makefiles, or CI.

![Wiz Icon](assets/logo.png)

## 🚀 Key Features

* **Dual-Mode Interface:** Launches an interactive wizard with `wiz`, or runs non-interactively with subcommands (`wiz install`, `wiz venv`, `wiz run`, `wiz list`) for scripting and CI.
* **Persistent Global Configuration:** Settings (default engine, max history) live in `~/.wiz/wiz.json` and are read by both the wizard and CLI subcommands.
* **Global Run History:** Recently run scripts are stored in `~/.wiz/wiz_history`, shared across every project instead of tied to one directory.
* **Dual Engine Support:** Every install/freeze action can go through `uv` (fast) or `pip` (standard), per-command or as a saved default.
* **Package Validation:** Rejects attempts to install Python builtin modules before shelling out to pip.
* **Tested & CI'd:** Hermetic `pytest` suite runs on every push across Ubuntu, Windows, and macOS on Python 3.10–3.12.

## 🛠 Tech Stack

* **Language:** Python (3.8+)
* **CLI Parsing:** `argparse`
* **Interactive UI:** `questionary`, `rich`
* **Storage:** JSON-based persistent configuration (`~/.wiz/wiz.json`)
* **Testing/CI:** `pytest`, GitHub Actions (cross-platform matrix)

## 📂 Project Structure

```text
Wiz/
├── .github/
│   └── workflows/
│       └── ci.yml       # Cross-platform test matrix
├── assets/               # Branding and visual assets
├── src/
│   └── wiz/
│       ├── __init__.py
│       ├── __main__.py  # python -m wiz entry point
│       ├── cli.py       # argparse setup, interactive loop, command handling
│       ├── styles.py     # rich/questionary theming
│       └── utils.py      # config, history, validation, pip execution
├── tests/
│   └── test_cli.py       # Hermetic unit tests
├── wiz.json               # Sample/reference config (not the runtime one)
├── pyproject.toml         # Project metadata and dependencies
└── .gitignore             # Git tracking exclusions
```
