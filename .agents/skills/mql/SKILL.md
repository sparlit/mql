```markdown
# mql Development Patterns

> Auto-generated skill from repository analysis

## Overview
This skill covers the core development patterns and conventions used in the `mql` Python codebase. It documents file organization, import/export styles, commit practices, and testing patterns. Whether you're contributing new features or maintaining existing code, this guide will help you align with the project's standards for consistency and clarity.

## Coding Conventions

### File Naming
- Use **snake_case** for all file names.
  - Example: `query_parser.py`, `data_loader.py`

### Import Style
- Use **relative imports** within the package.
  - Example:
    ```python
    from .utils import parse_query
    from .models import QueryModel
    ```

### Export Style
- Use **named exports** by explicitly listing public objects in `__all__` or by direct import.
  - Example:
    ```python
    __all__ = ['QueryParser', 'parse_query']
    ```

### Commit Messages
- Commit messages are **freeform** and may not follow a strict prefix.
- Average commit message length is about 58 characters.
  - Example:  
    ```
    Fix bug in query parsing for nested conditions
    ```

## Workflows

### Adding a New Module
**Trigger:** When you need to add a new feature or functionality.
**Command:** `/add-module`

1. Create a new Python file using snake_case (e.g., `feature_x.py`).
2. Implement the functionality, using relative imports for shared code.
3. Add named exports as needed.
4. Write corresponding tests in a file matching `*.test.*`.
5. Commit your changes with a clear, descriptive message.

### Running Tests
**Trigger:** When you want to verify your code changes.
**Command:** `/run-tests`

1. Locate all test files matching the pattern `*.test.*`.
2. Run the tests using your preferred Python test runner (e.g., `pytest`, `unittest`).
   - Example:
     ```
     pytest
     ```
3. Check the output and fix any failing tests.

### Refactoring Imports
**Trigger:** When reorganizing code or resolving import errors.
**Command:** `/refactor-imports`

1. Ensure all imports within the package use relative paths.
   - Example:
     ```python
     from .helpers import some_function
     ```
2. Update any absolute imports to relative ones.
3. Run tests to confirm nothing is broken.

## Testing Patterns

- Test files follow the pattern `*.test.*` (e.g., `query_parser.test.py`).
- The specific test framework is **unknown**, so use standard Python testing practices.
- Place tests alongside or near the code they test.
- Example test file structure:
  ```python
  # query_parser.test.py
  import unittest
  from .query_parser import parse_query

  class TestQueryParser(unittest.TestCase):
      def test_simple_query(self):
          self.assertEqual(parse_query("SELECT *"), expected_result)
  ```

## Commands
| Command         | Purpose                                 |
|-----------------|-----------------------------------------|
| /add-module     | Add a new module following conventions  |
| /run-tests      | Run all tests in the repository         |
| /refactor-imports | Refactor imports to use relative style |
```
