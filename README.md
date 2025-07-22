# Story Teller API

REST API for managing stories built with FastAPI and Poetry.

## Features

### Core Story Management

- Create, read, update, and delete stories
- Filter stories by genre, author, and publication status
- Publish/unpublish stories

### 🤖 AI-Powered Features

- **AI-powered story generation with LLM integration**
- **Story analysis (sentiment, genre classification, comprehensive analysis)**
- **Story summarization with customizable length and focus**
- **Story improvement (grammar, style, general quality enhancement)**
- **Support for multiple LLM providers (OpenAI, DeepInfra, Any OpenAI-compatible API)**
- **LLM usage statistics and health monitoring**

### ⚡ Asynchronous Processing

- **Asynchronous task processing with Celery and Redis**
- **Background task management for time-consuming operations**
- **Task status monitoring and result retrieval**
- **Non-blocking API responses with task-based workflows**
- **Real-time task progress tracking**

### 💾 Database & Infrastructure

- **MySQL database with SQLAlchemy ORM (with Docker support)**
- **SQLite fallback for development**
- **Redis message broker for distributed task processing**
- **Database transaction isolation and consistency**

### 🔧 Development & Operations

- **Error monitoring and tracking with Sentry**
- **Docker and docker-compose for easy deployment**
- **Isolated test environment with dedicated MySQL instance**
- **Performance testing with Locust**
- Automatic API documentation with Swagger UI
- CORS support for frontend integration
- Modern dependency management with Poetry
- Development tools: Black, isort, flake8, mypy, pytest

### 🧪 Testing & Quality Assurance

- **Comprehensive async testing with Celery integration**
- **Two-tier testing strategy (unit mocks + integration tests)**
- **Real worker testing with Redis and Celery infrastructure**
- **Production-grade end-to-end testing**
- **VS Code task automation for development workflows**

## Quick Start

### Option 1: Docker Setup (Recommended)

#### Prerequisites

- Docker and Docker Compose
- Git

#### Installation with Docker

1. Clone or navigate to the project directory:

```bash
cd story-teller  # or your project directory name
```

2. Set up environment variables:

```bash
cp .env.example .env
# Edit .env file if needed
```

3. Start all services:

```bash
./docker-setup.sh start
```

This will start:

- MySQL database on port 3306
- FastAPI application on port 8080
- phpMyAdmin on port 8081

For Celery task processing, also start Redis and Celery workers:

```bash
# Start Redis for Celery
./celery-setup.sh start

# Start Celery worker (in another terminal)
./celery-setup.sh worker

# Optional: Start Flower monitoring
./celery-setup.sh flower  # Available at http://localhost:5555
```

4. Access the application:

- API: http://localhost:8080
- API Documentation: http://localhost:8080/docs
- Database Admin: http://localhost:8081
- Task Monitoring (if Flower started): http://localhost:5555

#### Docker Commands

```bash
# Start services
./docker-setup.sh start

# Stop services
./docker-setup.sh stop

# View logs
./docker-setup.sh logs

# Connect to MySQL
./docker-setup.sh mysql

# Migrate data from SQLite (if you have existing data)
./docker-setup.sh migrate

# Clean up (removes all data!)
./docker-setup.sh clean

# Test environment (isolated MySQL for testing)
docker-compose -f docker-compose.test.yml up -d    # Start test database
docker-compose -f docker-compose.test.yml down -v  # Clean test environment

# Celery management
./celery-setup.sh start     # Start Redis
./celery-setup.sh stop      # Stop Redis
./celery-setup.sh worker    # Start Celery worker
./celery-setup.sh flower    # Start monitoring interface
./celery-setup.sh status    # Check system status
```

### Option 2: Local Development Setup

#### Prerequisites

