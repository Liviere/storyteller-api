# End-to-End Tests

This directory contains end-to-end (E2E) tests and performance tests for the Story Teller API, covering both legacy synchronous workflows and modern asynchronous (Celery-based) patterns.

## 🏗️ Architecture Overview

E2E tests validate complete user journeys across:

- **Story Management**: Full CRUD lifecycle with state transitions
- **LLM Integration**: AI-powered story generation, analysis, and improvement
- **Task Processing**: Asynchronous workflows with Celery workers
- **Performance**: Load testing and scalability validation under realistic conditions

## 📁 Test Structure

```
tests/e2e/
├── __init__.py                    # Package initialization
├── test_workflows_async.py        # 🆕 Modern async workflow tests (~8 tests)
├── locustfile.py                 # Performance/load testing with Locust
├── config.py                     # Performance test configuration and scenarios
└── README.md                     # This documentation
```

## 🧪 Test Categories

### 1. Modern Async Workflow Tests (`test_workflows_async.py`) - 🆕 Current Approach

**Purpose**: Validate complete async user journeys with task processing

**Key Workflow Scenarios**:

```python
async def test_complete_story_generation_workflow():
    """Test full async story generation from prompt to published story"""

    # 1. Create async story generation task
    response = await async_client.post("/api/v1/stories/generate", json={
        "prompt": "A story about microservices architecture",
        "genre": "Technology",
        "target_length": "medium"
    })

    task_id = response.json()["task_id"]

    # 2. Poll for task completion (real async processing)
    story_data = await poll_task_completion(task_id, timeout=120)

    # 3. Verify story was created and saved
    story_id = story_data["story_id"]
    story_response = await async_client.get(f"/api/v1/stories/{story_id}")

    assert story_response.status_code == 200
    assert len(story_response.json()["story_text"]) > 100

    # 4. Generate analysis task for the story
    analysis_response = await async_client.post(f"/api/v1/stories/{story_id}/analyze")
    analysis_task_id = analysis_response.json()["task_id"]

    # 5. Wait for analysis completion
    analysis_data = await poll_task_completion(analysis_task_id, timeout=60)

    # 6. Verify analysis results
    assert "themes" in analysis_data
    assert "sentiment" in analysis_data
    assert analysis_data["word_count"] > 0

    # 7. Publish the story
    publish_response = await async_client.put(f"/api/v1/stories/{story_id}", json={
        "is_published": True
    })

    assert publish_response.status_code == 200
    assert publish_response.json()["is_published"] is True
```

**Test Classes**:

- `TestAsyncStoryGeneration`: End-to-end story creation workflows
- `TestAsyncStoryAnalysis`: Complete analysis and improvement pipelines
- `TestMultiStepWorkflows`: Complex workflows combining multiple async operations
- `TestAsyncErrorHandling`: Failure scenarios in async context

**Infrastructure Requirements**:

```bash
# Required for real async processing
# Start Celery infrastructure
./docker-setup.sh celery   # Redis + Worker + Flower in containers

# LLM API keys for real story operations
export OPENAI_API_KEY="your-openai-key"
```

**Test Markers**: `@pytest.mark.celery_integration`

**Execution Time**: ~1.3 seconds (mocked) / ~5-12 minutes (real Celery) | **Dependencies**: Mocked TaskService / Celery + Redis + LLM APIs

### 2. Performance Tests (`locustfile.py`) - Load & Scalability

**Purpose**: Validate system performance under realistic load conditions

**Test Scenarios**:

- **Light Load**: 10 users, 2 spawn rate, 2 minutes
- **Medium Load**: 50 users, 5 spawn rate, 5 minutes
- **Heavy Load**: 200 users, 10 spawn rate, 10 minutes
- **Stress Test**: 500 users, 20 spawn rate, 5 minutes
- **Spike Test**: 100 users, 50 spawn rate, 3 minutes
- **Endurance Test**: 30 users, 3 spawn rate, 30 minutes

**Load Test Operations**:

```python
class StoryTellerUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Setup user session"""
        pass

    @task(3)
    def create_story(self):
        """Test story creation (high frequency)"""
        self.client.post("/api/v1/stories/", json={
            "title": f"Load Test Story {self.user_id}",
            "content": "Generated during load testing",
            "genre": "Testing"
        })

    @task(2)
    def list_stories(self):
        """Test story listing (medium frequency)"""
        self.client.get("/api/v1/stories/")

    @task(1)
    def generate_async_story(self):
        """Test async story generation (lower frequency, higher impact)"""
        response = self.client.post("/api/v1/stories/generate", json={
            "prompt": "A load testing story",
            "genre": "Performance"
        })

        if response.status_code == 202:
            task_id = response.json()["task_id"]
            # Poll for completion in background
            self.poll_task_status(task_id)
```

