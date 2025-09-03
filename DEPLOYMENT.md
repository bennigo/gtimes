# GTimes Deployment Guide

This guide covers deploying the GTimes package to PyPI using modern best practices.

## PyPI Authentication

### Recommended: API Tokens

API tokens are the secure, modern way to authenticate with PyPI:

1. **Create API Tokens:**
   - [Test PyPI](https://test.pypi.org/manage/account/token/): Create token for testing
   - [Production PyPI](https://pypi.org/manage/account/token/): Create token for production

2. **Set Environment Variables:**
   ```bash
   # For Test PyPI
   export TEST_PYPI_API_TOKEN="pypi-AgEIcHlwaS5vcmcC..."
   
   # For Production PyPI  
   export PYPI_API_TOKEN="pypi-AgEIcHlwaS5vcmcC..."
   ```

3. **Deploy:**
   ```bash
   # Test deployment (uses TEST_PYPI_API_TOKEN)
   python3 scripts/deploy_to_pypi.py --test-only
   
   # Full deployment (uses both tokens)
   python3 scripts/deploy_to_pypi.py
   ```

### Manual Upload (Alternative)

If you prefer manual control:

```bash
# Build package
python3 -m build

# Upload to Test PyPI
python3 -m twine upload --repository testpypi dist/* --username __token__ --password $TEST_PYPI_API_TOKEN

# Upload to Production PyPI
python3 -m twine upload dist/* --username __token__ --password $PYPI_API_TOKEN
```

## Deployment Process

The deployment script performs these steps:

1. **Validation** - Runs comprehensive package validation
2. **Build** - Creates wheel and source distributions
3. **Test Installation** - Tests installation in clean environment
4. **Test PyPI Upload** - Deploys to Test PyPI first
5. **Production PyPI** - Optionally deploys to production PyPI

## Security Benefits of API Tokens

- ✅ **Scoped Access** - Can be limited to specific projects
- ✅ **Revocable** - Can be revoked without changing password
- ✅ **Audit Trail** - Better logging of API usage
- ✅ **No Password Exposure** - Tokens don't reveal account passwords
- ✅ **Automation Friendly** - Perfect for CI/CD pipelines

## CI/CD Integration

For automated deployments, add tokens as repository secrets:

```yaml
# GitHub Actions example
- name: Deploy to PyPI
  env:
    TEST_PYPI_API_TOKEN: ${{ secrets.TEST_PYPI_API_TOKEN }}
    PYPI_API_TOKEN: ${{ secrets.PYPI_API_TOKEN }}
  run: python3 scripts/deploy_to_pypi.py
```

## Troubleshooting

### Common Issues

1. **"Invalid credentials"** - Check token format (should start with `pypi-`)
2. **"Package already exists"** - Increment version number in `pyproject.toml`
3. **"Upload failed"** - Check internet connection and PyPI status

### Token Management

- Store tokens securely (password manager, environment variables)
- Don't commit tokens to version control
- Rotate tokens periodically for security
- Use project-scoped tokens when possible

## Verification

After deployment, verify your package:

```bash
# Test PyPI
pip install --index-url https://test.pypi.org/simple/ gtimes

# Production PyPI
pip install gtimes
```