# Stories Router Tests

This directory contains tests specifically for the stories router functionality (`app/routers/stories.py`). These tests focus on story management features and API endpoints.

## Test Files

### test_unit.py

Unit tests for story-related business logic and validation.

**What it tests:**

- Story data validation (StoryCreate, StoryUpdate schemas)
- Business logic helpers (slug generation, excerpt creation, word counting)
- Story filtering and search logic
- Data normalization (title, genre, author formatting)
- Reading time estimation
- Content validation rules

**Key test classes:**

- `TestStoryValidation`: Schema validation and data integrity
- `TestStoryBusinessLogic`: Core business rules and transformations
- `TestStoryHelpers`: Utility functions (slugs, excerpts, word counts)
- `TestStoryFiltering`: Search and filter logic testing

### test_integration.py

Integration tests for the complete stories API endpoints.

**What it tests:**

- Full CRUD operations via HTTP endpoints
- API request/response handling
- Database persistence and retrieval
- Error handling and status codes
- Query parameters (pagination, filtering)
- Publishing/unpublishing workflows

**Key test classes:**

- `TestStoriesAPI`: Comprehensive API endpoint testing
  - Story creation with validation
  - Listing with pagination and filters
  - Retrieval by ID
  - Updates and partial updates
  - Deletion
  - Publishing state management

## Test Structure Philosophy

Stories tests follow the **router-based organization** principle:

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
