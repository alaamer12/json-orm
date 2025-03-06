# Contributing to JsonDB

Thank you for your interest in contributing to JsonDB! This document provides guidelines and instructions for contributing to this project.

## Development Setup

1. Fork and clone the repository:
```bash
git clone https://github.com/yourusername/jsondb.git
cd jsondb
```

2. Create a virtual environment and activate it:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -r requirements/dev.txt
```

4. Install pre-commit hooks:
```bash
pre-commit install
```

## Development Workflow

1. Create a new branch for your feature or bugfix:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes and ensure:
   - All tests pass: `make test`
   - Code is properly formatted: `make format`
   - Linting passes: `make lint`
   - Type checking passes: `make typecheck`

3. Write tests for new features or bug fixes
4. Update documentation as needed
5. Add an entry to CHANGELOG.md under [Unreleased]

## Pull Request Process

1. Update the README.md with details of major changes
2. Update the documentation if you're adding or modifying features
3. Run the full test suite and ensure all tests pass
4. Push your changes and create a Pull Request
5. Wait for review and address any feedback

## Commit Messages

Follow conventional commits format:
- feat: New feature
- fix: Bug fix
- docs: Documentation changes
- style: Code style changes (formatting, etc)
- refactor: Code refactoring
- test: Adding or modifying tests
- chore: Maintenance tasks

## Code Style

- Follow PEP 8 guidelines
- Use type hints for all function parameters and return values
- Write docstrings for all public functions and classes
- Keep functions focused and single-purpose
- Write clear, descriptive variable and function names

## Testing

- Write unit tests for all new features
- Maintain or improve code coverage
- Test edge cases and error conditions
- Use pytest fixtures and parametrize when appropriate

## Documentation

- Update docstrings for modified functions
- Keep README.md up to date
- Add examples for new features
- Update FEATURES.md for new SQL features

## Questions or Problems?

- Open an issue for bugs or feature requests
- Join our community discussions
- Check existing issues before creating new ones

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License.
