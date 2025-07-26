# Contributing to tzkit

Thank you for considering contributing to tzkit! We welcome all contributions, including bug reports, feature requests, documentation improvements, and code contributions.

## How to Contribute

1. **Fork** the repository on GitHub
2. **Clone** your fork locally
   ```bash
   git clone https://github.com/your-username/tzkit.git
   cd tzkit
   ```
3. **Create a branch** for your changes
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Make your changes** and commit them with a clear message
   ```bash
   git commit -m "Add your commit message here"
   ```
5. **Push** your changes to your fork
   ```bash
   git push origin feature/your-feature-name
   ```
6. Open a **Pull Request** with a clear description of your changes

## Development Setup

1. Set up a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

3. Install the package in development mode:
   ```bash
   pip install -e .
   ```

## Running Tests

```bash
pytest
```

## Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use type hints for all function signatures
- Keep functions small and focused on a single responsibility
- Write docstrings for all public functions and classes

## Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Keep the first line under 72 characters
- Reference issues and pull requests liberally

## Reporting Issues

When reporting issues, please include:
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Environment details (OS, Python version, etc.)
- Any relevant error messages or logs

## Feature Requests

For feature requests, please:
1. Check if the feature has already been requested
2. Explain why this feature would be useful
3. Describe your proposed implementation (if applicable)

## Code Review Process

1. A maintainer will review your PR
2. You may receive feedback or be asked to make changes
3. Once approved, your PR will be merged

Thank you for contributing to tzkit!
