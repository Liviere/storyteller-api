# Task Management Testing

This directory contains comprehensive tests for the Celery-based task management system introduced in the Celery integration feature. The task system enables asynchronous processing of LLM operat## 📊 Test Metrics (Based on Real Execution Times)

| Test Category     | Count  | Execution Time | Dependencies        |
| ----------------- | ------ | -------------- | ------------------- |
| Unit Tests        | 17     | **0.37s**      | Mocked Celery       |
| API Tests         | 13     | **1.62s**      | Mocked TaskService  |
| Integration Tests | 13     | **Skipped\***  | Real Celery + Redis |
| **Fast Tests**    | **30** | **~2s**        | Mocked only         |
| **All Tests**     | **43** | **~30-60s**    | Mixed               |

_Integration tests require `--integration` flag or `@pytest.mark.celery_integration` marker to run_

**Note**: Times measured on actual test execution (2025-01-21). Fast tests complete in under 2 seconds, making them perfect for rapid development cycles.y generation workflows.

## 🏗️ Architecture Overview

The task system consists of:

- **TaskService**: Core service managing task lifecycle and Celery integration
- **Task Router** (`/api/v1/tasks/*`): REST API for task operations
- **Celery Workers**: Background processors for async task execution
- **TaskResponse Schema**: Standardized async operation responses

## 📁 Test Structure

```
tests/tasks/
├── test_task_service.py        # TaskService unit tests with mocked Celery
├── test_tasks_api.py          # Task API endpoints testing
├── test_celery_integration.py # Real Celery worker integration tests
└── README.md                  # This documentation
```

## 🧪 Test Categories

### Unit Tests (`test_task_service.py`)

**Purpose**: Test TaskService business logic with mocked Celery dependencies

**Key Test Areas**:

- Task creation and validation
- Status transitions and error handling
- Result processing and serialization
- Task cleanup and timeout management

**Mocking Strategy**:

```python
@patch('app.celery_app.celery.delay')
def test_task_creation(mock_delay):
    mock_delay.return_value.id = "test_task_123"
    mock_delay.return_value.status = "PENDING"

    response = task_service.process_task("generate_story", {"prompt": "test"})
    assert response.task_id == "test_task_123"
    assert response.status == TaskStatus.PENDING
```

**Test Coverage** (~15 tests):

- ✅ Task creation with various input types
- ✅ Status polling and result retrieval
- ✅ Error handling for invalid inputs
- ✅ Task cancellation and cleanup
- ✅ Timeout and retry mechanisms

### API Integration Tests (`test_tasks_api.py`)

**Purpose**: Test task management endpoints with mocked TaskService

**API Endpoints Tested**:

- `POST /api/v1/tasks/` - Create new task
- `GET /api/v1/tasks/{task_id}` - Get task status
- `GET /api/v1/tasks/` - List tasks (with filtering)
- `DELETE /api/v1/tasks/{task_id}` - Cancel task

**Test Patterns**:

```python
async def test_create_task_endpoint(async_client, mock_task_service):
    mock_task_service.process_task.return_value = TaskResponse(
        task_id="api_test_123",
        status=TaskStatus.PENDING,
        result=None
    )

    response = await async_client.post("/api/v1/tasks/", json={
        "task_type": "generate_story",
        "parameters": {"prompt": "Test story"}
    })

    assert response.status_code == 201
    assert response.json()["task_id"] == "api_test_123"
```

**Test Coverage** (~20 tests):

- ✅ Task creation with validation
- ✅ Status polling with different task states
- ✅ Error responses (404, 400, 422)
- ✅ Task listing with filtering
- ✅ Task cancellation flows

### Celery Integration Tests (`test_celery_integration.py`)

**Purpose**: End-to-end testing with real Celery workers and Redis broker

**Infrastructure Requirements**:

```bash
# Required before running these tests
./celery-setup.sh start    # Start Redis broker
./celery-setup.sh worker   # Start Celery worker in background
```

**Test Marker**: `@pytest.mark.celery_integration`

**Real-World Scenarios**:

