# Tests for Story Teller API

This directory contains comprehensive unit, integration, and end-to-end tests for the Story Teller API, designed for **asynchronous task processing with Celery**. The testing strategy follows a simplified three-tier approach with consistent file structure.

## 🏗️ Test Architecture

### **Simplified Three-Tier Testing Strategy:**

#### **Tier 1: Unit Tests** (`@pytest.mark.unit`)

- **Purpose**: Rapid feedback during development
- **Method**: SQLite in-memory database, mocked external services
- **Files**: `test_unit.py` in each component folder
- **Usage**: Continuous development, pre-commit hooks, TDD cycles

#### **Tier 2: Integration Tests** (`@pytest.mark.integration`)

- **Purpose**: Database integration and API validation
- **Method**: MySQL test database, real API endpoints, mocked external services
- **Files**: `test_integration.py` in each component folder
- **Usage**: Pre-deployment validation, CI/CD pipelines

#### **Tier 3: End-to-End Tests** (`@pytest.mark.e2e`)

- **Purpose**: Complete workflow validation with real infrastructure
- **Method**: MySQL + Redis + Celery workers + real LLM providers
- **Files**: `test_e2e.py` in each component folder
- **Usage**: Production readiness verification, regression testing

## 📁 Test Structure

```
tests/
├── __init__.py                     # Package marker
├── conftest.py                     # Core test configuration and fixtures
├── README.md                       # This file
│
├── shared/                         # 🧱 Foundation Components
│   ├── __init__.py
│   └── test_integration.py         # FastAPI application integration tests
│
├── tasks/                          # ⚡ Celery Task Management
│   ├── __init__.py
│   ├── test_unit.py                # TaskService unit tests (mocked)
│   └── test_integration.py         # Task API endpoints with MySQL
│
├── stories/                        # 📚 Story Management
│   ├── __init__.py
│   ├── test_unit.py                # Story business logic validation
│   ├── test_integration.py         # Story API endpoints with database
│   └── test_e2e.py                 # Complete story workflows with Celery
│
├── llm/                            # 🤖 AI/LLM Functionality
│   ├── __init__.py
│   ├── test_unit.py                # LLM service unit tests (mocked)
│   ├── test_integration.py         # LLM API endpoints with database
│   └── test_e2e.py                 # Full LLM workflows with real providers
│
└── performance/                    # 🚀 Performance Testing
    ├── __init__.py
    ├── locustfile.py               # Performance testing scenarios
    └── config.py                   # Performance test configuration
```

### Performance Tests (`tests/performance/`)

**Purpose**: Performance and load testing

- **locustfile.py**: Performance testing scenarios (light, medium, heavy load testing)
- **config.py**: Performance test configuration and scenarios

## Testing Strategies

This repository employs a **simplified three-tier testing strategy** optimized for development speed and maintainability:

### Test Execution Framework

#### Simplified Test Markers

Our test suite uses three simple pytest markers:

- `@pytest.mark.unit`: Fast unit tests with mocked dependencies
- `@pytest.mark.integration`: Database integration tests with mocked external services
- `@pytest.mark.e2e`: End-to-end tests with real infrastructure (Celery, Redis, LLM providers)

## 🚀 Launching tests

```bash
# All tests (unit, integration, e2e)
./test-setup.sh init              # Initialize full test environment with MySQL, Redis, and Celery Worker
./test-setup.sh test              # Run all tests (unit, integration, e2e)

# or selectively run tests
./test-setup.sh test-unit         # Run unit tests only
./test-setup.sh test-integration  # Run integration tests with MySQL
./test-setup.sh test-e2e          # Run end-to-end tests with full infrastructure

./test-setup.sh stop              # Stop all test services
./test-setup.sh clean             # Clean up test environment (removes all data)
```

## LLM Testing

LLM tests require specific setup for end-to-end testing:

### Environment Variables

E2E LLM tests automatically detect required API keys from your `llm_config.yaml` configuration:

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

# Then e2e tests will check for: OPENAI_API_KEY, DEEPINFRA_API_KEY
# And skip providers that have requires_api_key: false

export OPENAI_API_KEY="your-openai-key"
export DEEPINFRA_API_KEY="your-deepinfra-key"
# Add other keys as defined in your config

# E2E tests will automatically skip if required keys are missing
poetry run pytest tests/llm/test_e2e.py -v
```

**Smart API Key Detection:**

- Tests dynamically read `llm_config.yaml` to determine required API keys
- Only providers with `requires_api_key: true` (default) are checked
- Providers with `requires_api_key: false` are skipped from validation
- Tests automatically skip if any required keys are missing
- No hardcoded provider list - fully configurable via YAML

## Performance Testing

### Start Application

```bash
# Start the application first
poetry run uvicorn main:app --reload --port 8080
```

### Run Performance Tests

```bash
# Web interface for interactive testing
poetry run locust -f tests/performance/locustfile.py --host=http://localhost:8080

# Headless mode with different scenarios
poetry run locust -f tests/performance/locustfile.py --host=http://localhost:8080 \
  --headless --users 10 --spawn-rate 2 --run-time 2m --html reports/light_load.html

poetry run locust -f tests/performance/locustfile.py --host=http://localhost:8080 \
  --headless --users 50 --spawn-rate 5 --run-time 5m --html reports/medium_load.html
```

### Using VS Code Tasks

Performance testing tasks are available in VS Code:

- `Locust: Start Web Interface`
- `Locust: Light Load Test`
- `Locust: Medium Load Test`
- `Locust: Heavy Load Test`

# Open Command Palette (Ctrl+Shift+P) and search for "Tasks: Run Task"

- "Locust: Light Load Test"
- "Locust: Medium Load Test"
- "Locust: Heavy Load Test"

## Test Markers

Tests use pytest markers for organization:

- `@pytest.mark.unit`: Fast unit tests with mocked dependencies
- `@pytest.mark.integration`: Integration tests with real database and mocked external services
- `@pytest.mark.e2e`: End-to-end tests with full infrastructure (Celery, Redis, LLM providers)

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
