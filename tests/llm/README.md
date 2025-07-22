# LLM Tests

This directory contains comprehensive tests for Large Language Model (LLM) functionality in the Story Teller API, including both synchronous and asynchronous (Celery-based) operations.

## 🏗️ Architecture Overview

The LLM system supports:

- **Synchronous Operations**: Direct API calls for health checks, model info, statistics
- **Asynchronous Operations**: Celery-based task processing for story generation, analysis
- **Multiple Providers**: OpenAI, DeepInfra, with extensible provider architecture
- **Configuration Management**: YAML-based model configuration and task assignments

## 📁 Test Structure

```
tests/llm/
├── __init__.py                    # Package marker
├── conftest_llm.py               # LLM-specific fixtures and configuration
├── test_unit.py                  # Unit tests with mocked LLM services (25 tests)
├── test_integration.py           # Real LLM API integration tests (7 tests)
├── test_llm_api.py              # Sync API endpoints testing (~10 tests)
├── test_llm_api_async.py        # 🆕 Async API endpoints with TaskResponse (~15 tests)
├── test_integration_celery.py   # 🆕 Real LLM + Celery integration (~8 tests)
└── README.md                    # This documentation
```

## 🧪 Test Categories

### 1. Unit Tests (`test_unit.py`) - Fast Development

**Purpose**: Test LLM service logic with mocked dependencies

- **Configuration validation**: YAML parsing, model resolution, task assignments
- **Service layer logic**: Method signatures, return values, exception handling
- **Error handling**: Invalid inputs, timeout scenarios, service failures
- **Provider abstraction**: Testing provider interface implementations

**Mocking Strategy**:

```python
@patch('app.llm.services.LLMService._make_request')
def test_story_generation(mock_request):
    mock_request.return_value = {"story": "Generated story content"}

    result = llm_service.generate_story("Test prompt")
    assert "Generated story content" in result["story"]
```

**Execution Time**: ~0.6 seconds | **API Costs**: None | **Dependencies**: None

### 2. Sync API Tests (`test_llm_api.py`) - Endpoint Validation

**Purpose**: Test synchronous LLM endpoints with mocked services

**Endpoints Tested**:

- `GET /api/v1/llm/health` - Service health status
- `GET /api/v1/llm/models` - Available model information
- `GET /api/v1/llm/stats` - Usage statistics

**Test Patterns**:

```python
async def test_health_endpoint(async_client, mock_llm_service):
    mock_llm_service.get_health.return_value = {"status": "healthy"}

    response = await async_client.get("/api/v1/llm/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

**Execution Time**: ~1-2 seconds | **API Costs**: None | **Dependencies**: Mocked LLM

### 3. Async API Tests (`test_llm_api_async.py`) - 🆕 TaskResponse Endpoints

**Purpose**: Test asynchronous LLM operations returning TaskResponse objects

**Endpoints Tested**:

- `POST /api/v1/llm/stories/generate` - Async story generation
- `POST /api/v1/llm/stories/analyze` - Async story analysis
- `POST /api/v1/llm/stories/summarize` - Async story summarization

**Test Patterns**:

```python
async def test_async_story_generation(async_client, mock_task_service):
    mock_task_service.process_task.return_value = TaskResponse(
        task_id="llm_test_123",
        status=TaskStatus.PENDING,
        result=None
    )

    response = await async_client.post("/api/v1/llm/stories/generate", json={
        "prompt": "Test story prompt",
        "model": "gpt-3.5-turbo"
    })

    assert response.status_code == 202
    assert response.json()["task_id"] == "llm_test_123"
    assert response.json()["status"] == "PENDING"
```

**Execution Time**: ~1-2 seconds | **API Costs**: None | **Dependencies**: Mocked TaskService

### 4. Integration Tests (`test_integration.py`) - Real LLM APIs

**Purpose**: Validate real LLM provider integration (requires API keys)

**Test Marker**: `@pytest.mark.llm_integration`

**Test Coverage**:

- Real model responses and quality validation
- Provider-specific behavior testing
- Error handling with real API failures
- Performance and token usage validation

**Infrastructure Requirements**:

```bash
# Required environment variables
export OPENAI_API_KEY="your-openai-key"
export DEEPINFRA_API_KEY="your-deepinfra-key"

