# .gitignore Configuration

## Overview
A comprehensive `.gitignore` file has been created for the vCon ElevenLabs Adapter project to prevent committing unnecessary or sensitive files to the Git repository.

## What's Ignored

### Python Build & Distribution
- `__pycache__/` - Compiled Python bytecode
- `*.py[cod]` - Compiled files (.pyc, .pyo, .pyd)
- `*.egg-info/` - Egg distribution metadata
- `dist/` - Distribution packages
- `build/` - Build artifacts
- `*.egg` - Egg packages
- Setuptools artifacts

### Virtual Environment
- `venv/` - Main virtual environment directory
- `ENV/` - Alternative venv name
- `env/` - Alternative venv name
- `.venv` - Hidden venv directory

### IDE & Editor
- `.vscode/` - VS Code settings
- `.idea/` - JetBrains IDE (PyCharm, IntelliJ)
- `*.swp` - Vim swap files
- `*.swo` - Vim swap files
- `.DS_Store` - macOS metadata
- `*.sublime-project` - Sublime Text projects
- `*.iml` - IntelliJ module files

### Testing & Coverage
- `.pytest_cache/` - Pytest cache
- `.coverage` - Coverage.py data
- `htmlcov/` - Coverage HTML reports
- `.tox/` - Tox testing artifacts
- `.hypothesis/` - Hypothesis test data
- `.nox/` - Nox testing artifacts

### Environment & Configuration
- `.env` - Environment variables (secrets)
- `.env.local` - Local environment overrides
- `.env.*.local` - Environment-specific local configs
- `config.yml` - Generated configuration
- `config.local.yml` - Local configuration overrides

### Project Artifacts
- `vcons/` - Generated vCon files
- `*.log` - Log files
- `logs/` - Log directory
- `temp/` - Temporary files
- `tmp/` - Temporary files

### OS-Specific
- `.DS_Store` - macOS metadata
- `Thumbs.db` - Windows thumbnail cache
- `.gitkeep` - Git keep files

### Temporary Files
- `*.bak` - Backup files
- `*.tmp` - Temporary files
- `*.orig` - Original files before edits

### Development Tools
- `node_modules/` - Node.js dependencies (if using npm)
- `.vim/`, `.vimrc` - Vim configuration
- `.envrc` - direnv configuration
- `.pylintrc` - Pylint configuration
- `.mypy_cache/` - MyPy type checker cache

## Best Practices

### What NOT to commit:
- Virtual environments (large, machine-specific)
- API keys and secrets (use `.env` files instead)
- Generated build artifacts
- IDE settings (personal to developer)
- Test coverage reports
- Local configuration files
- OS-specific metadata

### What TO commit:
- Source code (`.py` files)
- Configuration templates (`config.yml.example`)
- Documentation
- Tests
- `requirements.txt` / `setup.py`
- `README.md` and other docs
- `.gitignore` itself

## Security

This `.gitignore` prevents accidental commits of:
- `.env` files containing API keys
- Local configuration with credentials
- IDE files with personal settings
- Temporary files with sensitive data

### Additional Steps:
1. Use environment variables for secrets
2. Add `.env.example` as a template
3. Document required environment variables
4. Never commit actual `.env` files
5. Use `.env.local` for machine-specific config

## Size Benefits

Excluding these files saves:
- Virtual environment: 100-500+ MB
- IDE settings: 1-50 MB
- Build artifacts: 10-100+ MB
- Pytest cache: 1-50 MB

**Total potential savings**: 200+ MB per repository

## Git Workflow

### Before pushing:
```bash
git status              # Verify only tracked files shown
git add .
git commit -m "message"
git push
```

### To verify what would be ignored:
```bash
git check-ignore -v <filename>
```

### To see what Git would commit:
```bash
git ls-files
```

## Files Created/Modified

- **Created**: `.gitignore` - Comprehensive ignore rules

## Verification

The `.gitignore` file is now in place and will automatically exclude matching files from Git operations.

---

**Status**: Configured
**Date**: October 17, 2025
**Coverage**: Comprehensive Python project + IDE + testing