**Execution**: Via VS Code tasks or command line

```bash
# Web interface for interactive testing
poetry run locust -f tests/e2e/locustfile.py --host=http://localhost:8080

# Automated load tests
```

## 🚀 Running E2E Tests

### Fast Development (Legacy Compatibility)

```bash
# Legacy workflow tests (~31 tests, ~2-4 minutes)
poetry run pytest tests/e2e/test_workflows.py.deprecated -v

# Skip LLM integration in legacy tests
poetry run pytest tests/e2e/test_workflows.py.deprecated -m "not llm_integration" -v
```

### Modern Async Workflows (Real Infrastructure)

```bash
# Start required infrastructure
./docker-setup.sh celery
# Worker included in celery profile

# Set LLM API keys
export OPENAI_API_KEY="your-openai-key"

# Modern async workflow tests (8 tests, ~1.3 seconds - mocked)
poetry run pytest tests/e2e/test_workflows_async.py -v

# Real Celery integration tests (requires infrastructure)
poetry run pytest tests/e2e/test_workflows_async.py -v -m celery_integration

# All E2E tests including legacy (~39 tests, ~7-16 minutes with Celery)
poetry run pytest tests/e2e/ -v
```

### Performance Testing

```bash
# Start application server
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8080

# Interactive load testing (web interface)
poetry run locust -f tests/e2e/locustfile.py --host=http://localhost:8080

# Automated load tests (headless)
poetry run locust -f tests/e2e/locustfile.py --host=http://localhost:8080 --headless --users 50 --spawn-rate 5 --run-time 5m --html reports/performance/load_test.html

# Use VS Code tasks for common scenarios
# Ctrl+Shift+P → "Tasks: Run Task" → "Locust: Light Load Test"
```

### Selective Testing Strategies

```bash
# Skip expensive integration tests (development)
poetry run pytest tests/e2e/ -m "not celery_integration and not llm_integration" -v

# Only modern async patterns (recommended)
poetry run pytest tests/e2e/test_workflows_async.py -v

# Specific workflow categories
poetry run pytest tests/e2e/test_workflows_async.py::TestAsyncStoryGeneration -v
poetry run pytest tests/e2e/test_workflows_async.py::TestMultiStepWorkflows -v
```

## 📊 Test Metrics Summary

| Test Category     | File                           | Tests   | Time      | Cost        | Dependencies       |
| ----------------- | ------------------------------ | ------- | --------- | ----------- | ------------------ |
| Legacy Workflows  | `test_workflows.py.deprecated` | 31      | ~4m       | ~$0.15      | LLM APIs (direct)  |
| Async Workflows   | `test_workflows_async.py`      | 8       | ~1.3s     | $0 (mocked) | Mocked TaskService |
| Async + Celery    | `test_workflows_async.py`      | 8       | ~12m      | ~$0.40      | Celery + LLM APIs  |
| Performance Tests | `locustfile.py`                | Manual  | Variable  | $0          | Running server     |
| **Fast Total**    | **Mocked Only**                | **8**   | **~1.3s** | **$0**      | **Mocked**         |
| **Full Total**    | **All Files**                  | **~39** | **~16m**  | **~$0.55**  | **Mixed**          |

_Cost estimates based on OpenAI gpt-3.5-turbo pricing for workflow tests_

## 🔧 Development Workflow

### Adding New E2E Scenarios

1. **Identify User Journey**: Define complete workflow from start to finish
2. **Write Async Test**: Add to `test_workflows_async.py` with real task processing
3. **Add Performance Test**: Include scenario in `locustfile.py` if relevant
4. **Validate End-to-End**: Test with real infrastructure and LLM integration

### Debugging E2E Failures

```bash
# Run single workflow with detailed output
poetry run pytest tests/e2e/test_workflows_async.py::test_specific_workflow -v -s

# Check Celery worker status during failures
./docker-setup.sh status
./docker-setup.sh logs

# Monitor task processing
# Flower available at http://localhost:5555 (included in celery profile)
```

### Performance Analysis

```bash
# Generate performance reports
poetry run locust -f tests/e2e/locustfile.py --host=http://localhost:8080 --headless --users 100 --spawn-rate 10 --run-time 5m --html reports/performance/analysis.html

# View detailed performance metrics
open reports/performance/analysis.html
```

## 🎯 E2E Test Philosophy