# Uses testing configuration from llm_config.yaml
```

**Execution Time**: ~2-5 minutes | **API Costs**: Low ($0.01-0.10) | **Dependencies**: Real LLM APIs

### 5. Celery Integration Tests (`test_integration_celery.py`) - 🆕 End-to-End Async

**Purpose**: Test complete async workflows with real Celery workers and LLM APIs

**Test Marker**: `@pytest.mark.celery_integration`

**Infrastructure Requirements**:

```bash
# Start Celery infrastructure
./docker-setup.sh celery    # Redis broker
# Worker included in celery profile   # Celery worker

# Requires LLM API keys for real processing
export OPENAI_API_KEY="your-openai-key"
```

**Test Scenarios**:

```python
@pytest.mark.celery_integration
async def test_real_async_story_generation():
    # Create real task processed by Celery worker with real LLM
    response = await async_client.post("/api/v1/llm/stories/generate", json={
        "prompt": "A short story about async testing",
        "model": "gpt-3.5-turbo"
    })

    task_id = response.json()["task_id"]

    # Poll for real task completion
    for _ in range(60):  # Max 60 seconds for LLM response
        status = await async_client.get(f"/api/v1/tasks/{task_id}")
        if status.json()["status"] in ["SUCCESS", "FAILURE"]:
            break
        await asyncio.sleep(1)

    # Verify real LLM-generated story
    final_result = await async_client.get(f"/api/v1/tasks/{task_id}")
    assert final_result.json()["status"] == "SUCCESS"
    assert len(final_result.json()["result"]["story"]) > 50
```

**Execution Time**: ~3-8 minutes | **API Costs**: Moderate ($0.05-0.30) | **Dependencies**: Celery + Real LLM APIs

## Configuration-Driven Testing

Tests automatically adapt to your `llm_config.yaml` configuration:

### Testing Models Configuration

Add `testing` arrays to task configurations:

```yaml
tasks:
  story_generation:
    primary: 'gpt-4.1-mini'
    fallback: ['meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8']
    testing: ['google/gemma-3-4b-it', 'gpt-4.1-nano'] # ← Integration tests will use these
    description: 'Models optimized for creative writing'

  improvement:
    primary: 'deepseek-ai/DeepSeek-R1-0528'
    fallback: ['gpt-4.1']
    # No 'testing' key = only mock tests for this task
    description: 'High-quality models for text improvement'
```

### Test Settings

Configure test behavior in settings:

```yaml
settings:
  testing:
    enable_integration_tests: true # Global integration test toggle
    test_timeout: 30 # Timeout for integration tests
    mock_responses_by_default: true # Default to mock unless specified
    skip_slow_models: true # Skip expensive models in tests
```

## 🚀 Running LLM Tests

### Fast Development (Mocked Dependencies)

```bash
# Unit tests only (25 tests, ~0.6 seconds)
poetry run pytest tests/llm/test_unit.py -v

# Sync API tests (~10 tests, ~1-2 seconds)
poetry run pytest tests/llm/test_llm_api.py -v

# Async API tests (~15 tests, ~1-2 seconds)
poetry run pytest tests/llm/test_llm_api_async.py -v

# All fast tests (~50 tests, ~3-5 seconds)
poetry run pytest tests/llm/ -m "not llm_integration and not celery_integration" -v
```

### Integration Testing (Real LLM APIs)

```bash
# Requires API keys
export OPENAI_API_KEY="your-openai-key"
export DEEPINFRA_API_KEY="your-deepinfra-key"

# Real LLM integration tests (~7 tests, ~2-5 minutes)
poetry run pytest tests/llm/test_integration.py -v -m llm_integration
```

### Celery Integration Testing (Real Infrastructure + LLM)

```bash
# Start Celery infrastructure
./docker-setup.sh celery
# Worker included in celery profile

# Set API keys
export OPENAI_API_KEY="your-openai-key"

