#!/bin/bash
# setup.sh — create a virtual environment, install dependencies,
# and prepare the .env file in one step.

set -e

echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

if [ ! -f .env ]; then
    cp .env.example .env
    echo ""
    echo "A .env file has been created from .env.example."
    echo "Open it and add your ANTHROPIC_API_KEY and TAVILY_API_KEY before running the agent."
else
    echo ".env already exists — skipping."
fi

echo ""
echo "Setup complete. To activate the environment run:"
echo "  source venv/bin/activate"
echo ""
echo "Then run the agent:"
echo "  python main.py --query \"What is 17 * 34?\""
