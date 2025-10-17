# vCon Import Fix Guide

## Issue

When running tests, you may encounter the following error:

```
ImportError: cannot import name 'Party' from 'vcon'
```

## Root Cause

The vcon library doesn't export `Party` and `Dialog` directly from the main module. They need to be imported from submodules:
- `Party` is in `vcon.party`
- `Dialog` is in `vcon.dialog`

## Solution

### Fixed Imports

Update all imports from:
```python
from vcon import Party, Dialog
```

To:
```python
from vcon.party import Party
from vcon.dialog import Dialog
```

### Files Modified

The following files have been updated with correct imports:

1. `src/transformers/party_mapper.py` - Line 6
2. `src/transformers/dialog_processor.py` - Line 7  
3. `tests/test_transformers.py` - Line 5

### Verification

All imports have been corrected to:

```python
# Correct imports
from vcon import Vcon  # Main vCon class (from main module)
from vcon.party import Party  # Party class (from submodule)
from vcon.dialog import Dialog  # Dialog class (from submodule)
```

## Installation & Testing

### Setup Virtual Environment (Recommended)

```bash
# Create virtual environment
python3.12 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Run Tests

```bash
# Run all tests
pytest

# Run specific test
pytest tests/test_models.py -v

# Run with coverage
pytest --cov=src --cov-report=html
```

## vCon Module Structure

```
vcon/
├── __init__.py          # Exports: Vcon
├── party.py            # Exports: Party, PartyHistory
├── dialog.py           # Exports: Dialog
├── vcon.py             # Main Vcon class
└── ... other modules
```

## Summary

The import errors are now fixed. You can proceed with:

1. Installing dependencies: `pip install -r requirements.txt`
2. Running tests: `pytest`
3. Viewing coverage: `pytest --cov=src --cov-report=html`

---

**Status**: Fixed
**Last Updated**: October 17, 2025
