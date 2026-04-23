# AGENTS.md

Operational guide for ShopifyProductTools. Keep under 60 lines.

## Build & Run

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run development server
uvicorn src.main:app --reload --port 8000

# Run CLI
python -m src.main --help
```

## Validation

Run these after implementing to get immediate feedback:

```bash
# Tests
pytest tests/ -v

# Typecheck
mypy src/

# Lint
ruff check src/
black --check src/
```

## Project Structure

- `src/` - Application source code
- `src/api/` - FastAPI routes
- `src/services/` - Business logic
- `src/models/` - Data models
- `tests/` - Test files

## Codebase Patterns

- Use Pydantic for data validation
- Use async/await for I/O operations
- One module per feature area
- Tests mirror src structure: `src/foo.py` → `tests/test_foo.py`

## Operational Notes

[Add learnings here as you discover them]
