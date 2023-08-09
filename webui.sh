#!/bin/bash

apt-get update

apt-get -y install python3-venv

VENV_FOLDER="env"
REQUIREMENTS_FILE="requirements.txt"
IS_COLAB=false
IS_PAPERSPACE=false
THEME="gradio/soft"

if [ ! -d "$VENV_FOLDER" ]; then
  echo "Virtual environment not found. Creating..."
  python3 -m venv "$VENV_FOLDER"
else
  echo "Virtual environment already exists. Skipping creation."
fi

source "$VENV_FOLDER/bin/activate"

python -m pip install --upgrade pip

pip list --format=freeze > installed_packages.txt

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

# Parse command line options
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --iscolab)
            IS_COLAB=true
            shift
            ;;
        --paperspace)
            IS_PAPERSPACE=true
            shift
            ;;
        --theme)
            THEME="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $key"
            ;;
    esac
done

python gui.py --iscolab "$IS_COLAB" --paperspace "$IS_PAPERSPACE" --theme "$THEME"

deactivate

read -p "Press Enter to exit."