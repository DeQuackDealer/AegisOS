# Aegis OS Installer Launcher (PowerShell)
# Automatically installs Python and dependencies, then runs the installer
# Works on Windows 10/11 with PowerShell 5.1+

param(
    [switch]$Freemium,
    [switch]$Licensed,
    [switch]$SkipPythonCheck,
    [switch]$Silent
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Configuration
$PythonMinVersion = [version]"3.11.0"
$PythonInstallerUrl = "https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe"
$PythonInstallerPath = Join-Path $env:TEMP "python-installer.exe"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Colors and formatting
function Write-Header {
    param([string]$Message)
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "   $Message" -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
}

function Write-Step {
    param([string]$Step, [string]$Message)
    Write-Host "[$Step] " -ForegroundColor Yellow -NoNewline
    Write-Host $Message
}

function Write-Success {
    param([string]$Message)
    Write-Host "    [OK] " -ForegroundColor Green -NoNewline
    Write-Host $Message
}

function Write-Warning {
    param([string]$Message)
    Write-Host "    [!] " -ForegroundColor Yellow -NoNewline
    Write-Host $Message
}

function Write-Error {
    param([string]$Message)
    Write-Host "    [ERROR] " -ForegroundColor Red -NoNewline
    Write-Host $Message
}

# Check Python installation
function Get-PythonInfo {
    $pythonCommands = @("py", "python", "python3")
    
    foreach ($cmd in $pythonCommands) {
        try {
            $output = & $cmd --version 2>&1
            if ($LASTEXITCODE -eq 0 -and $output -match "Python (\d+\.\d+\.\d+)") {
                return @{
                    Command = $cmd
                    Version = [version]$Matches[1]
                    VersionString = $Matches[1]
                }
            }
        } catch {
            continue
        }
    }
    
    return $null
}

# Download file with progress
function Download-File {
    param(
        [string]$Url,
        [string]$Destination
    )
    
    try {
        Write-Host "    Downloading from: $Url" -ForegroundColor Gray
        
        # Use .NET WebClient for better compatibility
        $webClient = New-Object System.Net.WebClient
        $webClient.DownloadFile($Url, $Destination)
        
        if (Test-Path $Destination) {
            $size = (Get-Item $Destination).Length / 1MB
            Write-Success "Downloaded ($([math]::Round($size, 1)) MB)"
            return $true
        }
    } catch {
        Write-Error "Download failed: $_"
    }
    
    return $false
}

# Install Python
function Install-Python {
    Write-Host ""
    Write-Warning "Python $PythonMinVersion or higher is required but not found."
    Write-Host ""
    
    if (-not $Silent) {
        Write-Host "    Options:" -ForegroundColor White
        Write-Host "    1. Download and install Python automatically" -ForegroundColor White
        Write-Host "    2. Cancel and install Python manually" -ForegroundColor White
        Write-Host ""
        
        $choice = Read-Host "    Enter choice (1 or 2)"
        
        if ($choice -eq "2") {
            Write-Host ""
            Write-Host "    Please install Python 3.11+ from https://www.python.org/downloads/" -ForegroundColor Yellow
            Write-Host "    Make sure to check 'Add Python to PATH' during installation." -ForegroundColor Yellow
            exit 1
        }
        
        if ($choice -ne "1") {
            Write-Error "Invalid choice."
            exit 1
        }
    }
    
    Write-Host ""
    Write-Host "    Downloading Python installer..." -ForegroundColor White
    
    if (-not (Download-File -Url $PythonInstallerUrl -Destination $PythonInstallerPath)) {
        Write-Error "Failed to download Python installer."
        Write-Host "    Please download manually from https://www.python.org/downloads/" -ForegroundColor Yellow
        exit 1
    }
    
    Write-Host ""
    Write-Host "    Installing Python..." -ForegroundColor White
    
    # Check if we have admin rights
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    
    if ($isAdmin -or $Silent) {
        # Silent install (per-user, no admin required)
        $installArgs = "/quiet InstallAllUsers=0 PrependPath=1 Include_test=0"
        Start-Process -FilePath $PythonInstallerPath -ArgumentList $installArgs -Wait -NoNewWindow
    } else {
        # Interactive install
        Write-Host "    Launching Python installer..." -ForegroundColor Gray
        Write-Host "    Please check 'Add Python to PATH' during installation!" -ForegroundColor Yellow
        Start-Process -FilePath $PythonInstallerPath -Wait
    }
    
    # Clean up
    Remove-Item $PythonInstallerPath -Force -ErrorAction SilentlyContinue
    
    # Refresh environment
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
    
    # Add common Python paths
    $pythonPaths = @(
        "$env:LOCALAPPDATA\Programs\Python\Python312",
        "$env:LOCALAPPDATA\Programs\Python\Python312\Scripts",
        "$env:LOCALAPPDATA\Programs\Python\Python311",
        "$env:LOCALAPPDATA\Programs\Python\Python311\Scripts"
    )
    foreach ($p in $pythonPaths) {
        if (Test-Path $p) {
            $env:Path = "$p;$env:Path"
        }
    }
    
    # Verify installation
    $pythonInfo = Get-PythonInfo
    if ($null -eq $pythonInfo) {
        Write-Error "Python installation may have failed or PATH not updated."
        Write-Host "    Please restart this script or install Python manually." -ForegroundColor Yellow
        exit 1
    }
    
    Write-Success "Python $($pythonInfo.VersionString) installed successfully"
    return $pythonInfo
}

# Install dependencies
function Install-Dependencies {
    param([string]$PythonCmd)
    
    Write-Host ""
    Write-Host "    Upgrading pip..." -ForegroundColor Gray
    & $PythonCmd -m pip install --upgrade pip --quiet 2>$null
    
    Write-Host "    Installing cryptography..." -ForegroundColor Gray
    & $PythonCmd -m pip install cryptography --quiet 2>$null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Dependencies installed"
    } else {
        Write-Warning "Some dependencies may not have installed correctly"
    }
}

