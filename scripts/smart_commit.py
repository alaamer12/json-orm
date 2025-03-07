#!/usr/bin/env python3
import subprocess
import sys
import re
from pathlib import Path
from dataclasses import dataclass
from collections import defaultdict
from typing import List, Tuple, Optional
from rich import print
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.text import Text
import g4f

console = Console()

@dataclass
class FileChange:
    path: Path
    status: str  # 'M' (modified), 'A' (added), 'D' (deleted), 'R' (renamed)
    diff: str
    type: Optional[str] = None  # 'feat', 'fix', 'docs', etc.

def run_git_command(command: List[str]) -> Tuple[str, str, int]:
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()
    return stdout, stderr, process.returncode

def parse_git_status() -> List[Tuple[str, str]]:
    stdout, stderr, code = run_git_command(["git", "status", "--porcelain"])
    if code != 0:
        console.print(f"[red]Error getting git status:[/red] {stderr}", style="bold red")
        sys.exit(1)
    
    changes = []
    for line in stdout.splitlines():
        if not line.strip():
            continue
        status, file_path = line[:2].strip(), line[3:].strip()
        if status == "R":
            file_path = file_path.split(" -> ")[1]
        changes.append((status, file_path))
    return changes

def get_file_diff(file_path: str) -> str:
    stdout, _, code = run_git_command(["git", "diff", "--cached", "--", file_path])
    if code == 0 and stdout:
        return stdout
    stdout, _, code = run_git_command(["git", "diff", "--", file_path])
    return stdout if code == 0 else ""

def analyze_file_type(file_path: Path, diff: str) -> str:
    patterns = {
        "test": r"(test|spec)[s]?\.py$",
        "docs": r"(docs/|\.md$|\.rst$)",
        "style": r"\.(css|scss|less)$",
        "ci": r"(\.github/|\.gitlab-ci|\.travis|\.circleci)",
        "build": r"(setup\.py|pyproject\.toml|requirements\.txt|Makefile)",
    }
    for type_name, pattern in patterns.items():
        if re.search(pattern, str(file_path), re.I):
            return type_name
    if diff:
        if "def test_" in diff or "class Test" in diff:
            return "test"
        if "fix" in diff.lower() or "bug" in diff.lower():
            return "fix"
        if "refactor" in diff.lower():
            return "refactor"
    return "feat"

def group_related_changes(changes: List[FileChange]) -> List[List[FileChange]]:
    groups = defaultdict(list)
    for change in changes:
        key = f"{change.type}_{change.path.parent}" if change.path.parent.name != '.' else change.type
        groups[key].append(change)
    return list(groups.values())

def generate_commit_message(changes: List[FileChange]) -> str:
    combined_context = "\n".join([f"{change.status} {change.path}" for change in changes])
    prompt = f"""
    Analyze these file changes and generate a conventional commit message:
    {combined_context}
    """
    try:
        response = g4f.ChatCompletion.create(
            model=g4f.models.gpt_35_turbo,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.strip().split("\n")[0]
    except Exception:
        pass
    return f"{changes[0].type}: update {' '.join(str(c.path.name) for c in changes)}"

def commit_changes(files: List[str], message: str):
    for file_path in files:
        run_git_command(["git", "add", "--", file_path])
    stdout, stderr, code = run_git_command(["git", "commit", "-m", message])
    if code == 0:
        console.print(f"[green]✔ Successfully committed:[/green] {message}")
    else:
        console.print(f"[red]✘ Error committing changes:[/red] {stderr}")

def reset_staging():
    run_git_command(["git", "reset", "HEAD"])

def display_changes(changes: List[FileChange]):
    table = Table(title="Staged Changes", show_header=True, header_style="bold magenta")
    table.add_column("Status", justify="center")
    table.add_column("File Path")
    table.add_column("Type", justify="center")
    for change in changes:
        table.add_row(f"[cyan]{change.status}[/cyan]", f"[white]{change.path}[/white]", f"[green]{change.type}[/green]")
    console.print(table)

def main():
    reset_staging()
    changed_files = parse_git_status()
    if not changed_files:
        console.print("[yellow]⚠ No changes to commit[/yellow]")
        sys.exit(0)
    
    changes = [FileChange(Path(fp), st, get_file_diff(fp), analyze_file_type(Path(fp), get_file_diff(fp))) for st, fp in changed_files]
    if not changes:
        console.print("[yellow]⚠ No valid changes to commit[/yellow]")
        sys.exit(0)
    
    display_changes(changes)
    change_groups = group_related_changes(changes)
    
    for group in change_groups:
        message = generate_commit_message(group)
        console.print(Panel(f"Proposed commit message:\n[bold cyan]{message}[/bold cyan]", title="Commit Preview", border_style="blue"))
        response = Prompt.ask("Proceed with commit? (Y/n/e to edit)", choices=["y", "n", "e"], default="y")
        
        if response == "n":
            console.print("[yellow]Skipping these changes...[/yellow]")
            continue
        elif response == "e":
            message = Prompt.ask("Enter new commit message")
        
        commit_changes([str(change.path) for change in group], message)

if __name__ == "__main__":
    main()