E2E tests validate **complete user value delivery**:

1. **Real Infrastructure**: Use actual Celery workers, Redis, LLM APIs
2. **End-to-End Flows**: Test complete workflows, not just API endpoints
3. **Production-Like**: Mirror real-world usage patterns and data volumes
4. **User-Centric**: Focus on user goals, not technical implementation details

**When to Write E2E Tests**:

- ✅ New user workflows spanning multiple components
- ✅ Critical business processes (story generation, publishing)
- ✅ Integration points between major system components
- ❌ Simple CRUD operations (covered by integration tests)
- ❌ Unit-level business logic (covered by unit tests)

### Performance Tests

#### Prerequisites

1. Start the API server:

   ```bash
   poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8080
   ```

2. Ensure database is running and populated with test data

#### Running Locust Tests

**Web Interface (Recommended):**

```bash
poetry run locust -f tests/e2e/locustfile.py --host=http://localhost:8080
```

Then open http://localhost:8089 in your browser to configure and run tests.

**Headless Mode:**

```bash
# Light load test
poetry run locust -f tests/e2e/locustfile.py --host=http://localhost:8080 \
  --headless --users 10 --spawn-rate 2 --run-time 2m

# Medium load test
poetry run locust -f tests/e2e/locustfile.py --host=http://localhost:8080 \
  --headless --users 50 --spawn-rate 5 --run-time 5m

# Heavy stress test
poetry run locust -f tests/e2e/locustfile.py --host=http://localhost:8080 \
  --headless --users 200 --spawn-rate 10 --run-time 10m
```

#### Pre-configured Tasks (via tasks.json)

```bash
# Light load test
npm run test:performance:light

# Medium load test
npm run test:performance:medium

# Heavy load test
npm run test:performance:heavy
```

## Test Configuration

### Workflow Tests

- Use standard pytest fixtures from main `conftest.py`
- LLM tests require proper LLM configuration and available models
- Database tests use isolated test database

### Performance Tests

Performance test configuration is managed in `config.py`:

```python
# Default test scenarios
SCENARIOS = {
    'light': {'users': 10, 'spawn_rate': 2, 'duration': '2m'},
    'medium': {'users': 50, 'spawn_rate': 5, 'duration': '5m'},
    'heavy': {'users': 200, 'spawn_rate': 10, 'duration': '10m'},
    'stress': {'users': 500, 'spawn_rate': 20, 'duration': '5m'},
    'spike': {'users': 100, 'spawn_rate': 50, 'duration': '3m'},
    'endurance': {'users': 30, 'spawn_rate': 3, 'duration': '30m'}
}
```

## Test Workflow Examples

### Complete Story Workflow

```python
# Create story → Add content → Generate with LLM → Retrieve results
story = await create_story({"title": "Test Story", "content": "Once upon a time..."})
llm_response = await generate_story_continuation(story.id)
final_story = await get_story(story.id)
```

### LLM Integration Workflow

```python
# Test complete LLM pipeline: config → model → generation → validation
llm_config = await get_llm_config()
response = await generate_text({"prompt": "Tell me a story", "max_tokens": 100})
assert response.choices[0].message.content
```

## Integration with Main Test Suite

E2E tests complement the main test structure:

