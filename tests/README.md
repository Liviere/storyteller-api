# Tests for Story Teller API

This directory contains comprehensive unit, integration, and end-to-end tests for the Story Teller API, organized by functionality and router structure.

## Test Structure

```
tests/
├── __init__.py              # Package marker
├── conftest.py             # Main test configuration and fixtures
├── README.md              # This file
├── shared/                # Shared component tests (reusable across routers)
│   ├── __init__.py
│   ├── test_models.py     # SQLAlchemy model tests
│   ├── test_schemas.py    # Pydantic schema tests
│   └── test_main.py       # Main application tests
├── stories/               # Stories router tests
│   ├── __init__.py
│   ├── conftest.py        # Stories-specific fixtures
│   ├── test_unit.py       # Unit tests (validation, business logic)
│   └── test_integration.py # Integration tests (API endpoints)
├── llm/                   # LLM functionality tests
│   ├── __init__.py
│   ├── conftest.py        # LLM-specific fixtures and configuration
│   ├── test_unit.py       # Unit tests with mocked LLM services
│   ├── test_integration.py # Real LLM API integration tests
│   └── test_llm_api.py    # LLM API endpoint tests (mocked)
└── e2e/                   # End-to-end workflows and performance tests
    ├── __init__.py
    ├── conftest.py        # E2E test fixtures
    ├── test_workflows.py  # Complete user journey tests
    ├── locustfile.py      # Performance testing scenarios
    ├── config.py          # Performance test configuration
    └── README.md          # E2E testing documentation
```

## Test Categories

### Shared Component Tests (`tests/shared/`)

**Purpose**: Tests for core components used across multiple routers

- **test_models.py** (6 tests): SQLAlchemy model validation, relationships, and database operations
- **test_schemas.py** (10 tests): Pydantic schema validation, serialization, and field constraints
- **test_main.py** (5 tests): Main application endpoints, CORS, and documentation

### Stories Router Tests (`tests/stories/`)

**Purpose**: Complete testing of story management functionality

- **test_unit.py** (16 tests): Story validation, business logic, filtering, and helper functions
- **test_integration.py** (18 tests): Full API endpoint testing including CRUD operations, filtering, publishing

### LLM Functionality Tests (`tests/llm/`)

**Purpose**: Comprehensive testing of AI/LLM integration

- **test_unit.py** (25 tests): Configuration validation, service initialization, mocked LLM operations
- **test_integration.py** (7 tests): Real API calls to configured LLM providers (requires API keys)
- **test_llm_api.py** (19 tests): FastAPI endpoint testing with mocked LLM services

### End-to-End Tests (`tests/e2e/`)

**Purpose**: Complete user workflows and performance testing

- **test_workflows.py** (6 tests): Full user journeys combining story management with LLM operations
- **locustfile.py**: Performance testing scenarios (light, medium, heavy load testing)
- **config.py**: Performance test configuration and scenarios

## Running Tests

### Run All Tests (107 total)

```bash
# Run all tests
poetry run pytest

# Run with verbose output
poetry run pytest -v

# Run with coverage report
poetry run pytest --cov=. --cov-report=html
open reports/coverage/index.html
```

### Run Tests by Category

```bash
# Shared component tests (16 tests)
poetry run pytest tests/shared/ -v

# Stories functionality tests (34 tests)
poetry run pytest tests/stories/ -v

# LLM functionality tests (51 tests)
poetry run pytest tests/llm/ -v

# End-to-end workflow tests (6 tests)
poetry run pytest tests/e2e/ -v
```

### Run Specific Test Files

```bash
# Individual test files
poetry run pytest tests/shared/test_models.py -v
poetry run pytest tests/stories/test_integration.py -v
poetry run pytest tests/llm/test_unit.py -v
poetry run pytest tests/e2e/test_workflows.py -v
```

### Run Tests with Markers

```bash
# Skip LLM integration tests (requires API keys)
poetry run pytest -m "not llm_integration"

# Run only slow tests
poetry run pytest -m "slow"

# Run only fast unit tests
poetry run pytest tests/shared/ tests/stories/test_unit.py tests/llm/test_unit.py
```

### Run Specific Test Methods

```bash
# Specific test class
poetry run pytest tests/stories/test_integration.py::TestStoriesAPI -v

# Specific test method
poetry run pytest tests/stories/test_integration.py::TestStoriesAPI::test_create_story -v

# Pattern matching
poetry run pytest -k "test_story_creation" -v
```

## LLM Testing

LLM tests require specific setup:

### Environment Variables

LLM integration tests automatically detect required API keys from your `llm_config.yaml` configuration:

```bash
# The test system automatically reads your llm_config.yaml and checks
# for API keys defined in each provider's 'api_key_env' field

# Example: If your config has providers like:
# providers:
#   openai:
#     api_key_env: "OPENAI_API_KEY"
#   deepinfra:
#     api_key_env: "DEEPINFRA_API_KEY"
#   custom:
#     api_key_env: "CUSTOM_API_KEY"
#     requires_api_key: false  # This provider won't be checked

# Then tests will check for: OPENAI_API_KEY, DEEPINFRA_API_KEY
# And skip providers that have requires_api_key: false

export OPENAI_API_KEY="your-openai-key"
export DEEPINFRA_API_KEY="your-deepinfra-key"
# Add other keys as defined in your config

# Tests will automatically skip if required keys are missing
poetry run pytest tests/llm/test_integration.py
```