- Python 3.11+
- Poetry (https://python-poetry.org/docs/#installation)
- MySQL (optional, defaults to SQLite)

#### Installation

1. Clone or navigate to the project directory:

```bash
cd story-teller  # or your project directory name
```

2. Install dependencies with Poetry:

```bash
poetry install
```

3. Set up environment variables (optional):

```bash
cp .env.example .env
# Edit .env with your preferred settings
```

4. Run the application:

```bash
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

The API will be available at:

- API: http://localhost:8080
- Interactive docs (Swagger UI): http://localhost:8080/docs
- Alternative docs (ReDoc): http://localhost:8080/redoc

## Poetry Commands

### Basic Commands

```bash
# Install all dependencies
poetry install

# Add a new dependency
poetry add package-name

# Add a development dependency
poetry add --group dev package-name

# Run the application
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8080

# Enter Poetry shell
poetry shell
```

## LLM Configuration

The application supports multiple LLM providers for AI-powered story generation and text processing.

### Quick LLM Setup

1. Copy the LLM configuration template:

```bash
cp llm_config.example.yaml llm_config.yaml
```

2. Edit `llm_config.yaml` with your preferred provider settings:

3. Set your API keys in environment variables (optional):

```bash
export OPENAI_API_KEY="your-api-key"
export DEEPINFRA_API_KEY="your-deepinfra-key"
```

### Supported LLM Providers

- **OpenAI** - GPT models (requires API key)
- **DeepInfra** - Hosted open-source models (requires API key)
- **Custom endpoints** - Any OpenAI-compatible API

### LLM API Endpoints

- **Health check**: `GET /api/v1/llm/health`
- **Generate story**: `POST /api/v1/llm/generate` _(async task)_
- **Analyze text**: `POST /api/v1/llm/analyze` _(async task)_
- **Summarize content**: `POST /api/v1/llm/summarize` _(async task)_
- **Improve story**: `POST /api/v1/llm/improve` _(async task)_
- **Available models**: `GET /api/v1/llm/models`
- **Usage statistics**: `GET /api/v1/llm/stats`

### Testing LLM Integration

Test the LLM functionality without API keys:

```bash
python test_llm.py
```

### Development Tools

```bash
# Format code with Black
poetry run black .

# Sort imports with isort
poetry run isort .

# Lint code with flake8
poetry run flake8 .

# Type checking with mypy
poetry run mypy .

# Run tests
poetry run pytest

```

## Testing

The project features a **modern, production-grade testing architecture** designed around **asynchronous task processing with Celery**. After Celery integration, the testing strategy has been completely modernized to handle async workflows, real infrastructure integration, and comprehensive end-to-end validation.

### 🏗️ Two-Tier Testing Architecture

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

### 📁 Modern Test Structure

```
tests/
├── conftest.py                      # Core test configuration and fixtures
│
├── shared/                          # 🧱 Foundation Components
│   ├── test_models.py               # SQLAlchemy model validation
│   ├── test_schemas.py              # Pydantic schema testing
│   └── test_main.py                 # FastAPI application tests
│
├── tasks/ 🆕                        # ⚡ Celery Task Management
│   ├── conftest.py                  # Celery fixtures and mock services
│   ├── test_task_service.py         # TaskService unit tests (mocked)
│   └── test_tasks_api.py            # Task API endpoints (/api/v1/tasks/*)
│
├── stories/                         # 📚 Story Management
│   ├── test_unit.py                 # Business logic validation
│   ├── test_integration.py          # Legacy sync API tests
│   ├── test_integration_async.py 🆕  # Async API tests (mocked tasks)
│   ├── test_integration_celery.py 🆕 # Real Celery integration tests
│   └── conftest.py                  # Story-specific fixtures
│
├── llm/ 🔄                          # 🤖 AI/LLM Functionality (Modernized)
│   ├── test_unit.py                 # LLM service unit tests
│   ├── test_integration.py          # Direct LLM API integration
│   ├── test_llm_api.py              # Sync endpoints (health, models, stats)
│   ├── test_llm_api_async.py 🆕      # Async endpoints returning TaskResponse
│   ├── test_integration_celery.py 🆕 # Real LLM + Celery integration
│   └── conftest.py                  # LLM fixtures and configurations
│
└── e2e/                             # 🌐 End-to-End Workflows
    ├── test_workflows.py.deprecated # Legacy sync workflow tests
    ├── test_workflows_async.py 🆕    # Modern async workflow tests
    ├── locustfile.py                # Performance testing scenarios
    └── conftest.py                  # E2E test fixtures
```

### 🚀 Running Tests

#### **Quick Development Tests**

```bash
# Fast tests only (excludes slow integration)
poetry run pytest -m "not slow and not llm_integration and not celery_integration" -v

# Unit tests with mocks (~6 seconds)
poetry run pytest tests/shared/ tests/tasks/test_task_service.py tests/stories/test_unit.py -v
```

#### **Async API Tests**

```bash
# Test async TaskResponse endpoints
poetry run pytest tests/llm/test_llm_api_async.py tests/stories/test_integration_async.py -v

# Test TaskService and Task API
poetry run pytest tests/tasks/test_task_service.py tests/tasks/test_tasks_api.py -v
```

#### **Celery Integration Tests** (Requires Infrastructure)

```bash
# 1. Start infrastructure
./celery-setup.sh start    # Redis
./celery-setup.sh worker   # Celery worker

# 2. Run real integration tests
poetry run pytest -m celery_integration -v

# 3. Specific integration suites
poetry run pytest tests/stories/test_integration_celery.py -v    # Stories + Celery
poetry run pytest tests/llm/test_integration_celery.py -v       # LLM + Celery
poetry run pytest tests/tasks/ -v                              # Task management
```

#### **Coverage and Comprehensive Testing**

```bash
# Full test suite
poetry run pytest

# With coverage report
poetry run pytest --cov=. --cov-report=html:reports/coverage
open reports/coverage/index.html

# All tests without Celery integration
poetry run pytest -m "not celery_integration" -v
```

### 🏷️ Test Markers and Categories

#### **Primary Markers**

- `celery_integration`: Requires Redis + Celery worker infrastructure
- `celery_mock`: Uses mocked Celery components (fast)
- `llm_integration`: Requires real LLM API keys
- `slow`: Long-running tests (> 30 seconds)
- `e2e`: Complete workflow validation

#### **Test Categories by Speed**

```bash
# ⚡ Lightning Fast (< 5s) - Daily development
poetry run pytest tests/shared/ tests/tasks/test_task_service.py -v

# 🏃 Fast (< 30s) - Pre-commit validation
poetry run pytest -m "not slow and not celery_integration" -v

# 🐢 Slow (30-90s) - Pre-deployment validation
poetry run pytest -m celery_integration -v
```

### 🔧 VS Code Integration

#### **Essential Development Tasks**

- `Poetry: Run Fast Tests Only` - Daily development workflow
- `Poetry: Run Task Service Tests` - TaskService validation
- `Poetry: Run Async LLM API Tests` - Async endpoint testing

#### **Integration Testing Tasks**

- `Poetry: Run All Celery Integration Tests` - Full infrastructure testing
- `Poetry: Run Stories Celery Integration Tests` - Story workflow validation
- `Poetry: Run LLM Celery Integration Tests` - AI feature validation

#### **Specialized Testing Tasks**

- `Poetry: Run Tests Without Celery Integration` - Fast CI/CD pipeline
- `Poetry: Run All New Async Tests` - Modern async test suite

_Access via: `Ctrl+Shift+P` → "Tasks: Run Task"_

### 🔄 API Testing Strategy After Celery Integration

#### **Before Celery** (Legacy):

```python
# Synchronous API expectation - immediate result
response = client.post("/api/v1/llm/generate", json={
    "prompt": "A brave knight's adventure",
    "genre": "fantasy",
    "length": "short"
})
assert response.status_code == 200
data = response.json()
assert "story" in data  # Direct story content
assert len(data["story"]) > 100
assert "metadata" in data
```

#### **After Celery** (Modern E2E Testing):

```python
# Step 1: Submit async task
response = client.post("/api/v1/llm/generate", json={
    "prompt": "A brave knight's adventure",
    "genre": "fantasy",
    "length": "short"
})
assert response.status_code == 200
task_data = response.json()
assert "task_id" in task_data
assert task_data["status"] == "PENDING"
task_id = task_data["task_id"]

# Step 2: Poll for task completion (integration tests)
import time
max_wait = 60  # seconds
start_time = time.time()

while time.time() - start_time < max_wait:
    task_response = client.get(f"/api/v1/tasks/{task_id}")
    assert task_response.status_code == 200
    task_status = task_response.json()

    if task_status["status"] == "SUCCESS":
        # Step 3: Verify the actual generated story
        result = task_status["result"]
        assert "story" in result
        assert len(result["story"]) > 100  # Generated content exists
        assert "knight" in result["story"].lower()  # Prompt reflected
        assert "metadata" in result
        assert result["metadata"]["word_count"] > 0
        break
    elif task_status["status"] == "FAILURE":
        pytest.fail(f"Task failed: {task_status.get('error', 'Unknown error')}")

    time.sleep(2)  # Wait before next poll
else:
    pytest.fail(f"Task {task_id} did not complete within {max_wait} seconds")
```

### 🏭 Infrastructure Requirements

#### **Unit/Mock Tests**: None

- Uses temporary SQLite database
- Mocks all external services
- No Redis or Celery required

#### **Integration Tests**: Full Infrastructure

```bash
# Required services
./celery-setup.sh start    # Redis (port 6379)
./celery-setup.sh worker   # Celery worker process
# Optional: ./celery-setup.sh flower  # Monitoring UI (port 5555)

# Database options
# Option 1: SQLite (default, automatic)
# Option 2: MySQL via Docker
./docker-setup.sh start    # MySQL (port 3306)
```

### 📊 Test Performance Metrics

| Test Category          | Count | Duration | Infrastructure |
| ---------------------- | ----- | -------- | -------------- |
| **Unit Tests**         | ~40   | < 5s     | None           |
| **Mock Async Tests**   | ~25   | < 15s    | None           |
| **Celery Integration** | ~15   | 30-90s   | Redis + Worker |
| **LLM Integration**    | ~8    | 60-120s  | + LLM API      |
| **Legacy Tests**       | ~30   | -        | (Deprecated)   |

### 🎯 Testing Best Practices

#### **Daily Development**

1. Run fast tests continuously: `poetry run pytest -m "not slow" -v`
2. Use VS Code tasks for common scenarios
3. Focus on unit tests for rapid iteration

#### **Pre-Commit Validation**

1. Run all non-integration tests: `poetry run pytest -m "not celery_integration" -v`
2. Verify code quality: `poetry run black . && poetry run isort . && poetry run flake8`
3. Check type safety: `poetry run mypy .`

#### **Pre-Deployment Validation**

1. Start full infrastructure: Redis + Celery + MySQL
2. Run complete integration suite: `poetry run pytest -v`
3. Verify real LLM integration with API keys
4. Run performance tests: Locust scenarios

#### **Continuous Integration**

- **Pipeline 1**: Fast tests (< 5 min) - on every commit
- **Pipeline 2**: Integration tests (< 15 min) - on pull requests
- **Pipeline 3**: Full validation (< 30 min) - on main branch

### 🔍 Debugging Integration Tests

#### **Common Issues and Solutions**

**Redis Connection Errors:**

```bash
# Check Redis status
redis-cli ping
# Start if needed
./celery-setup.sh start
```

**Celery Worker Not Processing:**

```bash
# Check worker status
./celery-setup.sh status
# Start worker
./celery-setup.sh worker
# Monitor tasks
./celery-setup.sh flower  # Web UI at localhost:5555
```

**Database Transaction Issues:**

```bash
# Integration tests use real database
# Ensure proper fixture usage: real_client, real_db
# Check database synchronization between test and worker
```

**LLM API Failures:**

```bash
# Set API keys for integration tests
export OPENAI_API_KEY="your-key"
export DEEPINFRA_API_KEY="your-key"
# Tests automatically skip if keys missing
```

This modern testing architecture ensures **production-grade reliability** while maintaining **developer productivity** through intelligent test categorization and infrastructure automation.

### LLM Testing

LLM tests are organized into categories:

- **Unit tests** (`tests/llm/test_unit.py`): Fast tests with mocked LLM services
- **Integration tests** (`tests/llm/test_integration.py`): Real API calls to configured LLM providers
- **API tests** (`tests/llm/test_llm_api.py`): FastAPI endpoint tests with mocked services

LLM integration tests require API keys:

```bash
export OPENAI_API_KEY="your-key"
export DEEPINFRA_API_KEY="your-key"
# Tests will automatically skip if keys are missing
```

### Performance Testing

Run performance tests with different load scenarios:

```bash
# Start the application first
poetry run uvicorn main:app --reload --port 8080

# Light load test (10 users, 2 min)
poetry run locust -f tests/e2e/locustfile.py --host=http://localhost:8080 \
  --headless --users 10 --spawn-rate 2 --run-time 2m

# Medium load test (50 users, 5 min)
poetry run locust -f tests/e2e/locustfile.py --host=http://localhost:8080 \
  --headless --users 50 --spawn-rate 5 --run-time 5m

# Or use pre-configured tasks
npm run test:performance:light   # If using VS Code tasks
```

### Docker Test Environment

For integration testing with MySQL (same as production), use the dedicated test environment:

```bash
# Start isolated test database (MySQL on port 3307)
docker-compose -f docker-compose.test.yml up -d

# Run tests with MySQL instead of SQLite
TEST_DATABASE_URL="mysql+mysqlconnector://test_user:test_pass@localhost:3307/storyteller_test" \
poetry run pytest tests/ -v

# Run integration tests specifically
TEST_DATABASE_URL="mysql+mysqlconnector://test_user:test_pass@localhost:3307/storyteller_test" \
poetry run pytest tests/test_integration.py -v

# Clean up test environment (removes all test data)
docker-compose -f docker-compose.test.yml down -v
```

#### Test Environment Features

- **Isolated MySQL**: Separate database instance on port 3307
- **Production parity**: Same MySQL version and configuration as production
- **Clean state**: Each test run can start with fresh database
- **CI/CD ready**: Perfect for automated testing pipelines
- **No conflicts**: Runs alongside development environment

#### Test Database Configuration

| Setting       | Development          | Test Environment          |
| ------------- | -------------------- | ------------------------- |
| **Port**      | 3306                 | 3307                      |
| **Database**  | `storyteller`        | `storyteller_test`        |
| **User**      | `storyteller_user`   | `test_user`               |
| **Container** | `story-teller-mysql` | `story-teller-mysql-test` |

## Performance Testing

The project includes comprehensive performance tests using Locust to simulate realistic API usage patterns.

### Performance Test Structure

```
tests/performance/
├── __init__.py          # Package marker
├── locustfile.py        # Main Locust test scenarios
├── config.py            # Test configurations
└── README.md            # Performance testing documentation
```

### Running Performance Tests

```bash
# Start the API server first
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8080

# Start Locust web interface
poetry run locust --host=http://localhost:8080
# Then open http://localhost:8089

# Or run predefined test scenarios
poetry run locust --host=http://localhost:8080 --headless --users 50 --spawn-rate 5 --run-time 2m --html reports/performance/load_test.html
```

### Test Scenarios

- **Light Load Test**: 10 users, 2m duration - for development
- **Medium Load Test**: 50 users, 5m duration - for staging
- **Heavy Load Test**: 200 users, 10m duration - for production readiness
- **Stress Test**: 500 users, 5m duration - to find system limits
- **Spike Test**: 100 users, fast spawn - for sudden traffic increases
- **Endurance Test**: 30 users, 30m duration - for long-term stability

### User Types Simulated

- **StoryReaderUser**: Regular users who primarily read stories (most common)
- **StoryWriterUser**: Content creators who write and manage stories
- **AdminUser**: Administrative users performing bulk operations
- **HealthCheckUser**: Monitoring systems with regular health checks

## API Endpoints

### Stories

- `POST /api/v1/stories/` - Create a new story
- `GET /api/v1/stories/` - Get all stories (with filtering options)
- `GET /api/v1/stories/{story_id}` - Get a specific story
- `PUT /api/v1/stories/{story_id}` - Update a story
- `DELETE /api/v1/stories/{story_id}` - Delete a story
- `PATCH /api/v1/stories/{story_id}/publish` - Publish a story
- `PATCH /api/v1/stories/{story_id}/unpublish` - Unpublish a story

### LLM & AI Features

- `GET /api/v1/llm/health` - Check LLM service health and available models
- `POST /api/v1/llm/generate` - Generate story content using AI
- `POST /api/v1/llm/analyze` - Analyze text content (sentiment, genre, comprehensive)
- `POST /api/v1/llm/summarize` - Create story summaries with customizable length
- `POST /api/v1/llm/improve` - Improve story quality (grammar, style, general)
- `GET /api/v1/llm/models` - Get list of available LLM models
- `GET /api/v1/llm/stats` - Get LLM usage statistics and metrics

### Query Parameters for GET /api/v1/stories/

- `skip` (int): Number of stories to skip (default: 0)
- `limit` (int): Number of stories to return (default: 10, max: 100)
- `genre` (string): Filter by genre
- `author` (string): Filter by author (partial match)
- `published_only` (bool): Show only published stories (default: false)

## Example Usage

### Create a Story

```bash
curl -X POST "http://localhost:8080/api/v1/stories/" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "The Adventure Begins",
       "content": "Once upon a time in a distant land...",
       "author": "John Doe",
       "genre": "Fantasy",
       "is_published": false
     }'
