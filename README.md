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
- Automatic API documentation with Swagger UI
- CORS support for frontend integration
- Modern dependency management with Poetry
- Development tools: Black, isort, flake8, mypy

## ✅ Testing

The application features a **three-tier testing strategy** for efficient development and reliable deployment:

### 🏗️ Test Tiers

- **Unit Tests** (`@pytest.mark.unit`) - Fast tests with mocked dependencies (SQLite, mocked services)
- **Integration Tests** (`@pytest.mark.integration`) - Database integration with MySQL test database
- **End-to-End Tests** (`@pytest.mark.e2e`) - Full infrastructure validation with MySQL, Redis, Celery, and real LLM providers

### 🚀 Launching tests

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

### 📖 Detailed Documentation

For comprehensive testing documentation, environment setup, and troubleshooting, see [tests/README.md](tests/README.md).

## Quick Start

### Port Configuration

The application uses flexible port configuration through environment variables. All ports can be customized via the `.env` file.

#### Default Ports:

- **FastAPI**: 8080
- **MySQL**: 3306
- **Redis**: 6379
- **phpMyAdmin**: 8081
- **Flower (Celery monitoring)**: 5555
- **Redis UI**: 8082
- **Test MySQL**: 3307
- **Test Redis**: 6380

#### Port Management:

```bash
# Check current port configuration and availability
./configure-ports.sh show

# Auto-fix any port conflicts
./configure-ports.sh fix

# Reset to default ports
./configure-ports.sh reset

# Validate ports without changing them
./configure-ports.sh validate
```

#### Auto-Port Assignment:

If you have port conflicts, you can use auto-port assignment:

```bash
# Start services with automatic port assignment
./docker-setup.sh start --auto-ports
./docker-setup.sh dev --auto-ports
```

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

For Celery task processing, use Docker profiles:

```bash
# Start with Celery infrastructure
./docker-setup.sh celery

# Or start full development environment
./docker-setup.sh dev
```

4. Access the application:

- API: http://localhost:8080
- API Documentation: http://localhost:8080/docs
- Database Admin: http://localhost:8081 (with `tools` or `full` profile)
- Task Monitoring: http://localhost:5555 (with `celery` or `full` profile)
- Redis UI: http://localhost:8082 (with `tools` or `full` profile)

## Docker Compose Profiles

The application uses Docker Compose profiles for flexible deployment:

### Available Profiles

- **default** (no profile): MySQL database only
- **production**: FastAPI app + Celery worker + MySQL
- **infrastructure**: MySQL + Redis + phpMyAdmin + Redis UI (for local development)
- **tools**: Same as infrastructure (MySQL + Redis + phpMyAdmin + Redis UI)
- **celery**: MySQL + Redis + Flower (for Celery development)
- **monitoring**: MySQL + Redis + Flower
- **dev**: Combines tools + monitoring (for local development)
- **full**: All infrastructure services (phpMyAdmin + Redis UI + Flower)

### Usage Examples

```bash
# Default setup (MySQL only) - matches pure Docker profile
./docker-setup.sh start
# or: docker-compose up -d

# Infrastructure only (for local API/worker development)
./docker-setup.sh infrastructure
# or: docker-compose --profile infrastructure up -d

# Development tools (same as infrastructure)
./docker-setup.sh tools
# or: docker-compose --profile tools up -d

# Celery infrastructure (MySQL + Redis + Flower)
./docker-setup.sh celery
# or: docker-compose --profile celery up -d

# Development infrastructure with monitoring (recommended for local development)
./docker-setup.sh dev
# or: docker-compose --profile tools --profile monitoring up -d

# All infrastructure services
./docker-setup.sh full
# or: docker-compose --profile full up -d

# Production setup (App + Worker) - matches pure Docker profile
./docker-setup.sh production
# or: docker-compose --profile production up -d

# Everything (Production + Tools + Monitoring)
./docker-setup.sh all
# or: docker-compose --profile production --profile tools --profile monitoring up -d
```

### Service URLs by Profile

