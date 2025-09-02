# Installation Guide

This guide covers installing GTimes in various environments and configurations.

## Quick Installation

### PyPI Installation (Recommended)

```bash
pip install gtimes
```

### Development Installation

For development work with testing and documentation tools:

```bash
pip install gtimes[dev]
```

### From Source

```bash
git clone https://github.com/vedur/gtimes.git
cd gtimes
pip install -e .
```

## System Requirements

### Python Version Support

GTimes supports Python 3.8 and newer:

- **Python 3.8+**: Full compatibility
- **Python 3.9+**: Recommended  
- **Python 3.10+**: Optimal performance
- **Python 3.11+**: Latest features supported
- **Python 3.12+**: Latest version tested
- **Python 3.13**: Experimental support

### Operating System Support

GTimes works on all major operating systems:

- **Linux**: All distributions (Ubuntu, CentOS, Debian, etc.)
- **macOS**: 10.14+ (including Apple Silicon)
- **Windows**: 10+ (including Windows 11)

## Dependencies

GTimes has minimal dependencies for maximum compatibility:

### Required Dependencies

- **python-dateutil** (≥2.9.0): Timezone handling and date parsing

### Optional Dependencies (Development)

When installing `gtimes[dev]`, additional tools are included:

- **pytest** (≥7.0.0): Testing framework
- **ruff** (≥0.1.0): Code linting and formatting  
- **black** (≥23.0.0): Code formatting
- **mypy** (≥1.0.0): Type checking

## Installation Methods

### 1. Standard Installation

For most users, the standard pip installation is recommended:

```bash
pip install gtimes
```

This installs GTimes with minimal dependencies for production use.

### 2. Development Installation

For contributors or users who want to run tests:

```bash
pip install gtimes[dev]
```

This includes all development and testing tools.

### 3. From Source (Latest)

To get the latest development version:

```bash
# Clone repository
git clone https://github.com/vedur/gtimes.git
cd gtimes

# Install in development mode
pip install -e .

# Or install with development tools
pip install -e .[dev]
```

### 4. Conda/Mamba Installation

GTimes can be installed in conda environments:

```bash
# Create new environment
conda create -n gps_processing python=3.11
conda activate gps_processing

# Install GTimes
pip install gtimes
```

## Virtual Environment Setup

### Using venv

```bash
# Create virtual environment
python -m venv gtimes_env

# Activate (Linux/macOS)
source gtimes_env/bin/activate

# Activate (Windows)
gtimes_env\Scripts\activate

# Install GTimes
pip install gtimes
```

### Using conda

```bash
# Create environment with specific Python version
conda create -n gtimes python=3.11
conda activate gtimes
pip install gtimes
```

### Using mamba (faster)

```bash
# Create environment
mamba create -n gtimes python=3.11
mamba activate gtimes
pip install gtimes
```

## Verification

### Basic Verification

Test that GTimes is properly installed:

```python
import gtimes
print(f"GTimes version: {gtimes.__version__}")

# Test basic functionality
from gtimes.gpstime import gpsFromUTC
result = gpsFromUTC(2024, 1, 1, 12, 0, 0)
print(f"GPS time test: Week {result[0]}, SOW {result[1]}")
```

### Command Line Verification

Test the command-line interface:

```bash
# Check version
timecalc --version

# Test basic functionality
timecalc -wd
```

### Running Tests

If you installed the development version:

```bash
# Run basic tests
pytest tests/ -v

# Run specific test categories
pytest tests/ -m unit
pytest tests/ -m integration

# Run with coverage (if pytest-cov installed)
pytest tests/ --cov=gtimes
```

## Troubleshooting

### Common Installation Issues

#### Issue: `pip install gtimes` fails

**Solution**: Update pip and try again:
```bash
pip install --upgrade pip
pip install gtimes
```

#### Issue: Permission errors on Linux/macOS

**Solution**: Install in user directory:
```bash
pip install --user gtimes
```

#### Issue: Python version compatibility

**Solution**: Check Python version and upgrade if needed:
```bash
python --version
# If < 3.8, upgrade Python or use pyenv/conda
```

#### Issue: Missing command `timecalc`

**Solution**: Ensure pip install location is in PATH:
```bash
# Check installation location
pip show -f gtimes

# Add to PATH if needed (Linux/macOS)
export PATH="$PATH:$HOME/.local/bin"
```

### GPS-Specific Issues

