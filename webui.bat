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

REM Install requirements if not already satisfied
setlocal enabledelayedexpansion

for /f "usebackq delims=" %%A in ("%REQUIREMENTS_FILE%") do (
    python -c "import pkg_resources; pkg = pkg_resources.get_distribution('%%~A'); exit(1)" >nul 2>nul
    if errorlevel 1 (
        REM Requirement %%~A already satisfied
    ) else (
        echo Installing requirement %%~A...
        pip install %%~A
    )
)

REM Run gui.py
python gui.py

REM Deactivate the virtual environment
deactivate

pause