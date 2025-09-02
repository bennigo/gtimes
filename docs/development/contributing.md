# Contributing to GTimes

Thank you for your interest in contributing to GTimes! This guide will help you get started with contributing to this GPS time processing library.

## Development Setup

### Prerequisites

- Python 3.8 or newer
- Git
- Basic understanding of GPS time systems (helpful but not required)

### Setting Up Development Environment

1. **Fork and clone the repository**:
   ```bash
   git clone https://github.com/your-username/gtimes.git
   cd gtimes
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv dev_env
   source dev_env/bin/activate  # Linux/macOS
   # dev_env\Scripts\activate    # Windows
   ```

3. **Install in development mode**:
   ```bash
   pip install -e .[dev,docs]
   ```

4. **Verify installation**:
   ```bash
   pytest tests/ -v
   ```

## Code Standards

### Code Style

GTimes follows these code standards:

- **Python Style**: PEP 8 compliant
- **Line Length**: 88 characters (Black formatter)
- **Import Order**: isort compatible
- **Type Hints**: Comprehensive type annotations required
- **Docstrings**: Google style docstrings for all public functions

### Tools Used

- **ruff**: Fast Python linter and formatter
- **black**: Code formatter  
- **mypy**: Static type checking
- **pytest**: Testing framework

### Running Code Quality Tools

```bash
# Lint code
ruff check src/ tests/

# Format code
black src/ tests/

# Type checking
mypy src/

# Run all checks
ruff check src/ && black --check src/ && mypy src/
```

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test categories
pytest tests/ -m unit
pytest tests/ -m integration
pytest tests/ -m performance

# Run with coverage
pytest tests/ --cov=gtimes

# Run tests for specific module
pytest tests/test_gpstime_comprehensive.py -v
```

### Test Categories

GTimes uses pytest markers to categorize tests:

- `unit`: Individual function testing
- `integration`: Multi-component workflows
- `performance`: Speed and efficiency tests
- `validation`: Input validation and error handling
- `edge_cases`: Boundary conditions
- `slow`: Long-running tests (optional with `--runslow`)

### Writing Tests

When adding new functionality, include comprehensive tests:

```python
import pytest
from gtimes.gpstime import your_new_function
from gtimes.exceptions import GPSTimeError

class TestYourNewFunction:
    """Test your new function."""
    
    @pytest.mark.unit
    def test_basic_functionality(self):
        """Test basic function behavior."""
        result = your_new_function(input_data)
        assert result == expected_result
    
    @pytest.mark.validation
    def test_input_validation(self):
        """Test input validation."""
        with pytest.raises(GPSTimeError):
            your_new_function(invalid_input)
    
    @pytest.mark.edge_cases
    def test_edge_cases(self):
        """Test edge cases and boundaries."""
        # Test boundary conditions
        pass
```

## Contribution Guidelines

### Types of Contributions

We welcome several types of contributions:

1. **Bug Reports**: Issues with existing functionality
2. **Feature Requests**: New GPS time processing capabilities
3. **Code Contributions**: Bug fixes, new features, optimizations
4. **Documentation**: Improvements to docs, examples, tutorials
5. **Testing**: Additional test cases, test coverage improvements

### Before Contributing

1. **Check existing issues**: Look for similar issues or feature requests
2. **Discuss major changes**: Open an issue to discuss significant changes before implementing
3. **Follow conventions**: Maintain consistency with existing code style
4. **Add tests**: Ensure your changes include appropriate tests
5. **Update documentation**: Include documentation updates for new features

### Pull Request Process

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**:
   - Follow code standards
   - Add comprehensive tests
   - Update documentation
   - Ensure backward compatibility

3. **Run quality checks**:
   ```bash
   # Run tests
   pytest tests/
   
   # Check code quality
   ruff check src/ tests/
   black --check src/ tests/
   mypy src/
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add new GPS time feature
   
   - Implement new function for XYZ
   - Add comprehensive tests
   - Update documentation
   - Maintain backward compatibility"
   ```

5. **Push and create pull request**:
   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Message Format

Use conventional commits format:

```
type(scope): brief description

Detailed description of changes including:
- What was changed
- Why it was changed  
- Any breaking changes
- Testing performed
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `chore`: Maintenance tasks

## Code Architecture

### Module Structure

```
src/gtimes/
├── gpstime.py      # Core GPS time conversions
├── timefunc.py     # Time utility functions  
├── timecalc.py     # Command-line interface
├── exceptions.py   # Custom exceptions and validation
└── __init__.py     # Package initialization
```

### Key Principles

1. **Backward Compatibility**: Never break existing APIs
2. **Scientific Accuracy**: Maintain microsecond precision
3. **Minimal Dependencies**: Keep external dependencies minimal
4. **Performance**: Optimize for batch processing
5. **Error Handling**: Provide informative error messages
6. **Type Safety**: Comprehensive type hints

### Adding New Functions

When adding new functions:

