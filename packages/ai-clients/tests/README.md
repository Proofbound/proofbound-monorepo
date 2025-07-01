# Test Suite for Book Generator API

This directory contains comprehensive unit tests for the AI-powered book generator API.

## Test Files

### Active Tests
- **`test_models.py`** - Tests for Pydantic models (`Section`, `TOCRequest`)
- **`test_simple_app.py`** - Tests for `simple_app.py` (lightweight version)
- **`conftest.py`** - Shared test fixtures and mock configurations

### Available Tests (Requires Dependencies)
- **`test_app_full.py.skip`** - Comprehensive tests for `app.py` (full version)
  - Rename to `test_app.py` after installing WeasyPrint system dependencies

## Running Tests

### Quick Start
```bash
# Run all available tests
python run_tests.py

# Run specific test files
pytest tests/test_simple_app.py -v
pytest tests/test_models.py -v
```

### Full Test Suite (After Installing WeasyPrint)
```bash
# Install system dependencies (macOS)
brew install python-tk pango gdk-pixbuf libffi gobject-introspection cairo gtk+3

# Set environment variables
export PKG_CONFIG_PATH="/opt/homebrew/lib/pkgconfig:/opt/homebrew/opt/libffi/lib/pkgconfig:$PKG_CONFIG_PATH"
export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"

# Enable full app tests
mv tests/test_app_full.py.skip tests/test_app.py

# Run all tests including full app
pytest tests/ -v
```

## Test Coverage

### Simple App Tests (28 tests)
- ✅ `/test` and `/toc` endpoint functionality
- ✅ Request validation and error handling
- ✅ LLM integration and response parsing
- ✅ Helper function testing
- ✅ Configuration and environment setup

### Model Tests (14 tests)
- ✅ Pydantic model validation
- ✅ Field requirement testing
- ✅ Type validation and conversion
- ✅ Edge cases and error scenarios

### Full App Tests (Available after dependency installation)
- 📋 All endpoints (`/test`, `/toc`, `/draft`, `/pdf`, `/cover`)
- 📋 PDF generation and image processing
- 📋 AI service integration (OpenAI, Replicate)
- 📋 File handling and conversion utilities
- 📋 Complex error scenarios and edge cases

## Test Features

### Mocking Strategy
- **External APIs**: OpenAI and Replicate clients are mocked to avoid costs
- **File Operations**: PDF generation and image processing are mocked
- **Environment**: Test-specific environment variables are injected

### Test Isolation
- Each test runs independently with fresh mocks
- Database/file state is isolated between tests
- External dependencies are mocked to ensure reliability

### Error Testing
- Invalid request data validation
- API failure scenarios
- Malformed response handling
- Missing environment variables

## Contributing

When adding new features:

1. **Add corresponding tests** in the appropriate test file
2. **Mock external dependencies** to avoid costs and improve reliability
3. **Test both success and failure scenarios**
4. **Update this README** if adding new test categories

## Dependencies

### Required (Already in requirements.txt)
- `pytest` - Test framework
- `pytest-asyncio` - Async test support
- `httpx` - FastAPI test client
- `pytest-mock` - Enhanced mocking capabilities

### Optional
- `pytest-cov` - Test coverage reporting
- `pytest-xdist` - Parallel test execution