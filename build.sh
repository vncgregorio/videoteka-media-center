#!/bin/bash
# Build script for Videoteka Media Center

set -e

echo "Building Videoteka Media Center..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run tests
echo "Running tests..."
python -m pytest tests/ -v || echo "Tests completed with some failures"

# Check code style (optional, requires black and flake8)
if command -v black &> /dev/null && command -v flake8 &> /dev/null; then
    echo "Checking code style..."
    black --check src/ tests/ || echo "Code style check failed"
    flake8 src/ tests/ || echo "Linting found issues"
fi

echo "Build complete!"
echo ""
echo "To run the application:"
echo "  source venv/bin/activate"
echo "  python -m src.main"
echo ""
echo "To create AppImage:"
echo "  cd packaging/appimage"
echo "  appimage-builder --recipe AppImageBuilder.yml"


