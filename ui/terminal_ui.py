"""
Layra Terminal UI
===========================
Rich terminal interface with animated banners, status indicators,
and color-coded output for the ultimate Layra experience.
"""

import logging
import os
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.markdown import Markdown
from rich import box

console = Console()

# Logo path
LOGO_PATH = Path(__file__).parent.parent / "assets" / "layra_logo.jpg"


# ============================================
# Layra ASCII Banner
# ============================================

LAYRA_BANNER = """
[bold cyan]
██╗      █████╗ ██╗   ██╗██████╗  █████╗ 
██║     ██╔══██╗╚██╗ ██╔╝██╔══██╗██╔══██╗
██║     ███████║ ╚████╔╝ ██████╔╝███████║
██║     ██╔══██║  ╚██╔╝  ██╔══██╗██╔══██║
███████╗██║  ██║   ██║   ██║  ██║██║  ██║
╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝
[/bold cyan]
[dim]Layra — Your Legendary Yielding Responsive AI[/dim]
[dim yellow]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/dim yellow]
"""

STARTUP_MESSAGE = """[bold green]✓[/bold green] System Online
[bold green]✓[/bold green] Voice Pipeline Ready
[bold green]✓[/bold green] AI Brain Connected
[bold green]✓[/bold green] Skills Loaded
[bold green]✓[/bold green] All Systems Operational"""


class TerminalUI:
    """Rich terminal interface for Layra"""

    def __init__(self):
        self.console = console

    def show_banner(self):
        """Display the startup banner with logo."""
        self.console.clear()
        # Try to display logo image
        self._show_logo()
        self.console.print(LAYRA_BANNER)
        self.console.print(
            Panel(
                STARTUP_MESSAGE,
                title="[bold cyan]System Status[/bold cyan]",
                border_style="cyan",
                box=box.DOUBLE_EDGE,
                padding=(1, 2),
            )
        )
        self.console.print()

    def _show_logo(self):
        """Display Layra logo image in terminal using climage."""
        try:
            import climage
            if LOGO_PATH.exists():
                # Get terminal width for sizing
                term_width = os.get_terminal_size().columns
                logo_width = min(40, term_width // 2)
                output = climage.convert(str(LOGO_PATH), width=logo_width, is_unicode=True)
                # Center the logo
                lines = output.split('\n')
                pad = ' ' * ((term_width - logo_width * 2) // 2)
                for line in lines:
                    print(pad + line)
        except Exception:
            pass  # Silently fall back to text banner only

    def show_listening(self):
        """Show that Layra is listening."""
        self.console.print(
            "\n[bold cyan]🎤 Listening...[/bold cyan] "
            "[dim](Say 'Layra' or press Enter to activate)[/dim]"
        )

    def show_recording(self):
        """Show that Layra is recording user speech."""
        self.console.print("[bold yellow]🔴 Recording...[/bold yellow] [dim](Speak now)[/dim]")

    def show_thinking(self):
        """Show that Layra is processing."""
        self.console.print("[bold magenta]🧠 Processing...[/bold magenta]")

    def show_speaking(self):
        """Show that Layra is speaking."""
        self.console.print("[bold green]🔊 Speaking...[/bold green]")

    def show_user_input(self, text: str):
        """Display user's speech/text input."""
        self.console.print(
            Panel(
                f"[bold white]{text}[/bold white]",
                title="[bold cyan]👤 You[/bold cyan]",
                border_style="cyan",
                box=box.ROUNDED,
                padding=(0, 1),
            )
        )

    def show_layra_response(self, text: str):
        """Display Layra's response."""
        self.console.print(
            Panel(
                f"[bold yellow]{text}[/bold yellow]",
                title="[bold gold1]🤖 Layra[/bold gold1]",
                border_style="gold1",
                box=box.DOUBLE,
                padding=(0, 1),
            )
        )

    def show_action(self, action: str):
        """Show an action being performed."""
        self.console.print(f"  [dim cyan]⚡ {action}[/dim cyan]")

    def show_error(self, error: str):
        """Display an error message."""
        self.console.print(
            Panel(
                f"[bold red]{error}[/bold red]",
                title="[bold red]❌ Error[/bold red]",
                border_style="red",
                box=box.ROUNDED,
                padding=(0, 1),
            )
        )

    def show_success(self, message: str):
        """Display a success message."""
        self.console.print(f"  [bold green]✅ {message}[/bold green]")

    def show_warning(self, message: str):
        """Display a warning."""
        self.console.print(f"  [bold yellow]⚠️  {message}[/bold yellow]")

    def show_info(self, message: str):
        """Display info text."""
        self.console.print(f"  [dim]{message}[/dim]")

    def show_divider(self):
        """Show a divider line."""
        self.console.print("[dim yellow]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/dim yellow]")

    def show_help(self):
        """Show available commands."""
        table = Table(
            title="[bold cyan]Layra Commands[/bold cyan]",
            box=box.DOUBLE_EDGE,
            border_style="cyan",
            show_lines=True,
        )
        table.add_column("Category", style="bold cyan", width=15)
        table.add_column("Commands", style="white")

        table.add_row("🖥️ System", "Open/close apps, volume, brightness, WiFi, Bluetooth, dark mode, screenshot, lock, sleep")
        table.add_row("🌐 Browser", "Open URLs, search Google, search YouTube, open social media")
        table.add_row("🔍 Research", "Research any topic, weather, news, Wikipedia")
        table.add_row("📧 Email", "Check emails, send email, search emails")
        table.add_row("📱 Social", "Open Instagram, Twitter, LinkedIn, WhatsApp, etc.")
        table.add_row("📂 Projects", "Create/read files, git operations, run commands")
        table.add_row("🔧 Utilities", "Timer, calculator, notes, date/time, jokes, motivation")
        table.add_row("💬 Chat", "Just talk to Layra naturally!")

        self.console.print()
        self.console.print(table)
        self.console.print()

    def show_status_bar(self, mode: str = "idle"):
        """Show current status."""
        status_map = {
            "idle": "[dim]💤 Idle — Say 'Layra' to activate[/dim]",
            "listening": "[bold cyan]🎤 Listening...[/bold cyan]",
            "recording": "[bold yellow]🔴 Recording — Speak now...[/bold yellow]",
            "thinking": "[bold magenta]🧠 Thinking...[/bold magenta]",
            "speaking": "[bold green]🔊 Speaking...[/bold green]",
            "error": "[bold red]❌ Error occurred[/bold red]",
        }
        self.console.print(status_map.get(mode, status_map["idle"]))

    def show_goodbye(self):
        """Show shutdown message."""
        self.console.print()
        self.console.print(
            Panel(
                "[bold cyan]Goodbye, Sir. Layra going offline.\n"
                "All systems have been safely shut down.[/bold cyan]",
                title="[bold gold1]🤖 Layra[/bold gold1]",
                border_style="gold1",
                box=box.DOUBLE,
                padding=(1, 2),
            )
        )
        self.console.print()


# Create global UI instance
ui = TerminalUI()
