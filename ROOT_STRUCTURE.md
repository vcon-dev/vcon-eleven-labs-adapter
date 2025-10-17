# Project Root Directory Structure

This document explains the organization of the project root directory.

## Essential Files in Root

```
/
├── README.md                    # Main project README
├── LICENSE                      # MIT License
├── CONTRIBUTING.md              # Contribution guidelines
├── CODE_OF_CONDUCT.md           # Community Code of Conduct
├── ROOT_STRUCTURE.md            # This file
│
├── requirements.txt             # Python dependencies
├── setup.py                     # Package setup
├── pytest.ini                   # Pytest configuration
├── config.yml.example           # Configuration template
│
├── .gitignore                   # Git ignore rules
├── .github/                     # GitHub configuration
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── PULL_REQUEST_TEMPLATE/
│       └── pull_request_template.md
```

## Main Directories

### /docs/ - Complete Documentation
**Complete GitBook-ready documentation** with 15 files and 4,369+ lines.
- Installation guide
- Quick start
- Configuration reference
- Complete user guide
- 13+ code examples
- API reference
- Testing guide
- Debugging guide
- Architecture overview
- Status & metrics

See: `docs/README.md`

### /src/ - Source Code
Production code organized by component:
- Adapter main class
- Configuration management
- Logging infrastructure
- Extractors (ElevenLabs API)
- Transformers (vCon conversion)
- Exporters (File, S3, Webhook)
- Data models

### /tests/ - Test Suite
Comprehensive test suite with 130+ tests and 90%+ coverage:
- Fixtures and configuration
- Model tests (50+)
- Extractor tests (25+)
- Transformer tests (25+)
- Exporter tests (30+)

### /examples/ - Usage Examples
Practical code examples:
- basic_usage.py

### /.archive/ - Historical Documentation
Old development notes and logs (for reference only):
- Build notes
- Testing summaries
- API fixes
- Progress tracking
- Application logs

## Project Files

### Configuration
- `config.yml.example` - Configuration template for users
- `pytest.ini` - Pytest test configuration

### Package Management
- `setup.py` - Package metadata and installation
- `requirements.txt` - Python dependencies (11 packages)

### Documentation Files
- `README.md` - Main project README
- `LICENSE` - MIT License (open source)
- `CONTRIBUTING.md` - How to contribute
- `CODE_OF_CONDUCT.md` - Community standards
- `ROOT_STRUCTURE.md` - This file

### GitHub Integration
- `.github/ISSUE_TEMPLATE/bug_report.md` - Bug report template
- `.github/ISSUE_TEMPLATE/feature_request.md` - Feature request template
- `.github/PULL_REQUEST_TEMPLATE/pull_request_template.md` - PR template

## Clean Root Guidelines

### Keep Root Clean
- Only essential files in root
- One README pointing to docs/
- Configuration examples only
- License and contributing files
- GitHub workflows and templates

### What Goes Where

| Item | Location |
|------|----------|
| User documentation | `/docs/` |
| Code | `/src/` |
| Tests | `/tests/` |
| Examples | `/examples/` |
| Old notes | `/.archive/` |
| Configuration templates | Root (*.example) |
| Licenses/legal | Root |
| Contribution info | Root |
| GitHub templates | `/.github/` |

## Quick Navigation

### For Users
- **Getting started**: See `docs/01-getting-started/`
- **How to use**: See `docs/02-usage/`
- **Configuration**: See `docs/01-getting-started/configuration.md`
- **Examples**: See `docs/02-usage/examples.md`

### For Developers
- **Source code**: See `src/`
- **Tests**: See `tests/`
- **Contributing**: See `CONTRIBUTING.md`
- **Architecture**: See `docs/04-advanced/architecture.md`

### For Maintainers
- **Issues**: Use templates in `.github/ISSUE_TEMPLATE/`
- **PRs**: Use template in `.github/PULL_REQUEST_TEMPLATE/`
- **Contributing**: Update `CONTRIBUTING.md`
- **Code of conduct**: Update `CODE_OF_CONDUCT.md`

## Version Control

### .gitignore Coverage
The project uses a standard `.gitignore` that excludes:
- Python cache and bytecode
- Virtual environment
- IDE files
- OS files
- Build artifacts
- Logs (except examples)

### .archive/ Behavior
The `.archive/` directory contains historical documentation:
- Not critical for current operations
- Can be excluded from distribution
- Useful for reference only

## Maintenance

### Adding New Files
1. **Documentation**: Add to `docs/`
2. **Code**: Add to `src/`
3. **Tests**: Add to `tests/`
4. **Legal/Meta**: Add to root or `/.github/`

### Updating Documentation
1. Modify files in `docs/`
2. Update `docs/SUMMARY.md` if needed
3. Update root `README.md` if needed
4. All changes auto-sync if using GitBook

### Adding Templates
1. Bug templates: `/.github/ISSUE_TEMPLATE/`
2. PR templates: `/.github/PULL_REQUEST_TEMPLATE/`
3. Workflow files: `/.github/workflows/`

## Summary

The root directory is now **clean and organized** with:

- Essential metadata files
- Configuration templates
- Links to comprehensive documentation
- GitHub integration templates
- Old development docs archived
- All content properly organized

All current user and developer information is in `/docs/`.

---

**Last Updated**: October 17, 2025
**Status**: Clean and organized for production
