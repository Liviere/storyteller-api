# Tests for Story Teller API

This directory contains comprehensive unit and integration tests for the Story Teller API.

## Test Structure

```
tests/
├── __init__.py              # Package marker
├── conftest.py             # Test configuration and fixtures
├── test_models.py          # Tests for SQLAlchemy models
├── test_schemas.py         # Tests for Pydantic schemas
├── test_api.py             # Tests for API endpoints
├── test_main.py            # Tests for main application
├── test_integration.py     # Integration tests
└── README.md              # This file
```

## Test Categories

### Unit Tests

- **test_models.py**: Tests for SQLAlchemy models including validation, relationships, and database operations
- **test_schemas.py**: Tests for Pydantic schemas including validation and serialization
- **test_main.py**: Tests for main application endpoints and configuration

### API Tests

- **test_api.py**: Comprehensive tests for all story-related API endpoints including CRUD operations, filtering, and error handling

### Integration Tests

- **test_integration.py**: End-to-end tests that verify complete workflows and component interactions

## Running Tests

### Run All Tests

```bash
# Using Poetry
poetry run pytest

# Or using VS Code task
# Ctrl+Shift+P -> "Tasks: Run Task" -> "Poetry: Run Tests"
```

### Run Specific Test Categories

```bash
# Run only unit tests
poetry run pytest tests/test_models.py tests/test_schemas.py tests/test_main.py

# Run only API tests
poetry run pytest tests/test_api.py

# Run only integration tests
poetry run pytest tests/test_integration.py
```

### Run Tests with Coverage

```bash
# Generate coverage report
poetry run pytest --cov=. --cov-report=html

# View coverage report
open reports/coverage/index.html
```

### Run Tests with Verbose Output

```bash
poetry run pytest -v
```

### Run Specific Test

```bash
# Run a specific test class
poetry run pytest tests/test_api.py::TestStoriesAPI

# Run a specific test method
poetry run pytest tests/test_api.py::TestStoriesAPI::test_create_story
```

## Test Fixtures

The tests use several fixtures defined in `conftest.py`:

- **temp_db**: Creates a temporary SQLite database for testing
- **db_session**: Provides a database session for tests
- **client**: FastAPI test client with temporary database
- **sample_story_data**: Sample story data for testing
- **sample_stories_data**: Multiple sample stories for testing

## Test Database

Tests use a temporary SQLite database that is created and destroyed for each test session. This ensures:

- Tests are isolated and don't affect each other
- No test data persists between test runs
- Tests can run in parallel without conflicts

## Writing New Tests

When adding new tests:

1. **Follow naming conventions**: Test files should start with `test_`, test classes with `Test`, and test methods with `test_`

2. **Use appropriate fixtures**: Use the provided fixtures for database sessions and test clients

3. **Test both success and failure cases**: Include tests for valid inputs and error conditions

4. **Use descriptive test names**: Test method names should clearly describe what is being tested

5. **Add docstrings**: Include docstrings explaining what each test does

Example test:

```python
def test_create_story_with_valid_data(self, client, sample_story_data):
    """Test creating a story with valid data returns 200 and correct data."""
    response = client.post("/api/v1/stories/", json=sample_story_data)

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == sample_story_data["title"]
    assert "id" in data
```

## Test Coverage Goals

Aim for high test coverage across all components:

- Models: 100% (all fields, validations, relationships)
- Schemas: 100% (all validation rules and serialization)
- API endpoints: 100% (all routes, success and error cases)
- Main application: 100% (configuration, middleware, startup)

## Continuous Integration

These tests are designed to run in CI/CD pipelines. They:

- Use temporary databases (no external dependencies)
- Clean up after themselves
- Provide clear failure messages
- Generate coverage reports

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure all dependencies are installed with `poetry install`

2. **Database connection errors**: Tests use temporary databases, but check that SQLAlchemy is properly configured

3. **Fixture not found**: Make sure `conftest.py` is in the same directory or a parent directory

4. **Test isolation issues**: Each test should clean up after itself or use fresh fixtures

### Debug Mode

Run tests with more verbose output for debugging:

```bash
poetry run pytest -vvv --tb=long
```
