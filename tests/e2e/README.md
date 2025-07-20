# End-to-End Tests

This directory contains end-to-end (E2E) tests and performance tests for the Story Teller API.

## Structure

```
tests/e2e/
├── __init__.py              # Package initialization
├── README.md               # This file
├── test_workflows.py       # Complete workflow tests
├── locustfile.py          # Performance/load testing with Locust
└── config.py              # Performance test configuration
```

## Test Categories

### Workflow Tests (`test_workflows.py`)

Complete user journey tests that validate end-to-end functionality:

- **Story Lifecycle Tests**: Full CRUD operations with state transitions
- **Multi-Story Workflows**: Complex scenarios with multiple stories
- **LLM Integration Workflows**: Combined story management and AI operations
- **Error Handling Workflows**: Cross-component error scenarios

### Performance Tests (`locustfile.py`)

Load and performance testing using Locust framework:

- **Load Testing**: Simulated user load with realistic usage patterns
- **Stress Testing**: High-load scenarios to identify breaking points
- **Endurance Testing**: Long-running tests for stability validation
- **Spike Testing**: Sudden load increases to test elasticity

## Running Tests

### Workflow Tests

```bash
# Run all workflow tests
poetry run pytest tests/e2e/test_workflows.py

# Run only story workflow tests
poetry run pytest tests/e2e/test_workflows.py::TestStoryWorkflows

# Run only LLM workflow tests (requires LLM configuration)
poetry run pytest tests/e2e/test_workflows.py::TestLLMWorkflows -m llm_integration
```

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
