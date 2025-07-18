#!/bin/bash

# Blossomer CLI Development Install Script
# Clean installation with minimal output

echo "🚀 Installing Blossomer CLI for development..."
echo ""

# Check if we're in a virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "💡 Tip: Consider using a virtual environment:"
    echo "   python -m venv venv && source venv/bin/activate"
    echo ""
fi

# Install with minimal output
echo "📦 Installing dependencies..."
pip install -e . --quiet --disable-pip-version-check

# Check if installation was successful
if [ $? -eq 0 ]; then
    echo "✅ Installation complete!"
    echo ""
    echo "🎯 Try it out:"
    echo "   blossomer --help"
    echo "   blossomer init example.com"
    echo ""
else
    echo "❌ Installation failed. Run with verbose output:"
    echo "   pip install -e ."
    exit 1
fi