| Profile/Command | MySQL | Redis | API | Docs | phpMyAdmin | Flower | Redis UI | Celery Worker | Notes                                        |
| --------------- | ----- | ----- | --- | ---- | ---------- | ------ | -------- | ------------- | -------------------------------------------- |
| default         | ✅    | ❌    | ❌  | ❌   | ❌         | ❌     | ❌       | ❌            | MySQL only                                   |
| infrastructure  | ✅    | ✅    | ❌  | ❌   | ✅         | ❌     | ✅       | ❌            | Infrastructure only (for local dev)          |
| tools           | ✅    | ✅    | ❌  | ❌   | ✅         | ❌     | ✅       | ❌            | Same as infrastructure                       |
| celery          | ✅    | ✅    | ❌  | ❌   | ❌         | ✅     | ❌       | ❌            | MySQL + Redis + Flower (for local dev)       |
| monitoring      | ✅    | ✅    | ❌  | ❌   | ❌         | ✅     | ❌       | ❌            | MySQL + Redis + Flower                       |
| dev             | ✅    | ✅    | ❌  | ❌   | ✅         | ✅     | ✅       | ❌            | Infrastructure + monitoring (for local dev)  |
| production      | ✅    | ✅    | ✅  | ✅   | ❌         | ❌     | ❌       | ✅            | App + Worker (complete production setup)     |
| full            | ✅    | ✅    | ✅  | ✅   | ✅         | ✅     | ✅       | ✅            | Everything (production + tools + monitoring) |

#### Docker Commands

```bash
# Default setup (MySQL only) - matches Docker profile
./docker-setup.sh start

# Infrastructure only (MySQL + Redis + Tools) - for local development
./docker-setup.sh infrastructure

# With development tools (MySQL + Redis + Tools) - same as infrastructure
./docker-setup.sh tools

# Celery infrastructure (MySQL + Redis + Flower) - for local development
./docker-setup.sh celery

# Development infrastructure (MySQL + Redis + monitoring) - for local development
./docker-setup.sh dev

# All infrastructure services (phpMyAdmin + Redis UI + Flower)
./docker-setup.sh full

# Production setup (App + Worker) - matches Docker profile
./docker-setup.sh production

# Everything (Production + Tools + Monitoring)
./docker-setup.sh all

# Stop services
./docker-setup.sh stop

# View logs
./docker-setup.sh logs

# Connect to MySQL
./docker-setup.sh mysql

# Migrate data from SQLite (if you have existing data)
./docker-setup.sh migrate

# Show status
./docker-setup.sh status

# Clean up (removes all data!)
./docker-setup.sh clean

# Docker Compose management
docker-compose --profile infrastructure up -d          # Infrastructure only
docker-compose --profile tools up -d                   # Tools only (same as infrastructure)
docker-compose --profile celery up -d                  # Celery infrastructure
docker-compose --profile monitoring up -d              # Monitoring only
docker-compose --profile production up -d              # Production (app + worker)
docker-compose --profile full up -d                    # All infrastructure
docker-compose --profile tools --profile monitoring up -d  # Development infrastructure
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

## Development Tools

```bash
# Format code with Black
poetry run black .

# Sort imports with isort
poetry run isort .

# Lint code with flake8
poetry run flake8 .

# Type checking with mypy
poetry run mypy .
```

### 🔧 VS Code Integration

#### **Essential Development Tasks**

- `Poetry: Run Unit Tests Only` - Daily development workflow (unit tests)
- `Poetry: Run Tests` - Integration testing with MySQL database
- `Poetry: Run All Task Tests` - TaskService validation
- `Poetry: Run All New Async Tests` - Modern async test suite

#### **Component-Specific Testing Tasks**

- `Poetry: Run Stories Tests` - Story management tests
- `Poetry: Run LLM Tests` - LLM functionality tests
- `Poetry: Run All Celery Integration Tests` - End-to-end infrastructure testing

#### **Specialized Testing Tasks**

- `Poetry: Run Tests Without Celery Integration` - Fast CI/CD pipeline
- `Poetry: Run Fast Tests Only` - Unit tests only

_Access via: `Ctrl+Shift+P` → "Tasks: Run Task"_

### **Common Issues and Solutions**

**Redis Connection Errors:**

```bash
# Check Redis status via Docker
./docker-setup.sh status
# Start if needed
./docker-setup.sh celery
```

**Celery Worker Not Processing:**

```bash
# Check worker status
./docker-setup.sh status
# Restart Celery services
./docker-setup.sh stop && ./docker-setup.sh celery
# Monitor tasks via Flower at http://localhost:5555
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
