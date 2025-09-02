---
name: Bug report
about: Create a report to help us improve GTimes
title: '[BUG] '
labels: 'bug'
assignees: ''

---

## Bug Description
A clear and concise description of what the bug is.

## To Reproduce
Steps to reproduce the behavior:

1. Import/use this function: `...`
2. With these parameters: `...`
3. Expected result: `...`
4. Actual result: `...`

## Code Example
```python
# Minimal code example that reproduces the issue
from gtimes.gpstime import gpsFromUTC

# Your code here
result = gpsFromUTC(2024, 1, 15, 12, 30, 45)
print(result)
```

## Expected Behavior
A clear and concise description of what you expected to happen.

## Actual Behavior
What actually happened, including any error messages.

```
# If applicable, paste the full error traceback here
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  ...
```

## Environment Information
Please complete the following information:
- **GTimes version**: [e.g., 0.4.0]
- **Python version**: [e.g., 3.11.5]
- **Operating system**: [e.g., Ubuntu 22.04, Windows 11, macOS 14]
- **Installation method**: [e.g., pip, conda, development install]

```bash
# Run this command and paste the output:
python -c "import gtimes; print(f'GTimes: {gtimes.__version__}'); import sys; print(f'Python: {sys.version}'); import platform; print(f'OS: {platform.system()} {platform.release()}')"
```

## GPS Time Context (if applicable)
- **Date/time being converted**: [e.g., 2024-01-15 12:30:45 UTC]
- **Expected GPS time**: [e.g., Week 2297, SOW 216645]
- **GPS application context**: [e.g., RINEX processing, GAMIT analysis]

## Additional Context
- Is this a regression from a previous version?
- Does this affect production GPS processing workflows?
- Are there any workarounds you've discovered?
- Any additional context that might be helpful

## Scientific Impact (if applicable)
- Does this affect scientific accuracy or precision?
- Is this blocking critical GPS research or operations?
- What is the expected precision/accuracy requirement?

## Checklist
- [ ] I have checked the [documentation](https://bgo-ehi.github.io/gtimes)
- [ ] I have searched for similar issues in the [issue tracker](https://github.com/bgo-ehi/gtimes/issues)
- [ ] I have tested this with the latest version of GTimes
- [ ] I have provided a minimal code example that reproduces the issue
- [ ] I have included all relevant environment information

---

**Thank you for helping improve GTimes!** 🛰️

The more details you provide, the faster we can identify and fix the issue.