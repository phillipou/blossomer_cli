# Blossomer CLI Development Makefile
# Cleaner commands for common development tasks

.PHONY: install install-verbose test lint clean dev help

# Default target
help:
	@echo "🌸 Blossomer CLI Development Commands"
	@echo ""
	@echo "📦 Installation:"
	@echo "  make install        Clean installation (recommended)"
	@echo "  make install-verbose Full pip output"
	@echo ""
	@echo "🔧 Development:"
	@echo "  make dev            Install + run example"
	@echo "  make test           Run tests (when available)"
	@echo "  make lint           Run linting (when available)"
	@echo "  make clean          Clean build artifacts"
	@echo ""
	@echo "💡 Quick start: make install && blossomer --help"

# Clean installation with minimal output
install:
	@echo "🚀 Installing Blossomer CLI..."
	@pip install -e . --quiet --disable-pip-version-check
	@echo "✅ Installation complete!"
	@echo ""
	@echo "🎯 Try it out:"
	@echo "   blossomer --help"
	@echo "   blossomer init example.com"

# Verbose installation (original behavior)
install-verbose:
	@echo "🚀 Installing Blossomer CLI (verbose)..."
	pip install -e .

# Development workflow
dev: install
	@echo ""
	@echo "🎯 Running example..."
	@blossomer --help

# Test runner (placeholder)
test:
	@echo "🧪 Running tests..."
	@echo "⚠️  Tests not yet implemented"

# Linting (placeholder)
lint:
	@echo "🔍 Running linting..."
	@echo "⚠️  Linting not yet configured"

# Clean build artifacts
clean:
	@echo "🧹 Cleaning build artifacts..."
	@rm -rf build/
	@rm -rf dist/
	@rm -rf *.egg-info/
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Clean complete!"

# Show current installation status
status:
	@echo "📋 Blossomer CLI Status:"
	@echo ""
	@if command -v blossomer >/dev/null 2>&1; then \
		echo "✅ CLI installed and available"; \
		echo "📍 Location: $$(which blossomer)"; \
		echo "🔖 Version: $$(blossomer --version 2>/dev/null || echo 'Unknown')"; \
	else \
		echo "❌ CLI not found in PATH"; \
		echo "💡 Run 'make install' to install"; \
	fi