# Main script
Write-Header "Aegis OS Installer Launcher"

# Step 1: Check Python
Write-Step "1/4" "Checking for Python installation..."

if (-not $SkipPythonCheck) {
    $pythonInfo = Get-PythonInfo
    
    if ($null -eq $pythonInfo) {
        $pythonInfo = Install-Python
    } elseif ($pythonInfo.Version -lt $PythonMinVersion) {
        Write-Warning "Python $($pythonInfo.VersionString) found, but $PythonMinVersion+ required"
        $pythonInfo = Install-Python
    } else {
        Write-Success "Python $($pythonInfo.VersionString) found via '$($pythonInfo.Command)'"
    }
    
    $PythonCmd = $pythonInfo.Command
} else {
    $PythonCmd = "py"
    Write-Success "Skipping Python check (using 'py')"
}

# Step 2: Install dependencies
Write-Step "2/4" "Installing required dependencies..."
Install-Dependencies -PythonCmd $PythonCmd

# Step 3: Select installer
Write-Step "3/4" "Selecting installer type..."

if ($Freemium) {
    $installerScript = "aegis-installer-freemium.py"
    $installerName = "Freemium"
} elseif ($Licensed) {
    $installerScript = "aegis-installer-licensed.py"
    $installerName = "Licensed"
} else {
    Write-Host ""
    Write-Host "    1. Freemium Edition (no license required)" -ForegroundColor White
    Write-Host "    2. Licensed Edition (requires valid license file)" -ForegroundColor White
    Write-Host ""
    
    $choice = Read-Host "    Enter choice (1 or 2)"
    
    if ($choice -eq "2") {
        $installerScript = "aegis-installer-licensed.py"
        $installerName = "Licensed"
    } else {
        $installerScript = "aegis-installer-freemium.py"
        $installerName = "Freemium"
    }
}

Write-Success "Selected $installerName installer"

# Step 4: Run installer
Write-Step "4/4" "Launching Aegis OS $installerName Installer..."

$installerPath = Join-Path $ScriptDir $installerScript

if (-not (Test-Path $installerPath)) {
    Write-Error "Installer script not found: $installerScript"
    Write-Host "    Expected location: $installerPath" -ForegroundColor Gray
    exit 1
}

Write-Host ""
try {
    & $PythonCmd $installerPath
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Installer exited with an error (code: $LASTEXITCODE)"
        exit 1
    }
} catch {
    Write-Error "Failed to launch installer: $_"
    exit 1
}

Write-Header "Installation Complete"
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
