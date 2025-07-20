# LLM Tests

This directory contains comprehensive tests for Large Language Model (LLM) functionality in the Story Teller API.

## Test Structure

```
tests/llm/
├── __init__.py              # Package marker
├── conftest_llm.py         # LLM-specific fixtures and configuration
├── test_llm_config.py      # Tests for LLM configuration management
├── test_llm_service.py     # Tests for LLM service implementation
├── test_llm_api.py         # Tests for LLM API endpoints
└── README.md              # This file
```

## Test Categories

### 1. Mock Tests (Fast) - `@pytest.mark.llm_mock`

These tests use mock services and don't make real API calls to LLM providers:

- **API endpoint validation**: Request/response format, parameter validation
- **Error handling**: Invalid inputs, timeout scenarios, service failures
- **Service layer logic**: Method signatures, return values, exception handling
- **Configuration loading**: YAML parsing, model resolution, task assignments

**Advantages:**

- ⚡ Fast execution (< 1 second per test)
- 🔄 Always runnable (no API keys required)
- 🎯 Isolated testing of our code logic
- 💰 No API costs

### 2. Integration Tests (Slow) - `@pytest.mark.llm_integration`

These tests make real calls to configured LLM models from the `testing` configuration:

- **Real model behavior**: Actual story generation, analysis, summarization
- **Model comparison**: Testing multiple models for quality differences
- **Performance validation**: Response times, token usage
- **End-to-end workflows**: Complete request → LLM → response cycles

**Advantages:**

- 🔍 Real-world validation
- 📊 Quality assessment of generated content
- ⚙️ Provider integration testing
- 🚀 Production readiness verification

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

## Running Tests

### Run All LLM Tests

```bash
# All LLM tests (mock + integration if configured)
poetry run pytest tests/llm/ -v

# Using VS Code task
# Ctrl+Shift+P → "Tasks: Run Task" → "Poetry: Run Tests"
```

### Run Only Mock Tests (Fast)

```bash
# Only fast mock tests
poetry run pytest tests/llm/ -m llm_mock -v

# Exclude integration tests
poetry run pytest tests/llm/ -m "not llm_integration" -v
```

### Run Only Integration Tests (Slow)

```bash
# Only real LLM integration tests
poetry run pytest tests/llm/ -m llm_integration -v

# Skip if no API keys
SKIP_LLM_INTEGRATION_TESTS=true poetry run pytest tests/llm/ -v
```

### Run Specific Test Categories

```bash
# Test specific endpoints
poetry run pytest tests/llm/test_llm_api.py::TestLLMGenerateEndpoint -v
poetry run pytest tests/llm/test_llm_api.py::TestLLMAnalyzeEndpoint -v

# Test configuration
poetry run pytest tests/llm/test_llm_config.py -v

# Test service layer
poetry run pytest tests/llm/test_llm_service.py -v
```

## Environment Setup

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

   # Check Python path
   PYTHONPATH=/home/livierek/projekty/story-teller poetry run pytest tests/llm/
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
