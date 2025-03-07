#!/usr/bin/env python3
import subprocess
import sys
import re
from pathlib import Path
from dataclasses import dataclass
from collections import defaultdict
from typing import List, Tuple, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
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
    console.print(f"Getting diff for {file_path}...", style="blue")
    stdout, _, code = run_git_command(["git", "diff", "--cached", "--", file_path])
    if code == 0 and stdout:
        return stdout
    stdout, _, code = run_git_command(["git", "diff", "--", file_path])
    return stdout if code == 0 else ""

def analyze_file_type(file_path: Path, diff: str) -> str:
    """
    Types:
    - feat: A new feature
    - fix: A bug fix
    - docs: Documentation only changes
    - style: Changes that do not affect the meaning of the code
    - refactor: A code change that neither fixes a bug nor adds a feature
    - perf: A code change that improves performance
    - test: Adding missing tests or correcting existing tests
    - build: Changes that affect the build system or external dependencies
    - ci: Changes to our CI configuration files and scripts
    - chore: Other changes that don't modify src or test files
    """
    type_patterns = {
        "test": (r"test[s]?/|testing/|__tests?__/|tests?\..*$|pytest\.ini$|conftest\.py$|.*_test\.py$|test_.*\.py$"),
        "docs": (r"^docs?/|\.md$|\.rst$|^(README|CHANGELOG|CONTRIBUTING|HISTORY|AUTHORS|SECURITY)(\.[^/]+)?$|^(COPYING|LICENSE)(\.[^/]+)?$|^(api|docs|documentation)/|.*\.docstring$"),
        "style": (r"\.(css|scss|sass|less|styl)$|^styles?/|^themes?/|\.editorconfig$|\.prettierrc|\.eslintrc|\.flake8$|\.style\.yapf$|\.isort\.cfg$|setup\.cfg$"),
        "ci": (r"^\.github/workflows/|^\.gitlab-ci|\.travis\.yml$|^\.circleci/|^\.azure-pipelines|^\.jenkins|^\.github/actions/|\.pre-commit-config\.yaml$"),
        "build": (r"^pyproject\.toml$|^setup\.(py|cfg)$|^requirements/|^requirements.*\.txt$|^poetry\.lock$|^Pipfile(\.lock)?$|^package(-lock)?\.json$|^yarn\.lock$|^Makefile$|^Dockerfile$|^docker-compose\.ya?ml$|^MANIFEST\.in$"),
        "perf": (r"^benchmarks?/|^performance/|\.*.profile$|^profiling/|^\.?cache/"),
        "chore": (r"^\.env(\.|$)|\.(ini|cfg|conf|json|ya?ml|toml|properties)$|^config/|^settings/|^\.git.*$")
    }

    diff_patterns = {
        "test": r"def test_|class Test|@pytest|unittest|@test|describe\s*\(|it\s*\(",
        "fix": r"fix|bug|issue|error|crash|resolve|closes?\s+#\d+",
        "refactor": r"refactor|clean|move|rename|restructure|rewrite",
        "perf": r"optimiz|performance|speed|memory|cpu|runtime|cache|faster|slower",
        "style": r"style|format|lint|prettier|eslint|indent|spacing"
    }

    def check_patterns(text: str, patterns: dict) -> Optional[str]:
        for type_name, pattern in patterns.items():
            if re.search(pattern, text, re.I):
                return type_name
        return None

    file_path_str = str(file_path).lower()
    file_type = check_patterns(file_path_str, type_patterns)
    if file_type:
        return file_type

    if diff:
        diff_type = check_patterns(diff.lower(), diff_patterns)
        if diff_type:
            return diff_type

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
    Respond with only expected commit follows best practices, without any introductions or explanations.
    """

	try:
		return model_prompt(prompt)
	except Exception as e:
		console.print(f"[red]Error generating commit message:[/red] {e}", style="bold red")
		pass

	return f"{changes[0].type}: update {' '.join(str(c.path.name) for c in changes)}"


def model_prompt(prompt: str) -> str:
	with Progress(
		SpinnerColumn(),
		TextColumn("[progress.description]{task.description}"),
		console=console,
	) as progress:
		task = progress.add_task("Waiting for model response...", total=None)

		response = g4f.ChatCompletion.create(
			model=g4f.models.gpt_4o_mini,
			messages=[
				{"role": "system",
				 "content": "Follow instructions precisely and respond concisely."},
				{"role": "user", "content": prompt}
			],
		)

		progress.remove_task(task)

	message = response.strip().split("\n")[0]
	console.print(message)
	return message


def commit_changes(files: List[str], message: str):
    with Progress(
        "[progress.description]{task.description}",
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        stage_task = progress.add_task("Staging files...", total=len(files))
        for file_path in files:
            run_git_command(["git", "add", "--", file_path])
            progress.advance(stage_task)
        
        commit_task = progress.add_task("Committing changes...", total=1)
        stdout, stderr, code = run_git_command(["git", "commit", "-m", message])
        progress.advance(commit_task)
        
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
    changes = get_valid_changes()
    if not changes:
        exit_with_no_changes()

    display_changes(changes)
    change_groups = group_related_changes(changes)

    for group in change_groups:
        process_change_group(group)

def get_valid_changes():
    changed_files = parse_git_status()
    if not changed_files:
        return []

    changes = []
    with Progress(
        "[progress.description]{task.description}",
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        analyze_task = progress.add_task("Analyzing files...", total=len(changed_files))
        diff_task = progress.add_task("Getting file diffs...", total=len(changed_files))
        
        for st, fp in changed_files:
            path = Path(fp)
            diff = get_file_diff(fp)
            progress.advance(diff_task)
            
            if diff:
                file_type = analyze_file_type(path, diff)
                changes.append(FileChange(path, st, diff, file_type))
            progress.advance(analyze_task)
    
    return changes

def create_file_change(status, file_path):
    path = Path(file_path)
    diff = get_file_diff(file_path)
    file_type = analyze_file_type(path, diff)
    return FileChange(path, status, diff, file_type) if diff else None

def exit_with_no_changes():
    console.print("[yellow]⚠ No changes to commit[/yellow]")
    sys.exit(0)

def process_change_group(group):
    message = generate_commit_message(group)
    display_commit_preview(message)
    response = input("Proceed with commit? (Y/n/e to edit): ").lower()

    if response == "n":
        console.print("[yellow]Skipping these changes...[/yellow]")
    elif response == "e":
        message = input("Enter new commit message: ")
        commit_changes([str(change.path) for change in group], message)
    else:
        commit_changes([str(change.path) for change in group], message)

def display_commit_preview(message):
    console.print(Panel(
        f"Proposed commit message:\n[bold cyan]{message}[/bold cyan]",
        title="Commit Preview",
        border_style="blue"
    ))

if __name__ == "__main__":
    main()
