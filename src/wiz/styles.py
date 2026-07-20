from questionary import Style
from rich.console import Console

console = Console()

theme = Style([
    ('qmark', 'fg:#8B949E'),
    ('question', 'bold #C9D1D9'),
    ('pointer', 'fg:#56D4DD bold'),
    ('highlighted', 'fg:#56D4DD bold'),
    ('selected', 'fg:#8B949E dim'),
    ('text', 'fg:#C9D1D9'),
    ('instruction', 'fg:#8B949E dim'),
])

def print_line(content="", color="#8B949E"):
    if content:
        console.print(f"[{color}]│[/{color}]  {content}")
    else:
        console.print(f"[{color}]│[/{color}]")