#### Issue: Leap second data seems outdated

**Solution**: GTimes includes historical leap second data up to the release date. For future leap seconds, the library gracefully handles missing data.

#### Issue: GPS time conversions seem incorrect

**Solution**: Verify your input dates and check leap second handling:

```python
from gtimes.gpstime import gpsFromUTC, getleapSecs
import datetime

# Check leap seconds for your date
date = datetime.datetime(2024, 1, 1)
leap_secs = getleapSecs(date, gpst=True)
print(f"Leap seconds: {leap_secs}")

# Test conversion
result = gpsFromUTC(2024, 1, 1, 12, 0, 0)
print(f"GPS time: Week {result[0]}, SOW {result[1]}")
```

### Performance Issues

#### Issue: Slow conversions for large datasets

**Solution**: Use batch processing and consider the following optimizations:

```python
from gtimes.gpstime import gpsFromUTC, leapSecDict

# Pre-load leap second dictionary
leap_dict = leapSecDict()

# Process in batches rather than one at a time
dates = [(2024, 1, i, 12, 0, 0) for i in range(1, 32)]
gps_times = [gpsFromUTC(*date) for date in dates]
```

## Environment-Specific Instructions

### Scientific Computing Environments

#### Jupyter/IPython

GTimes works seamlessly in Jupyter notebooks:

```python
# Install in Jupyter
!pip install gtimes

# Use with plotting
import matplotlib.pyplot as plt
from gtimes.timefunc import dTimetoYearf
import datetime

# Create time series
dates = [datetime.datetime(2024, 1, i) for i in range(1, 32)]
yearfs = [dTimetoYearf(d) for d in dates]
plt.plot(yearfs)
plt.title("Fractional Year Time Series")
```

#### Research Computing Clusters

For HPC environments with limited internet access:

```bash
# Download wheel file locally, then transfer
pip download gtimes

# On cluster, install from wheel
pip install gtimes-*.whl
```

### Production Deployment

#### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install GTimes
RUN pip install gtimes

# Copy your GPS processing scripts
COPY . /app

CMD ["python", "your_gps_script.py"]
```

#### Requirements File

For reproducible deployments:

```txt
# requirements.txt
gtimes>=0.3.3
python-dateutil>=2.9.0
```

```bash
pip install -r requirements.txt
```

## Integration with Other Tools

### GAMIT/GLOBK Integration

GTimes is designed to work with GAMIT/GLOBK workflows:

```python
# Convert GAMIT fractional years
from gtimes.timefunc import TimefromYearf, dTimetoYearf

# Read GAMIT time series (example)
gamit_years = [2024.0, 2024.0274, 2024.0548]  # From GAMIT output
datetimes = [TimefromYearf(y) for y in gamit_years]
```

### RINEX Processing

For RINEX file processing workflows:

```python
# Generate RINEX filenames
from gtimes.timefunc import datepathlist
import datetime

start = datetime.datetime(2024, 1, 1)
end = datetime.datetime(2024, 1, 8)

rinex_files = datepathlist("REYK%j0.%yO", "1D", start, end)
```

## Development Setup

### Complete Development Environment

For contributors:

```bash
# Clone repository
git clone https://github.com/vedur/gtimes.git
cd gtimes

# Create development environment
python -m venv dev_env
source dev_env/bin/activate  # Linux/macOS
# dev_env\Scripts\activate    # Windows

# Install in development mode with all tools
pip install -e .[dev]

# Run tests
pytest tests/

# Run linting
ruff check src/
black --check src/

# Run type checking
mypy src/
```

### Pre-commit Hooks

Set up pre-commit hooks for code quality:

```bash
# Install pre-commit
pip install pre-commit

# Set up hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

## Next Steps

After installation, you can:

1. **[Follow the Quick Start Guide](quickstart.md)** for basic usage
2. **[Read GPS Concepts](gps-concepts.md)** to understand GPS time systems  
3. **[Explore Examples](../examples/basic-usage.md)** for real-world applications
4. **[Check API Reference](../api/gpstime.md)** for detailed documentation

## Support

If you encounter issues:

1. Check this troubleshooting section
2. Review the [GitHub Issues](https://github.com/vedur/gtimes/issues)
3. Create a new issue with:
   - Python version (`python --version`)
   - Operating system
   - GTimes version (`pip show gtimes`)
   - Complete error message
   - Minimal code example that reproduces the issue