# Real async processing tests (~8 tests, ~3-8 minutes)
poetry run pytest tests/llm/test_integration_celery.py -v -m celery_integration

# All LLM tests including full integration (~65 tests, ~8-15 minutes)
poetry run pytest tests/llm/ -v
```

### Selective Testing Strategies

```bash
# Skip expensive tests (recommended for development)
poetry run pytest tests/llm/ -m "not llm_integration and not celery_integration" -v

# Only integration tests (for pre-deployment validation)
poetry run pytest tests/llm/ -m "llm_integration or celery_integration" -v

# Test specific async functionality
poetry run pytest tests/llm/test_llm_api_async.py tests/llm/test_integration_celery.py -v
```

## 📊 Test Metrics Summary

| Test Category      | File                         | Tests   | Time    | Cost       | Dependencies       |
| ------------------ | ---------------------------- | ------- | ------- | ---------- | ------------------ |
| Unit Tests         | `test_unit.py`               | 25      | ~0.6s   | $0         | None               |
| Sync API           | `test_llm_api.py`            | ~10     | ~1-2s   | $0         | Mocked LLM         |
| Async API          | `test_llm_api_async.py`      | ~15     | ~1-2s   | $0         | Mocked TaskService |
| Integration        | `test_integration.py`        | ~7      | ~5m     | ~$0.10     | Real LLM APIs      |
| Celery Integration | `test_integration_celery.py` | ~8      | ~8m     | ~$0.30     | Celery + LLM APIs  |
| **Total**          | **All Files**                | **~65** | **~5s** | **~$0.40** | **Mixed**          |

_Cost estimates based on OpenAI gpt-3.5-turbo pricing for testing prompts_

## 🔧 Configuration-Driven Testing

Tests automatically adapt to your `llm_config.yaml` configuration:

### For Mock Tests Only

No setup required - mock tests always work.

### For Integration Tests

1. **Set API Keys** (at least one):

   ```bash
   export OPENAI_API_KEY="your-openai-key"
   export DEEPINFRA_API_KEY="your-deepinfra-key"
   export CUSTOM_LLM_API_KEY="your-custom-key"  # if using custom provider
   ```

2. **Configure Testing Models** in `llm_config.yaml`:

   ```yaml
   tasks:
     story_generation:
       testing: ['gpt-4.1-nano', 'google/gemma-3-4b-it'] # Fast, cheap models for testing
   ```

3. **Optional: Disable Integration Tests**:
   ```bash
   export SKIP_LLM_INTEGRATION_TESTS=true
   ```

## Test Coverage

### API Endpoints Tested

| Endpoint          | Mock Tests | Integration Tests | Description                           |
| ----------------- | ---------- | ----------------- | ------------------------------------- |
| `GET /health`     | ✅         | ✅                | Service health and model availability |
| `GET /models`     | ✅         | ✅                | List available models                 |
| `GET /stats`      | ✅         | ⚪                | Usage statistics                      |
| `POST /generate`  | ✅         | ✅                | Story generation                      |
| `POST /analyze`   | ✅         | ✅                | Story analysis                        |
| `POST /summarize` | ✅         | ✅                | Story summarization                   |
| `POST /improve`   | ✅         | ✅                | Story improvement                     |

### Test Scenarios

- ✅ **Request validation**: All required/optional parameters
- ✅ **Response validation**: Correct format, required fields
- ✅ **Error handling**: Invalid inputs, missing data, timeouts
- ✅ **Model selection**: Primary, fallback, and testing model usage
- ✅ **Configuration**: YAML loading, model resolution, task assignments
- ✅ **Service logic**: Initialization, method calls, stats tracking

## Performance Considerations

### Mock Tests

- Target: < 1 second per test
- No external API calls
- Suitable for CI/CD pipelines

### Integration Tests

- Target: < 30 seconds per test
- Real API calls to LLM providers
- May have API costs
- Best for nightly builds or manual runs

## CI/CD Integration

### Fast Pipeline (Every PR)

```bash
# Run only mock tests for fast feedback
poetry run pytest tests/llm/ -m llm_mock --maxfail=1
```

### Full Pipeline (Scheduled/Release)

```bash
# Run all tests including integration
poetry run pytest tests/llm/ -v
```

### Test Environment Variables

```bash
# Fast tests only (default for CI)
SKIP_LLM_INTEGRATION_TESTS=true

