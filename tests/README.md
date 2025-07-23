# Tests for SK HPC Services Chatbot

This directory contains test files for various components of the HPC chatbot system.

## Test Files

- `test_card.py` - Tests for booking card generation and display functionality
- `test_markdown.py` - Tests for markdown rendering and formatting

## Running Tests

To run all tests:
```bash
python -m pytest tests/
```

To run specific test file:
```bash
python tests/test_card.py
python tests/test_markdown.py
```

## Test Dependencies

Make sure you have the required dependencies installed:
```bash
pip install pytest
```

## Adding New Tests

When adding new test files, please follow the naming convention:
- Test files should start with `test_`
- Test functions should start with `test_`
- Include docstrings explaining what each test does
