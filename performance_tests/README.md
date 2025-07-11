# Performance Tests for Story Teller API

This directory contains Locust-based performance tests for the Story Teller API.

## Prerequisites

Make sure you have installed all dependencies:

```bash
poetry install
```

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
poetry run locust --host=http://localhost:8080 --users 10 --spawn-rate 2 --run-time 2m --html reports/light_load_report.html
```

#### Medium Load Test (Staging)

```bash
poetry run locust --host=http://localhost:8080 --users 50 --spawn-rate 5 --run-time 5m --html reports/medium_load_report.html
```

#### Heavy Load Test (Production Readiness)

```bash
poetry run locust --host=http://localhost:8080 --users 200 --spawn-rate 10 --run-time 10m --html reports/heavy_load_report.html
```

#### Stress Test (Find Limits)

```bash
poetry run locust --host=http://localhost:8080 --users 500 --spawn-rate 20 --run-time 5m --html reports/stress_test_report.html
```

#### Spike Test (Sudden Traffic)

```bash
poetry run locust --host=http://localhost:8080 --users 100 --spawn-rate 50 --run-time 3m --html reports/spike_test_report.html
```

#### Endurance Test (Long Running)

```bash
poetry run locust --host=http://localhost:8080 --users 30 --spawn-rate 3 --run-time 30m --html reports/endurance_test_report.html
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
poetry run locust -f performance_tests/locustfile.py --host=http://localhost:8080
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

Reports are saved to the `reports/` directory when using `--html` option.

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
