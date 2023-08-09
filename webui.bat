@echo off

SET VENV_FOLDER=env
SET REQUIREMENTS_FILE=requirements.txt

REM Check if the virtual environment already exists
IF NOT EXIST %VENV_FOLDER% (
   echo Virtual environment not found. Creating...
   
   REM Create a Python virtual environment
   python -m venv %VENV_FOLDER%
) else (
   echo Virtual environment already exists. Skipping creation.
)

REM Activate the virtual environment
call %VENV_FOLDER%\Scripts\activate.bat

REM Upgrade pip
python -m pip install --upgrade pip

REM Create a temporary file to store installed packages
pip list --format=freeze > installed_packages.txt

for /f "usebackq delims=" %%A in ("%REQUIREMENTS_FILE%") do (
    findstr /x /i /c:"%%~A" installed_packages.txt >nul
    if errorlevel 1 (
        echo Installing requirement %%~A...
        python -m pip install %%~A
    ) else (
        REM Requirement is already satisfied
    )
)

REM Run gui.py
python gui.py

REM Deactivate the virtual environment
deactivate

pause