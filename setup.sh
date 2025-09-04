#!/bin/bash

echo "🚀 Setting up Perplexity Scraper..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip first."
    exit 1
fi

echo "✅ Python and pip found"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install Python dependencies"
    exit 1
fi

echo "✅ Python dependencies installed"

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
python3 -m playwright install

if [ $? -ne 0 ]; then
    echo "❌ Failed to install Playwright browsers"
    exit 1
fi

echo "✅ Playwright browsers installed"

echo ""
echo "🎉 Setup complete! You can now use the scraper:"
echo ""
echo "  # Run with default prompts:"
echo "  python3 scrape_perplexity_playwright.py"
echo ""
echo "  # Run with your own prompts:"
echo "  python3 scrape_perplexity_playwright.py --prompts-csv sample_prompts.csv"
echo ""
echo "  # Create a login session (if needed):"
echo "  python3 login_once.py"
echo ""
echo "📚 See README.md for more details and examples."
