# Stories Router Tests

This directory contains comprehensive tests for the stories router functionality (`app/routers/stories.py`), covering both synchronous and asynchronous (Celery-based) story operations.

## 🏗️ Architecture Overview

The stories system supports:

- **Synchronous Operations**: Basic CRUD operations (create, read, update, delete)
- **Asynchronous Operations**: LLM-powered story generation, analysis, and improvement via Celery
- **Publishing Workflow**: Draft → Published state management
- **Content Management**: Metadata handling, validation, search, and filtering

## 📁 Test Structure

```
tests/stories/
├── test_unit.py                  # Unit tests for business logic (16 tests)
├── test_integration.py           # Legacy sync API testing (18 tests, deprecated)
├── test_integration_async.py     # 🆕 Async API tests with mocked TaskService (~15 tests)
├── test_integration_celery.py    # 🆕 Real Celery integration tests (~10 tests)
└── README.md                    # This documentation
```

## 🧪 Test Categories

### 1. Unit Tests (`test_unit.py`) - Business Logic

**Purpose**: Test story business logic and validation with no external dependencies

**Key Test Areas**:

- Story data validation (StoryCreate, StoryUpdate schemas)
- Business logic helpers (slug generation, excerpt creation, word counting)
- Story filtering and search logic
- Data normalization (title, genre, author formatting)
- Reading time estimation and content validation rules

**Test Classes**:

- `TestStoryValidation`: Schema validation and data integrity
- `TestStoryBusinessLogic`: Core business rules and transformations
- `TestStoryHelpers`: Utility functions (slugs, excerpts, word counts)
- `TestStoryFiltering`: Search and filter logic testing

**Execution Time**: ~0.35 seconds | **Dependencies**: None

### 2. Async Integration Tests (`test_integration_async.py`) - 🆕 Modern Approach

**Purpose**: Test async story operations with mocked TaskService

**API Endpoints Tested**:

- `POST /api/v1/stories/generate` - Async story generation with LLM
- `POST /api/v1/stories/{id}/analyze` - Story analysis and metadata extraction
- `POST /api/v1/stories/{id}/improve` - Story improvement suggestions
- Standard CRUD operations with async patterns

**Test Patterns**:

```python
async def test_async_story_generation(async_client, mock_task_service):
    mock_task_service.process_task.return_value = TaskResponse(
        task_id="story_gen_123",
        status=TaskStatus.PENDING,
        result=None
    )

    response = await async_client.post("/api/v1/stories/generate", json={
        "prompt": "A story about async testing",
        "genre": "Technology",
        "target_length": "short"
    })

    assert response.status_code == 202
    assert response.json()["task_id"] == "story_gen_123"
    assert response.json()["status"] == "PENDING"
```

**Test Classes**:

- `TestAsyncStoryGeneration`: LLM-powered story creation
- `TestAsyncStoryAnalysis`: Content analysis and metadata extraction
- `TestAsyncStoryImprovement`: Enhancement suggestions and optimization

**Execution Time**: ~1-2 seconds | **Dependencies**: Mocked TaskService

### 3. Celery Integration Tests (`test_integration_celery.py`) - 🆕 End-to-End

**Purpose**: Full async workflow testing with real Celery workers and LLM integration

**Test Marker**: `@pytest.mark.celery_integration`

**Infrastructure Requirements**:

```bash
# Start Celery infrastructure
./celery-setup.sh start    # Redis broker
./celery-setup.sh worker   # Celery worker

# LLM API keys for real story generation
export OPENAI_API_KEY="your-openai-key"
```

**Real-World Scenarios**:

```python
@pytest.mark.celery_integration
async def test_real_story_generation_workflow():
    # Create a real async story generation task
    response = await async_client.post("/api/v1/stories/generate", json={
        "prompt": "A tale of microservices and async processing",
        "genre": "Science Fiction",
        "target_length": "medium"
    })

    task_id = response.json()["task_id"]

    # Poll for real Celery task completion
    for _ in range(120):  # Max 2 minutes for story generation
        status = await async_client.get(f"/api/v1/tasks/{task_id}")
        task_status = status.json()["status"]

        if task_status in ["SUCCESS", "FAILURE"]:
            break
        await asyncio.sleep(1)

    # Verify real story was generated and persisted
    final_result = await async_client.get(f"/api/v1/tasks/{task_id}")
    assert final_result.json()["status"] == "SUCCESS"

    story_data = final_result.json()["result"]
    assert len(story_data["story_text"]) > 100
    assert story_data["genre"] == "Science Fiction"

    # Verify story was saved to database
    story_response = await async_client.get(f"/api/v1/stories/{story_data['story_id']}")
    assert story_response.status_code == 200
```