```python
@pytest.mark.celery_integration
async def test_real_story_generation_task():
    # Create real task that will be processed by Celery worker
    response = await async_client.post("/api/v1/tasks/", json={
        "task_type": "generate_story",
        "parameters": {"prompt": "A story about testing"}
    })

    task_id = response.json()["task_id"]

    # Poll for completion (real Celery processing)
    for _ in range(30):  # Max 30 seconds wait
        status_response = await async_client.get(f"/api/v1/tasks/{task_id}")
        if status_response.json()["status"] in ["SUCCESS", "FAILURE"]:
            break
        await asyncio.sleep(1)

    # Verify real task completion
    final_status = await async_client.get(f"/api/v1/tasks/{task_id}")
    assert final_status.json()["status"] == "SUCCESS"
    assert "story_text" in final_status.json()["result"]
```

**Test Coverage** (~10 tests):

- ✅ Real story generation with LLM
- ✅ Task failure and error propagation
- ✅ Task timeout and retry scenarios
- ✅ Worker availability validation
- ✅ Task result persistence

## 🚀 Running Task Tests

### Fast Development (Mocked Dependencies)

```bash
# Unit tests only (17 tests, ~0.4 seconds)
poetry run pytest tests/tasks/test_task_service.py -v

# API tests with mocked TaskService (13 tests, ~1.6 seconds)
poetry run pytest tests/tasks/test_tasks_api.py -v

# Both fast test suites (30 tests, ~2 seconds)
poetry run pytest tests/tasks/ -m "not celery_integration" -v
```

### Integration Testing (Real Infrastructure)

```bash
# Start required infrastructure
./celery-setup.sh start
./celery-setup.sh worker

# Run Celery integration tests (13 tests, requires --integration flag)
poetry run pytest tests/tasks/test_celery_integration.py -v --integration

# Alternative: use celery_integration marker
poetry run pytest tests/tasks/ -v -m celery_integration

# All task tests including integration (43 tests, ~30-60 seconds)
poetry run pytest tests/tasks/ -v --integration
```

### Debug and Development

```bash
# Run single test with detailed output
poetry run pytest tests/tasks/test_task_service.py::test_specific_function -v -s

# Check Celery worker status
./celery-setup.sh status

# View worker logs during testing
./celery-setup.sh logs
```

## 🔧 Test Configuration

### Environment Variables

Task tests respect these environment settings:

```bash
# Redis connection for Celery integration tests
CELERY_BROKER_URL="redis://localhost:6379/0"
CELERY_RESULT_BACKEND="redis://localhost:6379/0"

# Task timeouts for integration tests
TASK_TIMEOUT_SECONDS=30
TASK_POLL_INTERVAL=1
```

### Pytest Markers

- `@pytest.mark.celery_integration`: Requires real Celery/Redis infrastructure
- `@pytest.mark.slow`: Tests with longer execution times (>10 seconds)
- `@pytest.mark.asyncio`: Async test functions

### Mock Configuration

Fast tests use these key mocking patterns:

```python
# Mock Celery task delay
@patch('app.celery_app.celery.delay')

# Mock TaskService for API tests
@pytest.fixture
def mock_task_service():
    with patch('app.services.task_service.TaskService') as mock:
        yield mock.return_value
```

## 📊 Test Metrics (Based on Real Execution Times)

| Test Category     | Count  | Execution Time | Dependencies        |
| ----------------- | ------ | -------------- | ------------------- |
| Unit Tests        | 17     | **0.37s**      | Mocked Celery       |
| API Tests         | 13     | **1.62s**      | Mocked TaskService  |
| Integration Tests | 13     | **Skipped\***  | Real Celery + Redis |
| **Fast Tests**    | **30** | **~2s**        | Mocked only         |
| **All Tests**     | **43** | **~30-60s**    | Mixed               |

_Integration tests require `--integration` flag to run (see Running Tests section)_

**Note**: Times measured on actual test execution (2025-01-21). Fast tests (mocked) complete in under 10 seconds, making them ideal for rapid development cycles.

## 🛠️ Development Workflow

### Adding New Task Types

1. **Add Task Function**: Define in `app/celery_app/tasks/`
2. **Add Unit Tests**: Test task logic with mocks in `test_task_service.py`
3. **Add API Tests**: Test endpoint in `test_tasks_api.py`
4. **Add Integration Test**: Test end-to-end flow in `test_celery_integration.py`

### Test-Driven Development

```bash
# 1. Write failing test
poetry run pytest tests/tasks/test_task_service.py::test_new_feature -v

# 2. Implement feature
# ... code changes ...

# 3. Verify test passes
poetry run pytest tests/tasks/test_task_service.py::test_new_feature -v

# 4. Run full suite to ensure no regressions
poetry run pytest tests/tasks/ -v
```
