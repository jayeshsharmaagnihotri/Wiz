# 🪄 Wiz: Modern Python Package Wizard

Wiz is a lightweight, high-performance CLI tool designed to streamline your development workflow. It automates tedious configuration tasks, allowing you to focus on writing high-quality code.

![Wiz Icon](assets/logo.png)

## 🚀 Key Features

* **Project Automation:** Rapidly initialize and structure new project environments.
* **Persistent Configuration:** Uses an integrated `wiz.json` for reliable settings management.
* **Intuitive CLI:** Built for speed with a clean, user-friendly interface.
* **Lightweight:** Minimal dependencies, optimized for local development.

## 🛠 Tech Stack

* **Language:** Python
* **Storage:** JSON-based persistent configuration
* **Interface:** Command Line Interface (CLI)

## 📂 Project Structure

```text
Wiz/
├── assets/          # Branding and visual assets
├── src/
│   ├── wiz/         # Core application logic
│   │   ├── cli.py   # Command handling
│   │   └── utils.py # Helper functions
│   └── __init__.py
├── wiz.json         # Local configuration file
├── pyproject.toml   # Project metadata and dependencies
└── .gitignore       # Git tracking exclusions
