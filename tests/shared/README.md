# Shared Components Tests

This directory contains tests for core components that are used throughout the application. These are fundamental building blocks that other modules depend on.

## Test Files

### test_models.py

Tests for SQLAlchemy models - the database layer of the application.

**What it tests:**

- Story model creation and validation
- Database field constraints and defaults
- Model relationships and behavior
- String representation (`__repr__`)
- Required vs optional fields
- Timestamp handling (created_at, updated_at)

**Key test classes:**

- `TestStoryModel`: Comprehensive tests for the Story database model

### test_schemas.py

Tests for Pydantic schemas - the API data validation layer.

**What it tests:**

- Input validation for API requests
- Data serialization and deserialization
- Field length limits and constraints
- Optional field handling
- Schema inheritance (Base → Create → Update → Response)
- Error handling for invalid data

**Key test classes:**

- `TestStorySchemas`: Tests for all story-related schemas (StoryBase, StoryCreate, StoryUpdate, StoryResponse)

### test_main.py

Tests for the main FastAPI application setup and core endpoints.

**What it tests:**

- Application startup and configuration
- Core endpoints (root, health check)
- CORS configuration
- API documentation endpoints (Swagger UI, ReDoc)
- Error handling for invalid routes

**Key test classes:**

- `TestMainApp`: Tests for main application behavior

## Purpose in Test Architecture

**Shared components** represent the foundation layer that other test categories build upon:

```
┌─────────────────────────────────────────┐
│              E2E Tests                  │  ← Complete user workflows
│        (stories + LLM workflows)       │
├─────────────────────────────────────────┤
│  Stories Tests    │    LLM Tests        │  ← Router-specific functionality
│  (unit + integration) │ (unit + integration) │
├─────────────────────────────────────────┤
│           Shared Components             │  ← Core building blocks (THIS FOLDER)
│     (models, schemas, main app)         │
└─────────────────────────────────────────┘
```

## Running Shared Tests

```bash
# Run all shared component tests
poetry run pytest tests/shared/ -v

# Run specific test file
poetry run pytest tests/shared/test_models.py -v
poetry run pytest tests/shared/test_schemas.py -v
poetry run pytest tests/shared/test_main.py -v

# Run with coverage for shared components only
poetry run pytest tests/shared/ --cov=app.models --cov=app.schemas --cov=app.main
```

## Test Data and Fixtures

Shared tests use fixtures from the main `conftest.py`:

- `temp_db`: Temporary SQLite database for isolation
- `db_session`: Database session for each test
- `client`: FastAPI test client
- `sample_story_data`: Reusable test data for stories

## Coverage Goals

These tests aim for high coverage of core components:

- **Models**: 100% coverage of model fields, methods, and constraints
- **Schemas**: 100% coverage of validation logic and edge cases
- **Main App**: 95%+ coverage of application setup and core endpoints

## Dependencies

Shared component tests have minimal dependencies and run quickly:

- SQLAlchemy for database models
- Pydantic for schema validation
- FastAPI TestClient for application testing
- Pytest fixtures for test isolation

These tests form the stable foundation that allows other test categories to focus on higher-level functionality without retesting basic components.
