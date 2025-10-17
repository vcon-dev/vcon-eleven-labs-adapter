#!/bin/bash

# Setup script for live testing the ElevenLabs vCon Adapter

set -e

PROJECT_ROOT=$(cd "$(dirname "$0")" && pwd)
cd "$PROJECT_ROOT"

echo "======================================================================"
echo "  ElevenLabs vCon Adapter - Live Testing Setup"
echo "======================================================================"
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "ERROR: Virtual environment not found at $PROJECT_ROOT/venv"
    echo "Please create it first: python3 -m venv venv"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "Checking dependencies..."
pip install --quiet --upgrade pip setuptools wheel

if [ ! -f "requirements.txt" ]; then
    echo "ERROR: requirements.txt not found"
    exit 1
fi

pip install --quiet -r requirements.txt

# Create config file if it doesn't exist
if [ ! -f "config.yml" ]; then
    echo ""
    echo "Creating config.yml from template..."
    cp config.yml.example config.yml
    echo "  Created config.yml"
    echo "  You can edit this file to customize behavior"
fi

# Create vcons directory
mkdir -p vcons
echo "  Created vcons directory"

echo ""
echo "======================================================================"
echo "  Setup Complete!"
echo "======================================================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Get your ElevenLabs API key from https://elevenlabs.io/app/settings"
echo ""
echo "2. Run the interactive testing tool:"
echo "   source venv/bin/activate"
echo "   python3 test_live.py"
echo ""
echo "3. Or set environment variable and run:"
echo "   export ELEVENLABS_API_KEY='your_api_key_here'"
echo "   python3 examples/basic_usage.py"
echo ""
echo "4. Check the documentation:"
echo "   cat LIVE_TESTING_GUIDE.md"
echo ""
