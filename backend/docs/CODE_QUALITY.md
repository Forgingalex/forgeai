# Code Quality Standards

## Overview

This document outlines the code quality standards and practices for ForgeAI.

## Code Style

### Python

- **Formatter**: Black (line length: 100)
- **Import sorting**: isort (Black-compatible)
- **Linter**: flake8
- **Type checking**: mypy (optional, lenient)

### TypeScript/JavaScript

- **Formatter**: Prettier
- **Linter**: ESLint (Next.js config)

## Type Hints

- All functions should have type hints
- Use `Optional[T]` for nullable types
- Use `Dict[str, Any]` for dictionaries
- Use `List[T]` for lists

## Documentation

### Docstrings

All functions should have docstrings following this format:

```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief description of what the function does.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    
    Raises:
        ExceptionType: When this exception is raised
    
    Note:
        Any additional notes or important information
    """
```

### Architecture Documentation

- Document design decisions
- Explain why certain approaches were chosen
- Note trade-offs and future considerations

## Error Handling

- Use custom exceptions (`ForgeAIException` subclasses)
- Log all errors with appropriate levels
- Return user-friendly error messages
- Never expose internal errors to users

## Testing

- Aim for >80% code coverage
- Write unit tests for core functions
- Write integration tests for API endpoints
- Test error cases and edge cases

## Security

- Never log sensitive information (passwords, tokens)
- Validate all input
- Use parameterized queries (SQLAlchemy handles this)
- Implement rate limiting on sensitive endpoints

## Performance

- Use caching for expensive operations
- Optimize database queries
- Use async/await for I/O operations
- Profile before optimizing

## Logging

- Use structured logging
- Different log levels (DEBUG, INFO, WARNING, ERROR)
- Include context in log messages
- Rotate log files

