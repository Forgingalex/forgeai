# Contributing to ForgeAI

Thank you for your interest in contributing to ForgeAI! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Coding Conventions](#coding-conventions)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Documentation](#documentation)

## Code of Conduct

This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.9+** (Python 3.13 recommended)
- **Node.js 18+**
- **PostgreSQL 12+**
- **Redis** (optional, for caching and background tasks)
- **Ollama** - Download from [https://ollama.ai/download](https://ollama.ai/download)
- **Git**

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/forgeai.git
   cd forgeai
   ```
3. Add the upstream repository:
   ```bash
   git remote add upstream https://github.com/Forgingalex/ForgeAI.git
   ```

## Development Setup

### 1. Install Ollama

```bash
# Download from https://ollama.ai/download
# Then pull a model:
ollama pull llama3.1:8b
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\Activate.ps1

# Upgrade pip and install dependencies
pip install --upgrade pip setuptools wheel
pip install pydantic-core --only-binary :all:  # Fix for Python 3.13
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your PostgreSQL credentials

# Create PostgreSQL database
createdb forgeai

# Run database migrations
alembic upgrade head

# Start server (development mode)
uvicorn app.main:app --reload
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set up environment
cp .env.example .env.local
# Edit .env.local if needed (defaults work for local development)

# Start dev server
npm run dev
```

### 4. Verify Installation

1. **Backend**: Visit http://localhost:8000/api/docs (Swagger UI)
2. **Frontend**: Visit http://localhost:3000
3. **Ollama**: Run `ollama list` to verify model is installed
4. **Database**: Backend should start without connection errors

## Coding Conventions

### Python (Backend)

#### Code Style

- **Formatter**: [Black](https://black.readthedocs.io/) (line length: 100)
- **Import sorting**: [isort](https://pycqa.github.io/isort/) (Black-compatible)
- **Linter**: [flake8](https://flake8.pycqa.org/)
- **Type checking**: [mypy](https://mypy.readthedocs.io/) (optional, lenient)

#### Formatting Commands

```bash
cd backend

# Format code
make format
# or manually:
black app/ tests/
isort app/ tests/

# Lint code
make lint
# or manually:
flake8 app/ tests/
mypy app/
```

#### Type Hints

- All functions should have type hints
- Use `Optional[T]` for nullable types
- Use `Dict[str, Any]` for dictionaries
- Use `List[T]` for lists

#### Docstrings

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

### TypeScript/JavaScript (Frontend)

#### Code Style

- **Formatter**: [Prettier](https://prettier.io/)
- **Linter**: ESLint (Next.js config)

#### Formatting Commands

```bash
cd frontend

# Format code
npx prettier --write .

# Lint code
npm run lint
```

#### TypeScript Guidelines

- Use TypeScript for all new files
- Avoid `any` types - use proper types or `unknown`
- Use interfaces for object shapes
- Use enums for constants

## Testing

### Backend Tests

```bash
cd backend

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

#### Test Structure

- `tests/unit/`: Unit tests for individual functions
- `tests/integration/`: Integration tests for API endpoints

#### Writing Tests

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

### Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run in watch mode
npm run test:watch

# Run with coverage
npm run test:coverage
```

#### Writing Tests

```typescript
describe('Component', () => {
  it('should render correctly', () => {
    render(<Component />)
    expect(screen.getByText('Hello')).toBeInTheDocument()
  })
})
```

### Coverage Goals

- Aim for >80% code coverage
- Focus on critical paths (auth, file processing, AI)
- Test error cases and edge cases

## Submitting Changes

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Your Changes

- Write clean, well-documented code
- Follow the coding conventions
- Add tests for new features
- Update documentation as needed

### 3. Commit Your Changes

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```bash
git commit -m "feat: add new feature"
git commit -m "fix: resolve bug in authentication"
git commit -m "docs: update README"
git commit -m "test: add tests for new feature"
```

Commit types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### 4. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 5. Create a Pull Request

1. Go to the repository on GitHub
2. Click "New Pull Request"
3. Select your branch
4. Fill out the PR template
5. Submit the PR

### Pull Request Guidelines

- **Title**: Clear, descriptive title using conventional commits format
- **Description**: Explain what changes you made and why
- **Tests**: Ensure all tests pass
- **Documentation**: Update relevant documentation
- **Breaking Changes**: Clearly mark any breaking changes

### Review Process

- All PRs require at least one approval
- Address review comments promptly
- Keep PRs focused and reasonably sized
- Rebase on main if there are conflicts

## Documentation

### Code Documentation

- Add docstrings to all functions
- Document complex logic
- Include examples in docstrings when helpful

### Architecture Documentation

- Document design decisions
- Explain why certain approaches were chosen
- Note trade-offs and future considerations

### API Documentation

- FastAPI automatically generates OpenAPI docs
- Add detailed descriptions to endpoint docstrings
- Include request/response examples

## Code Quality Standards

### Error Handling

- Use custom exceptions (`ForgeAIException` subclasses)
- Log all errors with appropriate levels
- Return user-friendly error messages
- Never expose internal errors to users

### Security

- Never log sensitive information (passwords, tokens)
- Validate all input
- Use parameterized queries (SQLAlchemy handles this)
- Implement rate limiting on sensitive endpoints

### Performance

- Use caching for expensive operations
- Optimize database queries
- Use async/await for I/O operations
- Profile before optimizing

### Logging

- Use structured logging
- Different log levels (DEBUG, INFO, WARNING, ERROR)
- Include context in log messages
- Rotate log files

## Getting Help

- **Documentation**: Check the [README](README.md) and [Architecture docs](docs/ARCHITECTURE.md)
- **Issues**: Search existing issues or create a new one
- **Discussions**: Use GitHub Discussions for questions

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation

Thank you for contributing to ForgeAI! 🎉

