# Pull Request

## Description
Brief description of changes and what this PR accomplishes.

Fixes #(issue number) <!-- if applicable -->

## Type of Change
Please check the relevant option:

- [ ] 🐛 **Bug fix** (non-breaking change which fixes an issue)
- [ ] ✨ **New feature** (non-breaking change which adds functionality)
- [ ] 💥 **Breaking change** (fix or feature that would cause existing functionality to not work as expected)
- [ ] 📚 **Documentation** (updates to documentation only)
- [ ] 🧹 **Code cleanup** (refactoring, formatting, removing unused code)
- [ ] ⚡ **Performance** (changes that improve performance)
- [ ] 🔧 **Maintenance** (dependency updates, tooling changes)

## Changes Made
Detailed list of changes:

- [ ] Added/modified function: `function_name()` in `module.py`
- [ ] Updated documentation in `docs/`
- [ ] Added tests in `tests/`
- [ ] Updated examples in `docs/examples/`
- [ ] Modified CLI tool `timecalc`
- [ ] Updated dependencies in `pyproject.toml`

## GPS/Scientific Impact
**If this affects GPS time calculations or scientific accuracy:**

- [ ] **Precision**: Changes maintain microsecond accuracy
- [ ] **Leap seconds**: Leap second handling verified
- [ ] **GPS epoch**: GPS epoch (1980-01-06) compliance verified
- [ ] **Standards**: Complies with GPS/RINEX/GAMIT standards
- [ ] **Backward compatibility**: Existing APIs unchanged

## Testing
Please describe the tests that you ran to verify your changes:

### Test Cases
- [ ] **Unit tests**: All existing tests pass
- [ ] **Integration tests**: Cross-module functionality verified  
- [ ] **Scientific validation**: GPS time accuracy verified
- [ ] **Performance tests**: No performance regressions
- [ ] **Platform tests**: Tested on multiple OS/Python versions

### Test Commands Run
```bash
# List the commands you used to test
pytest tests/ -v
ruff check src/ tests/
mypy src/gtimes/
```

### Test Results
```
# Paste relevant test output here
================================ test session starts ================================
...
================================ X passed in Y.YYs ================================
```

## Code Quality
- [ ] **Linting**: Code passes `ruff check`
- [ ] **Formatting**: Code passes `ruff format --check` 
- [ ] **Type checking**: Code passes `mypy` checks
- [ ] **Documentation**: Functions have proper docstrings
- [ ] **Tests**: New functionality has test coverage
- [ ] **Examples**: Updated examples if applicable

## Performance Impact
If applicable, describe performance implications:

- **Speed**: [No impact/Faster/Slower] - measurement details
- **Memory**: [No impact/Less/More] - memory usage details  
- **Precision**: [Same/Better/Different] - accuracy measurements

```python
# Include any relevant benchmarks
```

## Documentation Updates
- [ ] API documentation updated (auto-generated from docstrings)
- [ ] User guide updated (`docs/guides/`)
- [ ] Examples updated (`docs/examples/`)
- [ ] CHANGELOG.md updated
- [ ] README.md updated (if needed)

## Scientific Validation
**For changes affecting GPS time calculations:**

### Validation Tests
- [ ] Known GPS time conversions verified
- [ ] Round-trip conversion accuracy tested
- [ ] Leap second transitions verified
- [ ] Edge cases tested (GPS epoch, year boundaries)

### Test Data
```python
# Include specific test cases and expected results
test_cases = [
    ((2024, 1, 15, 12, 30, 45), (2297, 216645.0)),
    # Add more test cases
]
```

## Breaking Changes
**If this is a breaking change:**

### What breaks
- List APIs that change
- Describe behavior changes
- Impact on existing code

### Migration guide
```python
# Before (old API)
old_function(params)

# After (new API)  
new_function(updated_params)
```

## Checklist
- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published

## Additional Notes
Any additional information that reviewers should know:

- **Dependencies**: New dependencies added/removed
- **Configuration**: Changes to config files
- **Deployment**: Any deployment considerations
- **Future work**: Related features or improvements planned

---

**Thank you for contributing to GTimes!** 🛰️⏰

Your contribution helps improve GPS time processing for the scientific community.