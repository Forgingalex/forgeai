# Testing Guide

## Running Tests

### Backend Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_security.py

# Run specific test
pytest tests/unit/test_security.py::test_password_hashing

# Run with verbose output
pytest -v
```

### Frontend Tests

```bash
# Run all tests
npm test

# Run in watch mode
npm run test:watch

# Run with coverage
npm run test:coverage
```

## Test Structure

### Backend

- `tests/unit/`: Unit tests for individual functions
- `tests/integration/`: Integration tests for API endpoints

### Frontend

- `tests/__tests__/`: Test files for components and utilities

## Writing Tests

### Backend Example

```python
def test_example():
    """Test description."""
    # Arrange
    input_value = "test"
    
    # Act
    result = function_to_test(input_value)
    
    # Assert
    assert result == expected_value
```

### Frontend Example

```typescript
describe('Component', () => {
  it('should render correctly', () => {
    render(<Component />)
    expect(screen.getByText('Hello')).toBeInTheDocument()
  })
})
```

## Coverage Goals

- Aim for >80% code coverage
- Focus on critical paths (auth, file processing, AI)
- Test error cases and edge cases

