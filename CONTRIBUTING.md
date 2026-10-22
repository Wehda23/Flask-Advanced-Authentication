# Contributing to flask-advanced-auth

Thank you for your interest in contributing to `flask-advanced-auth`!

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/Wehda23/Flask-Advanced-Authentication.git
   cd Flask-Advanced-Authentication
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

## Running Tests

Run the full test suite with coverage:
```bash
pytest -v
```

HTML coverage reports are generated automatically in `htmlcov/`.

## Code Style & Formatting

We use `black`, `isort`, `ruff`, and `mypy` for code quality:

```bash
# Format code
black flask_advanced_auth tests
isort flask_advanced_auth tests

# Linting
ruff check flask_advanced_auth tests

# Type check
mypy flask_advanced_auth
```

## Pull Request Process

1. Fork the repo and create your branch from `main`:
   ```bash
   git checkout -b feature/my-new-feature
   ```
2. Write tests covering your changes.
3. Ensure all tests pass with ≥ 80% coverage.
4. Update `CHANGELOG.md` under `[Unreleased]`.
5. Open a Pull Request describing your changes.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
