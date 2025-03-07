#!/usr/bin/env python3
import subprocess
import sys
from typing import List, Tuple, Dict, Optional
import g4f

from pathlib import Path
import re
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class FileChange:
    path: Path
    status: str  # 'M' (modified), 'A' (added), 'D' (deleted), 'R' (renamed)
    diff: str
    type: Optional[str] = None  # 'feat', 'fix', 'docs', etc.

def run_git_command(command: List[str]) -> Tuple[str, str, int]:
    """Run a git command and return stdout, stderr, and return code."""
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    stdout, stderr = process.communicate()
    return stdout, stderr, process.returncode

def get_changed_files() -> List[str]:
    """Get list of changed files."""
    stdout, stderr, code = run_git_command(['git', 'status', '--porcelain'])
    if code != 0:
        print(f"Error getting git status: {stderr}")
        # sys.exit(1)
    return [line.strip() for line in stdout.split('\n') if line.strip()]

def get_file_diff(file_path: str) -> str:
    """Get git diff for a specific file."""
    stdout, stderr, code = run_git_command(['git', 'diff', '--staged', file_path])
    if code != 0:
        print(f"Error getting git diff: {stderr}")
        # sys.exit(1)
    return stdout

def analyze_file_type(file_path: Path, diff: str) -> str:
    """Analyze file to suggest commit type."""
    file_types = {
        'test': r'(test|spec)[s]?\.py$',
        'docs': r'(docs/|\.md$|\.rst$)',
        'style': r'\.(css|scss|less)$',
        'ci': r'(\.github/|\.gitlab-ci|\.travis|\.circleci)',
        'build': r'(setup\.py|pyproject\.toml|requirements\.txt)',
    }
    
    # Check file path patterns
    for type_name, pattern in file_types.items():
        if re.search(pattern, str(file_path), re.I):
            return type_name
    
    # Check diff content
    if 'def test_' in diff or 'class Test' in diff:
        return 'test'
    if 'fix' in diff.lower() or 'bug' in diff.lower():
        return 'fix'
    if 'refactor' in diff.lower():
        return 'refactor'
    
    return 'feat'  # default to feature

def group_related_changes(changes: List[FileChange]) -> List[List[FileChange]]:
    """Group related file changes together."""
    groups = defaultdict(list)
    
    # Group by type and related files
    for change in changes:
        key = change.type
        if change.path.parent:
            # Group files in same directory
            key = f"{key}_{change.path.parent}"
        groups[key].append(change)
    
    return list(groups.values())

def generate_commit_message(changes: List[FileChange]) -> str:
    """Generate commit message for a group of related changes."""
    # Combine all diffs and paths for context
    combined_context = "\n".join([
        f"File: {change.path}\nStatus: {change.status}\nDiff:\n{change.diff}"
        for change in changes
    ])
    
    prompt = f"""
    Analyze these related file changes and create a conventional commit message.
    Rules:
    1. Format: type(scope): description
    2. Types: feat, fix, docs, style, refactor, test, chore
    3. Be specific but concise
    4. Use imperative mood
    5. Focus on the main change
    
    Changes:
    {combined_context}
    
    Generate only the commit message, nothing else.
    """
    
    
    try:
        response = g4f.ChatCompletion.create(
              model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
              web_search=False
        )
        message = response.strip().split('\n')[0]
        if message and any(t in message for t in ['feat', 'fix', 'docs', 'style', 'refactor', 'test', 'chore']):
            return message
    except Exception:
      pass
    
    # Fallback: Create conventional message from file analysis
    change_type = changes[0].type or 'chore'
    scope = changes[0].path.parent.name if changes[0].path.parent.name != '.' else None
    scope_str = f"({scope})" if scope else ""
    return f"{change_type}{scope_str}: update {', '.join(str(c.path.name) for c in changes)}"

def stage_file(file_path: str):
    """Stage a specific file."""
    stdout, stderr, code = run_git_command(['git', 'add', file_path])
    if code != 0:
        print(f"Error staging {file_path}: {stderr}")
        # sys.exit(1)

def commit_changes(message: str):
    """Commit changes with the given message."""
    stdout, stderr, code = run_git_command(['git', 'commit', '-m', message])
    if code != 0:
        print(f"Error committing changes: {stderr}")
        # sys.exit(1)
    print(f"Successfully committed with message: {message}")

def main():
    # Get all changed files
    changed_files = ['M MANIFEST.in', 'M poetry.lock', 'M pyproject.toml', 'AM requirements/build.txt', 'M requirements/deps.txt', 'M requirements/dev.txt', 'M requirements/test.txt', 'A  scripts/requirements.txt', 'AM scripts/smart_commit.py']
    if not changed_files:
        print("No changes to commit")
        # sys.exit(0)
    
    # Process each changed file
    changes = []
    for file_info in changed_files:
        status = file_info[:2].strip()
        file_path = file_info[3:].strip()
        
        # Stage the file to get its diff
        stage_file(file_path)
        diff = get_file_diff(file_path)
        
        # Create FileChange object
        path = Path(file_path)
        change = FileChange(
            path=path,
            status=status,
            diff=diff,
            type=analyze_file_type(path, diff)
        )
        changes.append(change)
    
    # Group related changes
    change_groups = group_related_changes(changes)
    
    # Process each group
    for group in change_groups:
        # Generate commit message
        print("\nAnalyzing changes for files:")
        for change in group:
            print(f"  - {change.path} ({change.type})")
        
        message = generate_commit_message(group)
        
        # Ask for confirmation
        print(f"\nProposed commit message: {message}")
        response = input("Proceed with commit? (Y/n/e to edit): ").lower()
        
        if response == 'n':
            print("Skipping these changes...")
            continue
        elif response == 'e':
            message = input("Enter new commit message: ")
        
        # Commit this group
        commit_changes(message)

if __name__ == "__main__":
    main()
