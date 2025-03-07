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
import concurrent.futures
from concurrent.futures import TimeoutError

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
	"""Analyze the file type based on its path and content."""
	# Check if the file path contains 'scripts' first
	if "scripts" in file_path.parts:
		return "chore"

	if is_test_file(file_path):
		return "test"

	file_type = check_file_path_patterns(file_path)
	if file_type:
		return file_type

	diff_type = check_diff_patterns(diff)
	if diff_type:
		return diff_type

	return "feat"


def is_test_file(file_path: Path) -> bool:
	"""Check if the file is in a dedicated test directory."""
	return any(part.lower() in ("tests", "test") for part in file_path.parts)


def check_file_path_patterns(file_path: Path) -> Optional[str]:
	"""Check file name patterns to determine file type."""
	type_patterns = {
		"test": r"^tests?/|^testing/|^__tests?__/|^test_.*\.py$|^.*_test\.py$",
		"docs": r"^docs?/|\.md$|\.rst$|^(README|CHANGELOG|CONTRIBUTING|HISTORY|AUTHORS|SECURITY)(\.[^/]+)?$|^(COPYING|LICENSE)(\.[^/]+)?$|^(api|docs|documentation)/|.*\.docstring$",
		"style": r"\.(css|scss|sass|less|styl)$|^styles?/|^themes?/|\.editorconfig$|\.prettierrc|\.eslintrc|\.flake8$|\.style\.yapf$|\.isort\.cfg$|setup\.cfg$",
		"ci": r"^\.github/workflows/|^\.gitlab-ci|\.travis\.yml$|^\.circleci/|^\.azure-pipelines|^\.jenkins|^\.github/actions/|\.pre-commit-config\.yaml$",
		"build": r"^pyproject\.toml$|^setup\.(py|cfg)$|^requirements/|^requirements.*\.txt$|^poetry\.lock$|^Pipfile(\.lock)?$|^package(-lock)?\.json$|^yarn\.lock$|^Makefile$|^Dockerfile$|^docker-compose\.ya?ml$|^MANIFEST\.in$",
		"perf": r"^benchmarks?/|^performance/|\.*.profile$|^profiling/|^\.?cache/",
		"chore": r"^\.env(\.|$)|\.(ini|cfg|conf|json|ya?ml|toml|properties)$|^config/|^settings/|^\.git.*$"
	}
	return check_patterns(str(file_path), type_patterns)


def check_diff_patterns(diff: str) -> Optional[str]:
	"""Check diff content patterns to determine file type."""
	diff_patterns = {
		"test": r"\bdef test_|\bclass Test|\@pytest|\bunittest|\@test\b",
		"fix": r"\bfix|\bbug|\bissue|\berror|\bcrash|resolve|closes?\s+#\d+",
		"refactor": r"\brefactor|\bclean|\bmove|\brename|\brestructure|\brewrite",
		"perf": r"\boptimiz|\bperformance|\bspeed|\bmemory|\bcpu|\bruntime|\bcache|\bfaster|\bslower",
		"style": r"\bstyle|\bformat|\blint|\bprettier|\beslint|\bindent|\bspacing"
	}
	return check_patterns(diff.lower(), diff_patterns)


def check_patterns(text: str, patterns: dict) -> Optional[str]:
	"""Check if text matches any pattern in the given dictionary."""
	for type_name, pattern in patterns.items():
		if re.search(pattern, text, re.I):
			return type_name
	return None

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

	model_message = model_prompt(prompt)
	if model_message:
		return model_message

	return f"{changes[0].type}: update {' '.join(str(c.path.name) for c in changes)}"


def model_prompt(prompt: str) -> str:
    def get_model_response():
        return g4f.ChatCompletion.create(
            model=g4f.models.gpt_4o_mini,
            messages=[
                {"role": "system", "content": "Follow instructions precisely and respond concisely."},
                {"role": "user", "content": prompt}
            ],
        )

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Waiting for model response...", total=None)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(get_model_response)
            try:
                response = future.result(timeout=10)  # 5 second timeout
                progress.remove_task(task)
                message = response.strip().split("\n")[0]
                console.print(message)
                return message
            except (TimeoutError, Exception) as e:
                progress.remove_task(task)
                if isinstance(e, TimeoutError):
                    console.print("[yellow]Model response timed out, using fallback message[/yellow]")
                else:
                    console.print(f"[yellow]Error in model response, using fallback message: {str(e)}[/yellow]")
                return None


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