**Smart API Key Detection:**

- Tests dynamically read `llm_config.yaml` to determine required API keys
- Only providers with `requires_api_key: true` (default) are checked
- Providers with `requires_api_key: false` are skipped from validation
- Tests automatically skip if any required keys are missing
- No hardcoded provider list - fully configurable via YAML

### LLM Test Configuration

LLM tests dynamically adapt to your `llm_config.yaml` configuration:

- **Unit tests**: Fast tests with mocked services (no API calls, no configuration dependency)
- **Integration tests**: Real API calls to providers defined in your YAML config
- **API tests**: FastAPI endpoint tests with mocked LLM services
- **Configuration-aware**: Tests automatically detect which providers are enabled and their API key requirements
- **Flexible providers**: Support any provider defined in YAML with custom `api_key_env` settings
- **Smart skipping**: Tests skip gracefully when required API keys are missing or providers are disabled

## Performance Testing

### Start Application

```bash
# Start the application first
poetry run uvicorn main:app --reload --port 8080
```

### Run Performance Tests

```bash
# Web interface for interactive testing
poetry run locust -f tests/e2e/locustfile.py --host=http://localhost:8080

# Headless mode with different scenarios
poetry run locust -f tests/e2e/locustfile.py --host=http://localhost:8080 \
  --headless --users 10 --spawn-rate 2 --run-time 2m --html reports/light_load.html

poetry run locust -f tests/e2e/locustfile.py --host=http://localhost:8080 \
  --headless --users 50 --spawn-rate 5 --run-time 5m --html reports/medium_load.html
```

### Using VS Code Tasks

```bash
# Pre-configured performance test tasks
# Open Command Palette (Ctrl+Shift+P) and search for "Tasks: Run Task"
- "Locust: Light Load Test"
- "Locust: Medium Load Test"
- "Locust: Heavy Load Test"
```

## Test Architecture

### Router-Based Organization

The new test structure follows the application's router organization:

- **Shared components** (`tests/shared/`): Core components used across multiple routers
- **Router-specific tests** (`tests/stories/`, `tests/llm/`): Tests organized by API router
- **End-to-end tests** (`tests/e2e/`): Complete workflows spanning multiple components

### Test Isolation and Fixtures

- **Database isolation**: Each test uses temporary SQLite database or dedicated MySQL test instance
- **Fixture hierarchy**: Main `conftest.py` provides shared fixtures, router-specific `conftest.py` files provide specialized fixtures
- **LLM mocking**: Unit tests use mocked LLM services, integration tests use real APIs with graceful skipping

### Test Markers

Tests use pytest markers for organization:

- `@pytest.mark.llm_integration`: Tests requiring real LLM API calls
- `@pytest.mark.slow`: Tests that take longer to execute
- `@pytest.mark.asyncio`: Async tests

## Test Coverage Goals

Current coverage: **76.57%** across 107 tests

**Coverage by component:**

- **Stories router**: High coverage (API endpoints, business logic)
- **Shared components**: Full coverage (models, schemas, main app)
- **LLM functionality**: Good coverage with both mocked and real API tests
- **End-to-end workflows**: Complete user journey coverage

## Writing New Tests

### Guidelines

1. **Follow router organization**: Place tests in appropriate router directory
2. **Use shared components**: Leverage `tests/shared/` for reusable component tests
3. **Mock external services**: Use mocks for unit tests, real APIs for integration tests
4. **Test error cases**: Include both success and failure scenarios

### Example Test Structure

```python
# tests/stories/test_unit.py
class TestStoryValidation:
    def test_story_create_validation(self):
        """Test story creation validation logic."""
        # Unit test with mocked dependencies

# tests/stories/test_integration.py
class TestStoriesAPI:
    def test_create_story(self, client, sample_story_data):
        """Test story creation via API endpoint."""
        # Integration test with real database
```

## Docker Test Environment

For production-like testing with MySQL:

```bash
# Start isolated test database (MySQL on port 3307)
docker-compose -f docker-compose.test.yml up -d

# Run tests with MySQL instead of SQLite
TEST_DATABASE_URL="mysql+mysqlconnector://test_user:test_pass@localhost:3307/storyteller_test" \
poetry run pytest tests/ -v

# Cleanup test environment
docker-compose -f docker-compose.test.yml down -v
```

## Troubleshooting

### Common Issues

**LLM Integration Tests Failing:**

```bash
# Set required API keys
export OPENAI_API_KEY="your-key"
export DEEPINFRA_API_KEY="your-key"

# Or skip LLM integration tests
poetry run pytest -m "not llm_integration"
```

**Database Connection Issues:**

```bash
# Use SQLite for local testing
poetry run pytest tests/

# Use MySQL test instance for production-like testing
docker-compose -f docker-compose.test.yml up -d
TEST_DATABASE_URL="mysql+mysqlconnector://test_user:test_pass@localhost:3307/storyteller_test" poetry run pytest
```

**Performance Test Issues:**

```bash
# Ensure application is running first
poetry run uvicorn main:app --reload --port 8080

# Then run performance tests
poetry run locust -f tests/e2e/locustfile.py --host=http://localhost:8080
```

### Debug Mode

```bash
# Verbose output with full tracebacks
poetry run pytest -vvv --tb=long

# Run specific failing test with maximum detail
poetry run pytest tests/stories/test_integration.py::TestStoriesAPI::test_create_story -vvv --tb=long
```
