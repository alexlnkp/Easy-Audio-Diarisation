#!/bin/bash

VENV_FOLDER="env"
REQUIREMENTS_FILE="requirements.txt"

# Check if the virtual environment already exists
if [ ! -d "$VENV_FOLDER" ]; then
  echo "Virtual environment not found. Creating..."
  
  # Create a Python virtual environment
  python3 -m venv "$VENV_FOLDER"
else
  echo "Virtual environment already exists. Skipping creation."
fi

# Activate the virtual environment
source "$VENV_FOLDER/Scripts/activate"

# Upgrade pip
python -m pip install --upgrade pip

# Create a temporary file to store installed packages
pip list --format=freeze > installed_packages.txt

# Install missing requirements
while IFS= read -r requirement || [ -n "$requirement" ]; do
  grep -x -i -q "$requirement" installed_packages.txt
  if [ $? -ne 0 ]; then
    echo "Installing requirement $requirement..."
    python -m pip install "$requirement"
  else
    # Requirement is already satisfied
    :
  fi
done < "$REQUIREMENTS_FILE"

# Run gui.py
python gui.py

# Deactivate the virtual environment
deactivate

read -p "Press Enter to exit."