```

### Get All Stories

```bash
curl "http://localhost:8080/api/v1/stories/"
```

### Get Stories with Filters

```bash
curl "http://localhost:8080/api/v1/stories/?genre=Fantasy&published_only=true&limit=5"
```

### AI Story Generation

```bash
# Generate a fantasy story
curl -X POST "http://localhost:8080/api/v1/llm/generate" \
     -H "Content-Type: application/json" \
     -d '{
       "prompt": "A brave knight discovers a hidden magical forest",
       "genre": "fantasy",
       "length": "short",
       "style": "engaging"
     }'

# Analyze story content
curl -X POST "http://localhost:8080/api/v1/llm/analyze" \
     -H "Content-Type: application/json" \
     -d '{
       "content": "Your story text here...",
       "analysis_type": "sentiment"
     }'

# Summarize a story
curl -X POST "http://localhost:8080/api/v1/llm/summarize" \
     -H "Content-Type: application/json" \
     -d '{
       "content": "Long story content here...",
       "summary_length": "brief",
       "focus": "plot"
     }'

# Improve story quality
curl -X POST "http://localhost:8080/api/v1/llm/improve" \
     -H "Content-Type: application/json" \
     -d '{
       "content": "Story to improve...",
       "improvement_type": "grammar",
       "target_audience": "adult"
     }'

