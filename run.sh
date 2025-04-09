#!/bin/bash

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Verify uvicorn installation
if ! command -v uvicorn &> /dev/null; then
    echo "uvicorn not found, installing directly..."
    pip install uvicorn
fi

# Create uploads directory if it doesn't exist
mkdir -p uploads

# Run the FastAPI application
echo "Starting the application..."
python3 -m uvicorn app:app --reload --host 0.0.0.0 --port 8000