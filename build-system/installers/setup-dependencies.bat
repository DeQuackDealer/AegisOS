@echo off
:: Aegis OS - Dependency Setup Script
:: Installs required Python packages for development and building

title Aegis OS - Dependency Setup

echo.
echo ========================================
echo    Aegis OS Dependency Setup
echo ========================================
echo.

:: Check for Python
echo Checking for Python...

py --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=py"
    goto :found_python
)

python --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=python"
    goto :found_python
)

python3 --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=python3"
    goto :found_python
)

echo.
echo [ERROR] Python not found!
echo Please install Python 3.11+ from https://www.python.org/downloads/
echo Make sure to check "Add Python to PATH" during installation.
echo.
pause
exit /b 1

:found_python
for /f "tokens=2" %%v in ('%PYTHON_CMD% --version 2^>^&1') do echo Found Python %%v
echo.

:: Upgrade pip
echo [1/3] Upgrading pip...
%PYTHON_CMD% -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo [WARNING] Failed to upgrade pip. Continuing anyway...
)
echo.

:: Install runtime dependencies
echo [2/3] Installing runtime dependencies...
echo      - cryptography (for license verification)
%PYTHON_CMD% -m pip install cryptography
if %errorlevel% neq 0 (
    echo [WARNING] Failed to install cryptography.
)
echo.

:: Install build dependencies
echo [3/3] Installing build dependencies...
echo      - pyinstaller (for creating executables)
%PYTHON_CMD% -m pip install pyinstaller
if %errorlevel% neq 0 (
    echo [WARNING] Failed to install pyinstaller.
)
echo.

:: Verify installations
echo ========================================
echo    Verification
echo ========================================
echo.

echo Checking cryptography...
%PYTHON_CMD% -c "import cryptography; print(f'    Version: {cryptography.__version__}')" 2>nul
if %errorlevel% neq 0 (
    echo    [FAILED] cryptography not installed correctly
) else (
    echo    [OK]
)

echo.
echo Checking pyinstaller...
%PYTHON_CMD% -m PyInstaller --version >nul 2>&1
if %errorlevel% neq 0 (
    echo    [FAILED] pyinstaller not installed correctly
) else (
    for /f "tokens=*" %%v in ('%PYTHON_CMD% -m PyInstaller --version 2^>^&1') do echo    Version: %%v
    echo    [OK]
)

echo.
echo ========================================
echo    Setup Complete
echo ========================================
echo.
echo You can now:
echo   - Run AegisInstaller.bat to launch the installer
echo   - Run "python build-windows.py" to build executables
echo.
pause