**Test Classes**:

- `TestRealStoryGeneration`: End-to-end story creation with LLM
- `TestRealStoryAnalysis`: Complete analysis workflow
- `TestAsyncWorkflowIntegration`: Multi-step story processing pipelines

**Execution Time**: ~3-8 minutes | **Dependencies**: Celery + Redis + LLM APIs

## 🚀 Running Stories Tests

### Fast Development (Unit + Mocked Integration)

```bash
# Unit tests only (16 tests, ~0.35 seconds)
poetry run pytest tests/stories/test_unit.py -v

# Async tests with mocked TaskService (~15 tests, ~1-2 seconds)
poetry run pytest tests/stories/test_integration_async.py -v

# All fast tests (~31 tests, ~2-3 seconds)
poetry run pytest tests/stories/ -m "not celery_integration" -v
```

### Legacy Testing (Backward Compatibility)

```bash
# Legacy sync integration tests (~18 tests, ~1-2 seconds)
poetry run pytest tests/stories/test_integration.py -v
```

### Celery Integration Testing (Real Infrastructure)

```bash
# Start Celery infrastructure
./celery-setup.sh start
./celery-setup.sh worker

# Set LLM API keys
export OPENAI_API_KEY="your-openai-key"

# Real async story processing (~10 tests, ~3-8 minutes)
poetry run pytest tests/stories/test_integration_celery.py -v -m celery_integration

# All story tests including full integration (~59 tests, ~10 minutes)
poetry run pytest tests/stories/ -v
```

## 📊 Test Metrics Summary

| Test Category      | File                         | Tests   | Time     | Dependencies       |
| ------------------ | ---------------------------- | ------- | -------- | ------------------ |
| Unit Tests         | `test_unit.py`               | 16      | ~0.35s   | None               |
| Legacy Integration | `test_integration.py`        | 18      | ~1-2s    | Database           |
| Async Integration  | `test_integration_async.py`  | ~15     | ~1-2s    | Mocked TaskService |
| Celery Integration | `test_integration_celery.py` | ~10     | ~8m      | Celery + LLM APIs  |
| **Total**          | **All Files**                | **~59** | **~10m** | **Mixed**          |

```
app/routers/stories.py  ←→  tests/stories/
├── API endpoints       ←→  test_integration.py
└── Business logic      ←→  test_unit.py
```

This ensures:

- **1:1 mapping** between router code and test organization
- **Clear separation** between unit (logic) and integration (API) concerns
- **Easy navigation** - developers know exactly where to find relevant tests

## API Coverage

### Endpoints Tested

- `POST /api/v1/stories/` - Create new story
- `GET /api/v1/stories/` - List stories with filtering
- `GET /api/v1/stories/{id}` - Get story by ID
- `PUT /api/v1/stories/{id}` - Update story
- `DELETE /api/v1/stories/{id}` - Delete story
- `POST /api/v1/stories/{id}/publish` - Publish story
- `POST /api/v1/stories/{id}/unpublish` - Unpublish story

### Query Parameters Tested

- `skip` and `limit` - Pagination
- `genre` - Filter by genre
- `author` - Filter by author (partial match)
- `published_only` - Show only published stories

## Running Stories Tests

```bash
# Run all stories tests
poetry run pytest tests/stories/ -v

# Run only unit tests (fast)
poetry run pytest tests/stories/test_unit.py -v

# Run only integration tests (API calls)
poetry run pytest tests/stories/test_integration.py -v

# Run with coverage for stories router
poetry run pytest tests/stories/ --cov=app.routers.stories --cov=app.schemas.story
```

## Test Data and Fixtures

Stories tests use both shared and local fixtures:

**From main conftest.py:**

- `temp_db`: Isolated database for each test
- `db_session`: Database session
- `client`: FastAPI test client

**From local conftest.py:**

- `sample_story_data`: Standard story test data
- `sample_stories_data`: Multiple stories for list/filter testing

## Database Testing

- **Isolation**: Each test uses a fresh SQLite database
- **Realistic data**: Tests use representative story content
- **Edge cases**: Tests cover validation limits and error conditions
- **Performance**: Fast execution suitable for TDD workflow

## Integration with Other Test Categories

Stories tests complement other test layers:

- **Shared tests** verify the underlying models and schemas work correctly
- **Stories tests** focus on router-specific logic and API behavior
- **E2E tests** verify complete user workflows involving stories + LLM
- **LLM tests** handle AI functionality that operates on stories

This layered approach ensures comprehensive coverage without duplication.
