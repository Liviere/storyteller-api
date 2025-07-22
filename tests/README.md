# Tests for Story Teller API

This directory contains comprehensive unit, integration, and end-to-end tests for the Story Teller API, modernized for **asynchronous task processing with Celery**. After Celery integration, the testing strategy has been completely rebuilt around async workflows and real infrastructure validation.

## 🏗️ Modern Test Architecture

### **Two-Tier Testing Strategy:**

#### **Tier 1: Unit/Mock Tests** (Fast Development)

- **Purpose**: Rapid feedback during development
- **Speed**: ~6 seconds for full fast suite (measured)
- **Method**: Mock Celery tasks and external services
- **Usage**: Continuous development, CI/CD pipelines

#### **Tier 2: Integration Tests** (Production Validation)

- **Purpose**: End-to-end validation with real infrastructure
- **Speed**: 2-3 minutes (includes real LLM API calls)
- **Method**: Real Redis + Celery workers + database
- **Usage**: Pre-deployment validation, regression testing

## 📁 Test Structure

```
tests/
├── __init__.py                      # Package marker
├── conftest.py                      # Core test configuration and fixtures
├── README.md                        # This file
│
├── shared/                          # 🧱 Foundation Components
│   ├── __init__.py
│   ├── test_models.py               # SQLAlchemy model tests (6 tests)
│   ├── test_schemas.py              # Pydantic schema tests (10 tests)
│   ├── test_main.py                 # FastAPI application tests (5 tests)
│   └── README.md                    # Shared components documentation
│
├── tasks/ 🆕                        # ⚡ Celery Task Management
│   ├── __init__.py
│   ├── conftest.py                  # Celery fixtures and mock services
│   ├── test_task_service.py         # TaskService unit tests (mocked)
│   ├── test_tasks_api.py            # Task API endpoints (/api/v1/tasks/*)
│   └── README.md                    # Task testing documentation
│
├── stories/                         # 📚 Story Management
│   ├── __init__.py
│   ├── conftest.py                  # Stories-specific fixtures
│   ├── test_unit.py                 # Business logic validation (16 tests)
│   ├── test_integration.py          # Legacy sync API tests (18 tests)
│   ├── test_integration_async.py 🆕  # Async API tests (mocked tasks)
│   ├── test_integration_celery.py 🆕 # Real Celery integration tests
│   └── README.md                    # Stories testing documentation
│
├── llm/ 🔄                          # 🤖 AI/LLM Functionality (Modernized)
│   ├── __init__.py
│   ├── conftest.py                  # LLM fixtures and configurations
│   ├── test_unit.py                 # LLM service unit tests (25 tests)
│   ├── test_integration.py          # Direct LLM API integration (7 tests)
│   ├── test_llm_api.py              # Sync endpoints (health, models, stats)
│   ├── test_llm_api_async.py 🆕      # Async endpoints returning TaskResponse
│   ├── test_integration_celery.py 🆕 # Real LLM + Celery integration
│   └── README.md                    # LLM testing documentation
│
└── e2e/                             # 🌐 End-to-End Workflows
    ├── __init__.py
    ├── conftest.py                  # E2E test fixtures
    ├── test_workflows.py.deprecated # Legacy sync workflow tests
    ├── test_workflows_async.py 🆕    # Modern async workflow tests
    ├── locustfile.py                # Performance testing scenarios
    ├── config.py                    # Performance test configuration
    └── README.md                    # E2E testing documentation
```

## Test Categories

### Shared Component Tests (`tests/shared/`)

**Purpose**: Tests for core components used across multiple routers

- **test_models.py** (6 tests): SQLAlchemy model validation, relationships, and database operations
- **test_schemas.py** (10 tests): Pydantic schema validation, serialization, and field constraints
- **test_main.py** (5 tests): Main application endpoints, CORS, and documentation

### 🆕 Task Management Tests (`tests/tasks/`)

**Purpose**: Comprehensive testing of Celery task processing and TaskService

- **test_task_service.py** (17 tests): TaskService unit tests with mocked Celery
- **test_tasks_api.py** (13 tests): Task API endpoints (/api/v1/tasks/\*) testing

### Stories Router Tests (`tests/stories/`)

**Purpose**: Complete testing of story management functionality