# Enable integration tests (with API keys)
OPENAI_API_KEY="..."
DEEPINFRA_API_KEY="..."
```

## Writing New Tests

### 1. Mock Test Template

```python
@pytest.mark.llm_mock
def test_new_feature_mock(self, client: TestClient, mock_llm_service):
    """Test new feature with mock service."""
    with patch('app.routers.llm.get_llm_service_dependency', return_value=mock_llm_service):
        response = client.post("/api/v1/llm/new-endpoint", json={"param": "value"})

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
```

### 2. Integration Test Template

```python
@pytest.mark.llm_integration
@pytest.mark.slow
@pytest.mark.skipif("skip_integration_tests", reason="Integration tests disabled")
def test_new_feature_integration(self, client: TestClient, integration_test_models):
    """Test new feature with real models."""
    testing_models = integration_test_models.get("new_task", [])

    if not testing_models:
        pytest.skip("No testing models configured for new_task")

    for model in testing_models:
        response = client.post("/api/v1/llm/new-endpoint", json={
            "param": "value",
            "model_name": model
        })

        if response.status_code == 200:
            # Validate real response
            data = response.json()
            assert len(data["result"]) > 10  # Reasonable length
        else:
            # Allow graceful failures
            assert response.status_code in [400, 500, 503]
```

### 3. Configuration Test Template

```python
def test_new_config_option(self, llm_config_data):
    """Test new configuration option."""
    assert "new_option" in llm_config_data["settings"]
    assert isinstance(llm_config_data["settings"]["new_option"], bool)
```

## Troubleshooting

### Common Issues

1. **Import Errors**

   ```bash
   # Ensure all dependencies are installed
   poetry install

   # Run tests from project root directory
   poetry run pytest tests/llm/
   ```

2. **API Key Issues**

   ```bash
   # Integration tests automatically check required API keys from llm_config.yaml
   # The system reads 'providers' section and checks 'api_key_env' for each provider

   # Check which providers are configured
   poetry run python -c "
   import yaml
   with open('llm_config.yaml') as f:
       config = yaml.safe_load(f)
       for name, provider in config['providers'].items():
           key_env = provider.get('api_key_env', 'N/A')
           required = provider.get('requires_api_key', False)
           print(f'{name}: {key_env} (required: {required})')
   "

   # Check environment variables dynamically
   poetry run python -c "
   import os, yaml
   with open('llm_config.yaml') as f:
       config = yaml.safe_load(f)
       for name, provider in config['providers'].items():
           if provider.get('requires_api_key', False):
               key_env = provider.get('api_key_env')
               has_key = bool(os.getenv(key_env)) if key_env else False
               print(f'{name} ({key_env}): {'✓' if has_key else '✗'}')
   "

   # Skip integration tests without API keys
   SKIP_LLM_INTEGRATION_TESTS=true poetry run pytest tests/llm/

   # Run only mock tests
   poetry run pytest tests/llm/ -m llm_mock
   ```

3. **Model Availability**

   ```bash
   # Test health endpoint
   curl http://localhost:8080/api/v1/llm/health

   # Check configuration
   poetry run python -c "from app.llm.config import llm_config; print(llm_config.get_available_models())"
   ```

4. **Timeout Issues**

   ```bash
   # Increase test timeout
   poetry run pytest tests/llm/ --timeout=60

   # Skip slow tests
   poetry run pytest tests/llm/ -m "not slow"
   ```

### Debug Mode

```bash
# Verbose output with full tracebacks
poetry run pytest tests/llm/ -vvv --tb=long

# Stop on first failure
poetry run pytest tests/llm/ --maxfail=1

# Run specific test with debugging
poetry run pytest tests/llm/test_llm_api.py::TestLLMGenerateEndpoint::test_generate_story_valid_request -vvv --pdb
```