1. **Choose the right module**:
   - `gpstime.py`: Core GPS ↔ UTC conversions
   - `timefunc.py`: Utility functions and workflows
   - `exceptions.py`: Validation and error handling

2. **Follow naming conventions**:
   - Functions: `camelCase` (historical GPS conventions)
   - Variables: `snake_case`
   - Constants: `UPPER_CASE`

3. **Include comprehensive docstrings**:
   ```python
   def new_gps_function(param1: int, param2: float) -> tuple[int, float]:
       """Brief description of the function.
       
       Longer description explaining the GPS time processing context,
       scientific background, and use cases.
       
       Args:
           param1: Description with valid ranges
           param2: Description with units and precision
           
       Returns:
           Tuple containing (result1, result2) with descriptions
           
       Raises:
           GPSTimeError: When input validation fails
           ValidationError: For specific validation errors
           
       Example:
           >>> result = new_gps_function(2024, 45.123)
           >>> print(result)
           (2297, 216645.123)
       """
   ```

4. **Add input validation**:
   ```python
   from .exceptions import validate_gps_week, GPSTimeError
   
   def new_gps_function(gps_week: int) -> int:
       try:
           gps_week = validate_gps_week(gps_week)
       except ValidationError as e:
           raise GPSTimeError(f"Invalid input: {e}") from e
   ```

## Scientific Background

### GPS Time System

Understanding GPS time is crucial for contributions:

- **GPS Epoch**: January 6, 1980, 00:00:00 UTC
- **No Leap Seconds**: GPS time is continuous
- **Week Rollovers**: GPS weeks roll over every 1024 weeks
- **Precision**: Microsecond-level accuracy required

### Key Concepts

1. **GPS Week**: Weeks since GPS epoch (full weeks, not modulo 1024)
2. **Seconds of Week (SOW)**: 0-604799 seconds within GPS week
3. **Leap Seconds**: Difference between GPS time and UTC
4. **Fractional Years**: GAMIT/GLOBK time representation

## Documentation

### Building Documentation

```bash
# Install documentation tools
pip install -e .[docs]

# Build documentation
mkdocs build

# Serve locally  
mkdocs serve
```

### Documentation Standards

- **API Documentation**: Auto-generated from docstrings
- **Examples**: Practical, real-world usage scenarios
- **Scientific Context**: Explain GPS time concepts
- **Code Quality**: All examples must be tested

### Adding Documentation

1. **API Changes**: Update docstrings in source code
2. **New Features**: Add examples to `docs/examples/`
3. **Concepts**: Add explanations to `docs/concepts/`
4. **Tutorials**: Add step-by-step guides to `docs/guides/`

## Release Process

### Version Management

GTimes uses semantic versioning (SemVer):

- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

### Release Checklist

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Run full test suite
4. Build and test documentation
5. Create release PR
6. Tag release after merge
7. Publish to PyPI

## Getting Help

### Communication Channels

- **Issues**: GitHub issues for bugs and feature requests
- **Discussions**: GitHub discussions for questions
- **Email**: Contact maintainers for sensitive issues

### Resources

- **GPS Time Concepts**: `docs/concepts/gps-time-systems.md`
- **API Reference**: `docs/api/`
- **Examples**: `docs/examples/`
- **Testing Guide**: `docs/development/testing.md`

## Code Review Process

### What We Look For

1. **Correctness**: Does the code work as intended?
2. **Tests**: Are there comprehensive tests?
3. **Documentation**: Is the code well-documented?
4. **Performance**: Are there performance implications?
5. **Compatibility**: Is backward compatibility maintained?
6. **Style**: Does it follow project conventions?

### Review Criteria

- **Scientific Accuracy**: GPS time calculations must be precise
- **Error Handling**: Proper validation and informative errors
- **Type Safety**: Complete type annotations
- **Test Coverage**: New code must include tests
- **Documentation**: Public functions need docstrings

## Specific Contribution Areas

### High Priority

1. **Performance Optimizations**: Batch processing improvements
2. **Additional Validations**: More robust input validation
3. **RINEX Support**: Enhanced RINEX file processing
4. **Documentation**: More examples and tutorials
5. **Testing**: Edge cases and performance tests

### Medium Priority

1. **New Time Formats**: Additional GPS time representations
2. **Utility Functions**: GPS processing workflow helpers
3. **Error Messages**: More informative error context
4. **CLI Enhancements**: Additional command-line features

### Advanced Contributions

1. **Algorithm Optimizations**: Faster GPS time algorithms
2. **Memory Optimizations**: Reduced memory usage for large datasets
3. **Integration Features**: Better GAMIT/GLOBK compatibility
4. **Scientific Extensions**: Additional coordinate systems

## Recognition

Contributors are recognized in:

- **README.md**: Contributor list
- **CHANGELOG.md**: Release notes
- **Documentation**: Author attribution
- **Git History**: Permanent contribution record

Thank you for contributing to GTimes and improving GPS time processing for the scientific community!