- **test_unit.py** (16 tests): Story validation, business logic, filtering, and helper functions
- **test_integration.py** (18 tests): Legacy sync API endpoint testing (deprecated)
- **test_integration_async.py** 🆕 (~15 tests): Async API tests with mocked TaskService
- **test_integration_celery.py** 🆕 (~10 tests): Real Celery integration for story operations

### LLM Functionality Tests (`tests/llm/`)

**Purpose**: Comprehensive testing of AI/LLM integration (modernized for async)

- **test_unit.py** (25 tests): Configuration validation, service initialization, mocked LLM operations
- **test_integration.py** (7 tests): Real API calls to configured LLM providers (requires API keys)
- **test_llm_api.py** (~10 tests): Sync endpoints (health, models, stats) with mocked services
- **test_llm_api_async.py** 🆕 (~15 tests): Async endpoints returning TaskResponse
- **test_integration_celery.py** 🆕 (~8 tests): Real LLM + Celery integration tests

### End-to-End Tests (`tests/e2e/`)

**Purpose**: Complete user workflows and performance testing (modernized for async)

- **test_workflows.py.deprecated**: Legacy sync workflow tests (31 tests, deprecated)
- **test_workflows_async.py** 🆕 (~8 tests): Modern async workflow tests with task polling
- **locustfile.py**: Performance testing scenarios (light, medium, heavy load testing)
- **config.py**: Performance test configuration and scenarios

### Testing Strategies

This repository employs a **two-tier testing strategy** optimized for development speed and CI/CD efficiency:

#### 🚀 **Tier 1: Fast Tests** (Mocked Dependencies)

- **Purpose**: Rapid development feedback (~6 seconds execution)
- **Strategy**: Mock external services (TaskService, LLM APIs, Celery workers)
- **Coverage**: Business logic, API schemas, database models, error handling
- **Use Case**: Pre-commit validation, TDD development, CI/CD quick feedback

**Key Mocking Patterns**:

```python
# TaskService mocking for async endpoints
@patch('app.services.task_service.TaskService.process_task')
def test_async_endpoint(mock_process):
    mock_process.return_value = TaskResponse(
        task_id="mock_123",
        status=TaskStatus.PENDING,
        result=None
    )
    # Test endpoint logic without Celery dependency
```

#### 🧪 **Tier 2: Integration Tests** (Real Infrastructure)

- **Purpose**: End-to-end validation with real services (2-5 minutes execution)
- **Strategy**: Real Celery workers, Redis broker, LLM providers, database transactions
- **Coverage**: Task processing pipelines, async workflows, external API integration
- **Use Case**: Pre-deployment validation, production readiness verification

**Infrastructure Requirements**:

```bash
# Start complete integration environment
./celery-setup.sh start    # Redis broker
./celery-setup.sh worker   # Celery worker process
# Tests can now use real TaskService functionality
```

### Test Execution Framework

#### Test Markers for Selective Execution

Our test suite uses pytest markers for granular test selection:

- `@pytest.mark.llm_integration`: Tests requiring real LLM API calls (OpenAI, DeepInfra)
- `@pytest.mark.celery_integration`: Tests requiring real Celery/Redis infrastructure
- `@pytest.mark.slow`: Tests with longer execution times (>10 seconds)

#### Common Test Execution Patterns

```bash
# 🚀 Fast development cycle (Tier 1) - ~6 seconds (measured)
poetry run pytest -m "not slow and not llm_integration and not celery_integration" -v

# 🧪 Full Celery integration testing (Tier 2) - ~30-60 seconds
poetry run pytest -m "celery_integration" -v

# 🔬 Real LLM integration testing (requires API keys) - ~60-120 seconds
poetry run pytest -m "llm_integration" -v

# ⚡ Unit tests only (fastest) - ~2 seconds
poetry run pytest tests/shared/ tests/stories/test_unit.py tests/llm/test_unit.py tests/tasks/test_task_service.py -v

# 🎯 Component-specific testing
poetry run pytest tests/tasks/ -v              # Task management tests (~2s)
poetry run pytest tests/stories/test_integration_async.py -v  # Async story tests
poetry run pytest tests/e2e/test_workflows_async.py -v       # E2E workflows
```

#### Test Environment Configuration

```bash
# Development environment (SQLite, mocked services)
poetry run pytest

# Production-like testing (MySQL, real services)
TEST_DATABASE_URL="mysql+mysqlconnector://user:pass@localhost:3307/test_db" \
poetry run pytest -m "celery_integration"
```

## Running Tests (Legacy Commands)

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
