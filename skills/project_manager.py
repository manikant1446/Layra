"""
Layra Project Manager Module
=======================================
File management, Git operations, and project tasks.
"""

import subprocess
import logging
import os
from pathlib import Path
from datetime import datetime

logger = logging.getLogger("layra.project")


class ProjectManager:
    """Manages files, git operations, and project tasks."""

    def __init__(self, default_workspace: str = None):
        self.default_workspace = default_workspace or str(Path.home())

    def create_file(self, file_path: str, content: str) -> str:
        """Create a new file with given content."""
        try:
            path = Path(file_path).expanduser()
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            logger.info(f"📄 Created file: {path}")
            return f"File created: {path}"
        except Exception as e:
            return f"Error creating file: {e}"

    def read_file(self, file_path: str) -> str:
        """Read contents of a file."""
        try:
            path = Path(file_path).expanduser()
            if not path.exists():
                return f"File not found: {path}"
            content = path.read_text()
            # Limit output for voice
            if len(content) > 2000:
                content = content[:2000] + f"\n... (truncated, total {len(content)} chars)"
            return f"Contents of {path.name}:\n{content}"
        except Exception as e:
            return f"Error reading file: {e}"

    def list_files(self, directory: str = None) -> str:
        """List files in a directory."""
        try:
            path = Path(directory or self.default_workspace).expanduser()
            if not path.is_dir():
                return f"Not a directory: {path}"

            items = sorted(path.iterdir())
            files = []
            dirs = []
            for item in items:
                if item.name.startswith('.'):
                    continue
                if item.is_dir():
                    dirs.append(f"📁 {item.name}/")
                else:
                    size = item.stat().st_size
                    files.append(f"📄 {item.name} ({self._format_size(size)})")

            result = f"Contents of {path}:\n"
            result += "\n".join(dirs + files)
            return result

        except Exception as e:
            return f"Error listing files: {e}"

    def _format_size(self, size: int) -> str:
        """Format file size to human readable."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def delete_file(self, file_path: str) -> str:
        """Delete a file (moves to trash for safety)."""
        try:
            path = Path(file_path).expanduser()
            if not path.exists():
                return f"File not found: {path}"

            # Move to trash instead of deleting
            subprocess.run(
                ['/usr/bin/osascript', '-e',
                 f'tell application "Finder" to delete POSIX file "{path}"'],
                capture_output=True
            )
            return f"Moved to trash: {path.name}"
        except Exception as e:
            return f"Error deleting file: {e}"

    # ==========================================
    # Git Operations
    # ==========================================

    def git_operation(self, operation: str, args: str = "") -> str:
        """Perform git operations."""
        try:
            operations = {
                "status": "git status",
                "add": f"git add {args or '.'}",
                "commit": f'git commit -m "{args or "Update by Layra"}"',
                "push": "git push",
                "pull": "git pull",
                "log": "git log --oneline -10",
                "diff": f"git diff {args}",
                "branch": "git branch",
                "checkout": f"git checkout {args}",
                "stash": f"git stash {args}",
            }

            cmd = operations.get(operation)
            if not cmd:
                return f"Unknown git operation: {operation}. Available: {', '.join(operations.keys())}"

            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True,
                cwd=self.default_workspace, timeout=30
            )

            output = result.stdout.strip()
            if result.returncode != 0:
                output += f"\nError: {result.stderr.strip()}"

            logger.info(f"🔀 Git {operation}: {output[:200]}")
            return output or f"Git {operation} completed"

        except subprocess.TimeoutExpired:
            return f"Git {operation} timed out"
        except Exception as e:
            return f"Git error: {e}"

    # ==========================================
    # Terminal Commands
    # ==========================================

    def run_command(self, command: str) -> str:
        """Run a terminal command safely."""
        # Safety check
        dangerous = ['rm -rf /', 'rm -rf ~', 'sudo rm', 'mkfs', ':(){', 'dd if=']
        for d in dangerous:
            if d in command:
                return f"⚠️ Blocked potentially dangerous command: {command}"

        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True,
                cwd=self.default_workspace, timeout=60
            )
            output = result.stdout.strip()
            if result.returncode != 0 and result.stderr:
                output += f"\nError: {result.stderr.strip()}"
            return output or "Command executed successfully"
        except subprocess.TimeoutExpired:
            return "Command timed out (60s limit)"
        except Exception as e:
            return f"Command error: {e}"

    # ==========================================
    # Project Templates
    # ==========================================

    def create_project(self, name: str, project_type: str = "python") -> str:
        """Create a new project with basic structure."""
        try:
            base = Path(self.default_workspace) / name
            base.mkdir(parents=True, exist_ok=True)

            if project_type == "python":
                (base / "src").mkdir(exist_ok=True)
                (base / "tests").mkdir(exist_ok=True)
                (base / "src" / "__init__.py").touch()
                (base / "tests" / "__init__.py").touch()
                (base / "requirements.txt").touch()
                (base / "README.md").write_text(f"# {name}\n\nCreated by Layra\n")
                (base / ".gitignore").write_text("__pycache__/\n*.pyc\n.env\nvenv/\n")

            elif project_type == "web":
                (base / "css").mkdir(exist_ok=True)
                (base / "js").mkdir(exist_ok=True)
                (base / "index.html").write_text(f"<!DOCTYPE html>\n<html>\n<head><title>{name}</title></head>\n<body>\n<h1>{name}</h1>\n</body>\n</html>")
                (base / "css" / "style.css").write_text("/* Styles */\n")
                (base / "js" / "app.js").write_text("// App logic\n")

            elif project_type == "node":
                (base / "src").mkdir(exist_ok=True)
                (base / "package.json").write_text(
                    json.dumps({"name": name, "version": "1.0.0", "main": "src/index.js"}, indent=2)
                )
                (base / "src" / "index.js").write_text("// Entry point\n")
                (base / ".gitignore").write_text("node_modules/\n.env\n")

            # Initialize git
            subprocess.run(
                "git init", shell=True, cwd=str(base),
                capture_output=True, timeout=10
            )

            return f"Project '{name}' ({project_type}) created at {base}"

        except Exception as e:
            return f"Error creating project: {e}"


# Need json for create_project
import json
