@echo off
setlocal enabledelayedexpansion

:: Aegis OS Installer Launcher
:: Automatically installs Python and dependencies, then runs the installer
:: Works on Windows 10/11

title Aegis OS Installer

echo.
echo ========================================
echo    Aegis OS Installer Launcher
echo ========================================
echo.

:: Configuration
set "PYTHON_MIN_VERSION=3.11"
set "PYTHON_INSTALLER_URL=https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe"
set "PYTHON_INSTALLER_NAME=python-installer.exe"
set "SCRIPT_DIR=%~dp0"

:: Check for existing Python installation
echo [1/4] Checking for Python installation...

:: Try py launcher first (most reliable on Windows)
py --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=2" %%v in ('py --version 2^>^&1') do set "PY_VERSION=%%v"
    echo      Found Python !PY_VERSION! via py launcher
    set "PYTHON_CMD=py"
    goto :check_version
)

:: Try python command
python --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=2" %%v in ('python --version 2^>^&1') do set "PY_VERSION=%%v"
    echo      Found Python !PY_VERSION!
    set "PYTHON_CMD=python"
    goto :check_version
)

:: Try python3 command
python3 --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=2" %%v in ('python3 --version 2^>^&1') do set "PY_VERSION=%%v"
    echo      Found Python !PY_VERSION!
    set "PYTHON_CMD=python3"
    goto :check_version
)

:: No Python found
echo      Python not found. Installation required.
goto :install_python

:check_version
:: Extract major.minor version
for /f "tokens=1,2 delims=." %%a in ("!PY_VERSION!") do (
    set "MAJOR=%%a"
    set "MINOR=%%b"
)

:: Check if version is 3.11+
if !MAJOR! lss 3 goto :install_python
if !MAJOR! equ 3 if !MINOR! lss 11 goto :install_python

echo      Python version OK (!PY_VERSION!)
goto :install_deps

:install_python
echo.
echo [!] Python %PYTHON_MIN_VERSION%+ is required but not found.
echo.
echo     Options:
echo     1. Download and install Python automatically (requires admin)
echo     2. Cancel and install Python manually from python.org
echo.
set /p CHOICE="Enter choice (1 or 2): "

if "!CHOICE!"=="2" (
    echo.
    echo Please install Python 3.11+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

if not "!CHOICE!"=="1" (
    echo Invalid choice.
    pause
    exit /b 1
)

echo.
echo Downloading Python installer...
echo URL: %PYTHON_INSTALLER_URL%

:: Check for curl or PowerShell for download
where curl >nul 2>&1
if %errorlevel% equ 0 (
    curl -L -o "%TEMP%\%PYTHON_INSTALLER_NAME%" "%PYTHON_INSTALLER_URL%"
) else (
    powershell -Command "(New-Object Net.WebClient).DownloadFile('%PYTHON_INSTALLER_URL%', '%TEMP%\%PYTHON_INSTALLER_NAME%')"
)

if not exist "%TEMP%\%PYTHON_INSTALLER_NAME%" (
    echo.
    echo [ERROR] Failed to download Python installer.
    echo Please download Python manually from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo.
echo Installing Python (this may require administrator privileges)...
echo.

:: Try silent install first (works if already elevated)
"%TEMP%\%PYTHON_INSTALLER_NAME%" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0

if %errorlevel% neq 0 (
    :: Silent install failed, try interactive install
    echo Silent install requires admin rights. Launching interactive installer...
    echo Please check "Add Python to PATH" during installation.
    echo.
    "%TEMP%\%PYTHON_INSTALLER_NAME%"
)

:: Clean up installer
del "%TEMP%\%PYTHON_INSTALLER_NAME%" 2>nul

:: Refresh PATH
set "PATH=%PATH%;%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts"

:: Verify installation
py --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=py"
    echo Python installed successfully.
) else (
    python --version >nul 2>&1
    if %errorlevel% equ 0 (
        set "PYTHON_CMD=python"
        echo Python installed successfully.
    ) else (
        echo.
        echo [ERROR] Python installation may have failed or PATH not updated.
        echo Please restart this script or install Python manually.
        pause
        exit /b 1
    )
)

:install_deps
echo.
echo [2/4] Installing required dependencies...

:: Upgrade pip first
%PYTHON_CMD% -m pip install --upgrade pip --quiet 2>nul

:: Install cryptography (required for licensed installer)
echo      Installing cryptography...
%PYTHON_CMD% -m pip install cryptography --quiet
if %errorlevel% neq 0 (
    echo      [WARNING] Failed to install cryptography. Licensed installer may not work.
) else (
    echo      cryptography installed.
)

:: tkinter is built-in with Python, no need to install

:select_installer
echo.
echo [3/4] Select installer type...
echo.
echo     1. Freemium Edition (no license required)
echo     2. Licensed Edition (requires valid license file)
echo.
set /p INSTALLER_CHOICE="Enter choice (1 or 2): "

if "!INSTALLER_CHOICE!"=="1" (
    set "INSTALLER_SCRIPT=aegis-installer-freemium.py"
    set "INSTALLER_NAME=Freemium"
) else if "!INSTALLER_CHOICE!"=="2" (
    set "INSTALLER_SCRIPT=aegis-installer-licensed.py"
    set "INSTALLER_NAME=Licensed"
) else (
    echo Invalid choice. Using Freemium installer.
    set "INSTALLER_SCRIPT=aegis-installer-freemium.py"
    set "INSTALLER_NAME=Freemium"
)

:run_installer
echo.
echo [4/4] Launching Aegis OS %INSTALLER_NAME% Installer...
echo.

:: Check if installer script exists
if not exist "%SCRIPT_DIR%%INSTALLER_SCRIPT%" (
    echo [ERROR] Installer script not found: %INSTALLER_SCRIPT%
    echo Expected location: %SCRIPT_DIR%%INSTALLER_SCRIPT%
    pause
    exit /b 1
)

:: Run the installer
%PYTHON_CMD% "%SCRIPT_DIR%%INSTALLER_SCRIPT%"

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Installer exited with an error.
    echo Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo ========================================
echo    Installation Complete
echo ========================================
echo.
pause
exit /b 0