- **tests/shared/**: Core component tests (models, schemas, main app)
- **tests/stories/**: Router-specific tests (unit + integration)
- **tests/llm/**: LLM functionality tests (mocked + real API)
- **tests/e2e/**: Complete user workflows + performance testing

All tests can be run together: `poetry run pytest tests/` or individually by directory.

## Test Scenarios

The performance tests include several user types that simulate realistic API usage:

### User Types

1. **StoryReaderUser** (Weight: 3)

   - Simulates regular users who primarily read stories
   - Performs GET operations with various filters
   - Most common user type

2. **StoryWriterUser** (Weight: 1)

   - Simulates content creators who write and manage stories
   - Performs CRUD operations on stories
   - Creates, updates, publishes, and deletes stories

3. **AdminUser** (Weight: 1)

   - Simulates administrative users
   - Performs bulk operations and administrative tasks
   - Uses higher limits and more intensive operations

4. **HealthCheckUser** (Weight: 1)
   - Simulates monitoring systems
   - Regular health checks and lightweight requests

## Running Tests

### Start the Application

First, make sure your Story Teller API is running:

```bash
# In one terminal
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

### Basic Locust Usage

```bash
# Start Locust with web interface
poetry run locust --host=http://localhost:8080

# Then open http://localhost:8089 in your browser
```

### Predefined Test Scenarios

Use the VS Code tasks or run these commands directly:

#### Light Load Test (Development)

```bash
poetry run locust --host=http://localhost:8080 --users 10 --spawn-rate 2 --run-time 2m --html reports/performance/light_load_report.html
```

#### Medium Load Test (Staging)

```bash
poetry run locust --host=http://localhost:8080 --users 50 --spawn-rate 5 --run-time 5m --html reports/performance/medium_load_report.html
```

#### Heavy Load Test (Production Readiness)

```bash
poetry run locust --host=http://localhost:8080 --users 200 --spawn-rate 10 --run-time 10m --html reports/performance/heavy_load_report.html
```

#### Stress Test (Find Limits)

```bash
poetry run locust --host=http://localhost:8080 --users 500 --spawn-rate 20 --run-time 5m --html reports/performance/stress_test_report.html
```

#### Spike Test (Sudden Traffic)

```bash
poetry run locust --host=http://localhost:8080 --users 100 --spawn-rate 50 --run-time 3m --html reports/performance/spike_test_report.html
```

#### Endurance Test (Long Running)

```bash
poetry run locust --host=http://localhost:8080 --users 30 --spawn-rate 3 --run-time 30m --html reports/performance/endurance_test_report.html
```

### Command Line Options

```bash
# Headless mode (no web interface)
poetry run locust --host=http://localhost:8080 --headless --users 50 --spawn-rate 5 --run-time 2m

# Generate HTML report
poetry run locust --host=http://localhost:8080 --headless --users 50 --spawn-rate 5 --run-time 2m --html report.html

# CSV output
poetry run locust --host=http://localhost:8080 --headless --users 50 --spawn-rate 5 --run-time 2m --csv=results

# Specify locustfile explicitly
poetry run locust -f tests/performance/locustfile.py --host=http://localhost:8080
```

## Test Data

The tests automatically generate realistic test data:

- **Story titles**: "Test Story {user_id}-{random_number}"
- **Content**: Generated from templates with random elements
- **Authors**: "LoadTest User {user_id}" or predefined names
- **Genres**: Fantasy, Sci-Fi, Mystery, Romance, Adventure, Horror, Drama

## Metrics to Monitor

When running tests, pay attention to:

### Response Time Metrics

- **Average response time**: Should be under 200ms for GET requests
- **95th percentile**: Should be under 500ms
- **Maximum response time**: Should be under 2 seconds

### Throughput Metrics

- **Requests per second (RPS)**: Target varies by endpoint
- **Failures per second**: Should be near zero under normal load

### Error Metrics

- **Error rate**: Should be under 1% under normal load
- **HTTP error codes**: Monitor for 4xx and 5xx errors

### System Metrics (Monitor separately)

- **CPU usage**: Should stay under 80%
- **Memory usage**: Monitor for memory leaks
- **Database connections**: Monitor connection pool usage
- **Disk I/O**: Important for SQLite operations

## Reports

Locust generates detailed reports including:

- Response time distribution
- Request statistics by endpoint
- Failure analysis
- Charts and graphs

Reports are saved to the `reports/performance/` directory when using `--html` option.

## Best Practices

### Before Testing

1. Use a separate test database or ensure you can restore data
2. Monitor system resources during tests
3. Start with light loads and gradually increase
4. Test individual endpoints before full scenarios

### During Testing

1. Watch for error rates and response time spikes
2. Monitor system resources (CPU, memory, disk)
3. Check application logs for errors
4. Note when performance starts to degrade

### After Testing

1. Analyze generated reports
2. Document performance baselines
3. Investigate any failures or slow responses
4. Clean up test data if needed

## Troubleshooting

### Common Issues

1. **Connection refused**: Make sure the API is running on valid port
2. **High error rates**: Check API logs and reduce load
3. **Slow responses**: Monitor system resources and database performance
4. **Import errors**: Ensure Locust is installed with `poetry install`

### Debug Mode

Run with verbose logging:

```bash
poetry run locust --host=http://localhost:8080 --loglevel DEBUG
```

### Custom Configuration

You can modify `locustfile.py` to:

- Add new user behaviors
- Change request patterns
- Adjust wait times
- Add custom metrics

## Integration with CI/CD

For automated performance testing:

```bash
# Example CI command
poetry run locust --host=http://localhost:8080 --headless --users 50 --spawn-rate 5 --run-time 2m --html ci_report.html --exit-code-on-error 1.0
```

The `--exit-code-on-error` flag makes Locust exit with non-zero code if failure rate exceeds the threshold (1.0% in this example).
