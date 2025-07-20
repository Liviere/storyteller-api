# Story Teller API

REST API for managing stories built with FastAPI and Poetry.

## Features

- Create, read, update, and delete stories
- Filter stories by genre, author, and publication status
- Publish/unpublish stories
- **AI-powered story generation with LLM integration**
- **Story analysis (sentiment, genre classification, comprehensive analysis)**
- **Story summarization with customizable length and focus**
- **Story improvement (grammar, style, general quality enhancement)**
- **Support for multiple LLM providers (OpenAI, DeepInfra, Any OpenAI-compatible API)**
- **LLM usage statistics and health monitoring**
- **MySQL database with SQLAlchemy ORM (with Docker support)**
- **SQLite fallback for development**
- **Error monitoring and tracking with Sentry**
- Automatic API documentation with Swagger UI
- CORS support for frontend integration
- Modern dependency management with Poetry
- Development tools: Black, isort, flake8, mypy, pytest
- **Docker and docker-compose for easy deployment**
- **Isolated test environment with dedicated MySQL instance**
- **Performance testing with Locust**

## Quick Start

### Option 1: Docker Setup (Recommended)

#### Prerequisites

- Docker and Docker Compose
- Git

#### Installation with Docker

1. Clone or navigate to the project directory:

```bash
cd /home/livierek/projekty/story-teller
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

4. Access the application:

- API: http://localhost:8080
- API Documentation: http://localhost:8080/docs
- Database Admin: http://localhost:8081

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
```

### Option 2: Local Development Setup

#### Prerequisites

- Python 3.8.1+
- Poetry (https://python-poetry.org/docs/#installation)
- MySQL (optional, defaults to SQLite)

#### Installation

1. Clone or navigate to the project directory:

```bash
cd /home/livierek/projekty/story-teller
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
- **Generate story**: `POST /api/v1/llm/generate`
- **Analyze text**: `POST /api/v1/llm/analyze`
- **Summarize content**: `POST /api/v1/llm/summarize`
- **Improve story**: `POST /api/v1/llm/improve`
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

The project includes comprehensive unit, integration, and end-to-end tests with organized structure and high code coverage.

### Test Structure

```
tests/
├── conftest.py          # Main test configuration and fixtures
├── shared/              # Shared component tests (models, schemas, main app)
│   ├── test_models.py   # SQLAlchemy model tests
│   ├── test_schemas.py  # Pydantic schema tests
│   └── test_main.py     # Main application tests
├── stories/             # Stories router tests
│   ├── test_unit.py     # Unit tests for story validation and business logic
│   ├── test_integration.py # API endpoint integration tests
│   └── conftest.py      # Stories-specific fixtures
├── llm/                 # LLM functionality tests
│   ├── test_unit.py     # Unit tests with mocked LLM services
│   ├── test_integration.py # Real LLM API integration tests
│   ├── test_llm_api.py  # LLM API endpoint tests (mocked)
│   └── conftest.py      # LLM-specific fixtures and configuration
├── e2e/                 # End-to-end workflows and performance tests
│   ├── test_workflows.py # Complete user journey tests
│   ├── locustfile.py    # Performance testing scenarios
│   ├── config.py        # Performance test configuration
│   └── conftest.py      # E2E test fixtures
└── README.md           # Detailed test documentation
```

### Running Tests

```bash
# Run all tests (107 total)
poetry run pytest

# Run with coverage report
poetry run pytest --cov=. --cov-report=html
open reports/coverage/index.html

# Run specific test categories
poetry run pytest tests/shared/     # Core component tests (16 tests)
poetry run pytest tests/stories/   # Stories functionality (34 tests)
poetry run pytest tests/llm/       # LLM functionality (51 tests)
poetry run pytest tests/e2e/       # End-to-end workflows (6 tests)

# Run specific test files
poetry run pytest tests/stories/test_integration.py -v
poetry run pytest tests/llm/test_unit.py -v

# Run with different markers
poetry run pytest -m "not llm_integration"  # Skip LLM integration tests
poetry run pytest -m "slow"                 # Run only slow tests
```

### Test Features

- **Router-based organization**: Tests organized by application routers (stories, llm)
- **Shared components**: Reusable tests for models, schemas, and main app
- **Comprehensive coverage**: Unit tests, integration tests, and complete workflows
- **LLM testing**: Both mocked unit tests and real API integration tests
- **Performance testing**: Load testing with Locust for various scenarios
- **Isolated testing**: Each test uses temporary SQLite database or dedicated MySQL test instance
- **Fixtures and mocking**: Extensive use of pytest fixtures and mocking for reliable tests
- **Fast execution**: Unit tests run quickly, integration tests can be skipped if needed

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
