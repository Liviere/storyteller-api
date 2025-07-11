# Story Teller API

REST API for managing stories built with FastAPI and Poetry.

## Features

- Create, read, update, and delete stories
- Filter stories by genre, author, and publication status
- Publish/unpublish stories
- **MySQL database with SQLAlchemy ORM (with Docker support)**
- **SQLite fallback for development**
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

# Run tests with coverage
poetry run pytest --cov=. --cov-report=term-missing --cov-report=html

# Run specific test categories
poetry run pytest tests/test_models.py tests/test_schemas.py  # Unit tests
poetry run pytest tests/test_api.py                          # API tests
poetry run pytest tests/test_integration.py                  # Integration tests
```

## Testing

The project includes comprehensive unit and integration tests with high code coverage (96%+).

### Test Structure

```
tests/
├── conftest.py          # Test configuration and fixtures
├── test_models.py       # SQLAlchemy model tests
├── test_schemas.py      # Pydantic schema tests
├── test_api.py          # API endpoint tests
├── test_main.py         # Main application tests
├── test_integration.py  # Integration tests
└── README.md           # Test documentation
```

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage report
poetry run pytest --cov=. --cov-report=html
open htmlcov/index.html

# Run specific test file
poetry run pytest tests/test_api.py -v

# Run specific test method
poetry run pytest tests/test_api.py::TestStoriesAPI::test_create_story -v
```

### Test Features

- **Isolated testing**: Each test uses a temporary SQLite database
- **Comprehensive coverage**: Tests for models, schemas, API endpoints, and integrations
- **Error handling**: Tests for both success and failure scenarios
- **Fixtures**: Reusable test data and database sessions
- **Fast execution**: Tests run in under 2 seconds

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
performance_tests/
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
poetry run locust --host=http://localhost:8080 --headless --users 50 --spawn-rate 5 --run-time 2m --html reports/load_test.html
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

## Development

### Project Structure

```
story-teller/
├── main.py                 # FastAPI application entry point
├── pyproject.toml          # Poetry configuration and dependencies
├── poetry.lock             # Poetry lock file
├── .env                   # Environment variables
├── models/                # SQLAlchemy models
│   ├── __init__.py
│   └── story.py
├── schemas/               # Pydantic schemas
│   ├── __init__.py
│   └── story.py
├── routers/               # API route handlers
│   ├── __init__.py
│   └── stories.py
└── database/              # Database configuration
    ├── __init__.py
    └── connection.py
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

- `DATABASE_URL`: Database connection string (default: sqlite:///./stories.db)
- `SECRET_KEY`: Secret key for JWT tokens
- `DEBUG`: Enable debug mode (default: True)
- `ENVIRONMENT`: Environment name (default: development)

## License

This project is open source and available under the MIT License.