# Check LLM health and available models
curl "http://localhost:8080/api/v1/llm/health"

# Get usage statistics
curl "http://localhost:8080/api/v1/llm/stats"
```

## Development

### Project Structure

```
story-teller/
├── main.py                 # FastAPI application entry point (imports from app/)
├── pyproject.toml          # Poetry configuration and dependencies
├── poetry.lock             # Poetry lock file
├── .env                   # Environment variables
├── llm_config.yaml        # LLM providers configuration
├── test_llm.py            # LLM integration testing script
├── app/                   # Main application package
│   ├── __init__.py
│   ├── main.py            # FastAPI app creation and configuration
│   ├── models/            # SQLAlchemy models
│   │   ├── __init__.py
│   │   └── story.py
│   ├── schemas/           # Pydantic schemas
│   │   ├── __init__.py
│   │   └── story.py
│   ├── routers/           # API route handlers
│   │   ├── __init__.py
│   │   ├── stories.py
│   │   └── llm.py         # LLM API endpoints
│   ├── llm/               # LLM integration module
│   │   ├── __init__.py
│   │   ├── config.py      # LLM configuration management
│   │   ├── models.py      # LLM data models
│   │   ├── services.py    # LLM service implementations
│   │   ├── chains.py      # LangChain processing chains
│   │   └── prompts.py     # Prompt templates
│   └── database/          # Database configuration
│       ├── __init__.py
│       └── connection.py
├── tests/                 # Test suite
│   ├── unit/              # Unit tests (models, schemas, core logic)
│   ├── integration/       # Integration tests (API endpoints, workflows)
│   └── performance/       # Performance testing with Locust
└── docker-compose.yml     # Docker configuration
```

### Code Quality

This project includes several development tools configured via Poetry:

- **Black**: Code formatter for consistent code style
- **isort**: Import sorter for organized imports
- **flake8**: Linter for code quality checks
- **mypy**: Static type checker
- **pytest**: Testing framework

Run all quality checks:

```bash
poetry run black .
poetry run isort .
poetry run flake8 .
poetry run mypy .
poetry run pytest
```

### VS Code Tasks

The project includes predefined VS Code tasks:

**Development:**

- Run FastAPI Development Server (Poetry)
- Poetry: Install Dependencies
- Poetry: Add Dependency

**Code Quality:**

- Poetry: Format Code (Black)
- Poetry: Sort Imports (isort)
- Poetry: Lint Code (flake8)
- Poetry: Type Check (mypy)

**Testing:**

- Poetry: Run Tests
- Poetry: Run Tests with Coverage
- Poetry: Run Unit Tests Only
- Poetry: Run API Tests Only
- Poetry: Run Integration Tests Only

**Performance Testing:**

- Locust: Start Web Interface
- Locust: Light Load Test
- Locust: Medium Load Test
- Locust: Heavy Load Test
- Locust: Stress Test
- Locust: Spike Test
- Locust: Endurance Test

**Maintenance:**

- Poetry: Check Outdated Packages
- Poetry: Update All Dependencies
- Poetry: Update Core Dependencies (Priority)

Access these via `Ctrl+Shift+P` > "Tasks: Run Task"

## Database

The application uses SQLite by default. The database file (`stories.db`) will be created automatically when you first run the application.

To use a different database, update the `DATABASE_URL` in your `.env` file.

## Environment Variables

### Core Application

- `DATABASE_URL`: Database connection string (default: sqlite:///./stories.db)
- `SENTRY_DSN`: Sentry DSN for error monitoring (optional)
- `SECRET_KEY`: Secret key for JWT tokens
- `DEBUG`: Enable debug mode (default: True)
- `ENVIRONMENT`: Environment name (default: development)

### LLM Integration

- `OPENAI_API_KEY`: OpenAI API key for GPT models (optional)
- `DEEPINFRA_API_KEY`: DeepInfra API key for hosted models (optional)
- `CUSTOM_LLM_API_KEY`: Custom LLM API key for OpenAI-compatible APIs (optional)
- `CUSTOM_LLM_BASE_URL`: Base URL for custom LLM API (optional)

## Monitoring

The application includes comprehensive error monitoring and performance tracking using Sentry.

### Error Monitoring Features

- **Real-time error tracking**: Automatic capture and reporting of exceptions
- **Performance monitoring**: Track API response times and database queries
- **User context**: Capture request headers and user data for debugging
- **Environment-based configuration**: Different Sentry projects for development/production

### Sentry Configuration

To enable Sentry monitoring, set the `SENTRY_DSN` environment variable:

```bash
# In your .env file
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

When configured, Sentry will automatically:

- Capture all unhandled exceptions
- Track API endpoint performance
- Monitor database connection issues
- Provide detailed error context and stack traces

### Monitoring Best Practices

- Use different Sentry projects for development, staging, and production
- Set up alerts for critical errors and performance degradation
- Review error trends and fix issues proactively
- Use Sentry's release tracking to monitor deployment impact

## License

This project is open source and available under the MIT License.
