<#
.SYNOPSIS
    Aegis OS Build Script for Windows using WSL2

.DESCRIPTION
    This PowerShell script builds Aegis OS ISO images using WSL2 (Ubuntu).
    It handles prerequisite checks, dependency installation, and build execution.

.PARAMETER Edition
    The Aegis OS edition to build. Valid options:
    - freemium (Free edition)
    - basic (Basic productivity)
    - workplace (Office workstation)
    - gamer (Gaming edition)
    - ai (AI Developer edition)
    - gamer-ai (Gaming + AI combo)
    - server (Enterprise server)

.PARAMETER OutputFolder
    The Windows folder where the ISO will be saved.
    Defaults to $HOME\Documents\AegisOS-Builds

.PARAMETER Simulate
    Run in simulation mode (no actual ISO created).
    Useful for testing the build process.

.PARAMETER RealBuild
    Force real build mode (creates actual bootable ISO).
    Requires root access in WSL.

.PARAMETER InstallDeps
    Install build dependencies in WSL before building.

.PARAMETER CheckOnly
    Only check prerequisites without building.

.PARAMETER Verbose
    Show detailed build output.

.EXAMPLE
    .\aegis-builder.ps1 -Edition freemium -Simulate
    Run a simulation build of the Freemium edition.

.EXAMPLE
    .\aegis-builder.ps1 -Edition gamer -RealBuild -OutputFolder "D:\ISOs"
    Build a real Gamer edition ISO and save to D:\ISOs

.EXAMPLE
    .\aegis-builder.ps1 -CheckOnly
    Check if all prerequisites are met.

.NOTES
    Author: Aegis OS Team
    Version: 2.0.0
    Requires: Windows 10/11 with WSL2 and Ubuntu installed
#>

[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [ValidateSet('freemium', 'basic', 'workplace', 'gamer', 'ai', 'gamer-ai', 'server')]
    [string]$Edition = 'freemium',
    
    [Parameter()]
    [string]$OutputFolder = "$HOME\Documents\AegisOS-Builds",
    
    [Parameter()]
    [switch]$Simulate,
    
    [Parameter()]
    [switch]$RealBuild,
    
    [Parameter()]
    [switch]$InstallDeps,
    
    [Parameter()]
    [switch]$CheckOnly,
    
    [Parameter()]
    [switch]$VerboseOutput
)

$ErrorActionPreference = 'Stop'
$Version = "2.0.0"

# Edition descriptions
$EditionInfo = @{
    'freemium'  = @{ Name = 'Freemium'; Size = '1.5 GB'; Desc = 'Basic Linux with XFCE desktop - Free edition' }
    'basic'     = @{ Name = 'Basic'; Size = '3.5 GB'; Desc = 'Professional productivity suite with development tools' }
    'workplace' = @{ Name = 'Workplace'; Size = '3 GB'; Desc = 'Professional workstation for office environments' }
    'gamer'     = @{ Name = 'Gamer'; Size = '4.5 GB'; Desc = 'Ultimate gaming with Steam, Lutris, Wine/Proton' }
    'ai'        = @{ Name = 'AI Developer'; Size = '6 GB'; Desc = 'Complete AI/ML development platform with CUDA support' }
    'gamer-ai'  = @{ Name = 'Gamer+AI'; Size = '7 GB'; Desc = 'Ultimate gaming and AI development combo' }
    'server'    = @{ Name = 'Server'; Size = '3 GB'; Desc = 'Enterprise-grade server with security hardening' }
}

# Required build tools
$RequiredTools = @('debootstrap', 'mksquashfs', 'xorriso', 'rsync')

function Write-Header {
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║            ⚔️  AEGIS OS BUILDER v$Version                      ║" -ForegroundColor Cyan
    Write-Host "║         Build Aegis OS ISOs using WSL2 on Windows            ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Status {
    param(
        [string]$Message,
        [ValidateSet('Info', 'Success', 'Warning', 'Error')]
        [string]$Type = 'Info'
    )
    
    $symbol = switch ($Type) {
        'Info'    { '►'; $color = 'Cyan' }
        'Success' { '✓'; $color = 'Green' }
        'Warning' { '⚠'; $color = 'Yellow' }
        'Error'   { '✗'; $color = 'Red' }
    }
    
    $timestamp = Get-Date -Format 'HH:mm:ss'
    Write-Host "[$timestamp] " -NoNewline -ForegroundColor DarkGray
    Write-Host "$symbol " -NoNewline -ForegroundColor $color
    Write-Host $Message -ForegroundColor $color
}

function Test-WSL2 {
    Write-Status "Checking WSL2 installation..." -Type Info
    
    try {
        $wslVersion = wsl --version 2>&1
        if ($LASTEXITCODE -eq 0 -and $wslVersion -match 'WSL') {
            Write-Status "WSL2 is installed" -Type Success
            return $true
        }
    }
    catch {
        # WSL not available
    }
    
    Write-Status "WSL2 is NOT installed" -Type Error
    Write-Host ""
    Write-Host "  To install WSL2, run this command in PowerShell (as Administrator):" -ForegroundColor Yellow
    Write-Host "    wsl --install -d Ubuntu" -ForegroundColor White
    Write-Host ""
    return $false
}

function Test-Ubuntu {
    Write-Status "Checking for Ubuntu distribution..." -Type Info
    
    try {
        $distros = wsl -l -q 2>&1
        if ($distros -match 'Ubuntu') {
            Write-Status "Ubuntu is available in WSL" -Type Success
            return $true
        }
    }
    catch {
        # Error checking distros
    }
    
    Write-Status "Ubuntu is NOT installed in WSL" -Type Warning
    Write-Host ""
    Write-Host "  To install Ubuntu in WSL, run:" -ForegroundColor Yellow
    Write-Host "    wsl --install -d Ubuntu" -ForegroundColor White
    Write-Host ""
    return $false
}

function Test-BuildDependencies {
    Write-Status "Checking build dependencies in WSL..." -Type Info
    
    $missing = @()
    foreach ($tool in $RequiredTools) {
        $check = wsl -d Ubuntu -- which $tool 2>&1
        if (-not $check -or $check -match 'not found') {
            $missing += $tool
        }
    }
    
    if ($missing.Count -eq 0) {
        Write-Status "All build dependencies are installed" -Type Success
        return $true
    }
    else {
        Write-Status "Missing dependencies: $($missing -join ', ')" -Type Warning
        return $false
    }
}

function Install-BuildDependencies {
    Write-Status "Installing build dependencies in WSL..." -Type Info
    
    Write-Host "  Updating package lists..." -ForegroundColor Gray
    wsl -d Ubuntu -- sudo apt-get update | Out-Null
    
    Write-Host "  Installing: debootstrap squashfs-tools xorriso isolinux rsync python3..." -ForegroundColor Gray
    wsl -d Ubuntu -- sudo apt-get install -y debootstrap squashfs-tools xorriso isolinux rsync python3
    
    if ($LASTEXITCODE -eq 0) {
        Write-Status "Dependencies installed successfully" -Type Success
        return $true
    }
    else {
        Write-Status "Failed to install dependencies" -Type Error
        return $false
    }
}

function Get-WSLPath {
    param([string]$WindowsPath)
    
    $drive = $WindowsPath.Substring(0, 1).ToLower()
    $path = $WindowsPath.Substring(2).Replace('\', '/')
    return "/mnt/$drive$path"
}

function Start-AegisBuild {
    param(
        [string]$Edition,
        [string]$OutputFolder,
        [bool]$IsSimulation
    )
    
    $info = $EditionInfo[$Edition]
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
    Write-Host "║  Building: Aegis OS $($info.Name)" -ForegroundColor Magenta
    Write-Host "║  Size: ~$($info.Size)" -ForegroundColor Magenta
    Write-Host "║  Mode: $(if ($IsSimulation) { 'SIMULATION' } else { 'REAL BUILD' })" -ForegroundColor Magenta
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Magenta
    Write-Host ""
    
    # Find build-system directory
    $ScriptDir = $PSScriptRoot
    if (-not $ScriptDir) {
        $ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    }
    
    $BuildSystemDir = $ScriptDir
    if (-not (Test-Path "$BuildSystemDir\build-aegis.py")) {
        $BuildSystemDir = Join-Path (Split-Path -Parent $ScriptDir) 'build-system'
    }
    
    if (-not (Test-Path "$BuildSystemDir\build-aegis.py")) {
        Write-Status "Cannot find build-aegis.py script!" -Type Error
        Write-Host "  Expected location: $BuildSystemDir\build-aegis.py" -ForegroundColor Red
        return $false
    }
    
    Write-Status "Build system found at: $BuildSystemDir" -Type Info
    
    # Convert paths to WSL format
    $WslBuildDir = Get-WSLPath $BuildSystemDir
    $WslOutputDir = Get-WSLPath $OutputFolder
    
    # Create output directory
    if (-not (Test-Path $OutputFolder)) {
        New-Item -ItemType Directory -Path $OutputFolder -Force | Out-Null
        Write-Status "Created output folder: $OutputFolder" -Type Info
    }
    
    wsl -d Ubuntu -- mkdir -p "$WslOutputDir"
    
    # Build command
    $buildMode = if ($IsSimulation) { '--simulate' } else { '--real-build' }
    $verboseFlag = if ($VerboseOutput) { '--verbose' } else { '' }
    
    $buildCmd = "cd '$WslBuildDir' && sudo python3 build-aegis.py --edition $Edition $buildMode $verboseFlag"
    
    Write-Status "Starting build process..." -Type Info
    Write-Host ""
    Write-Host "  Command: $buildCmd" -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "─────────────────────────────────────────────────────────────────" -ForegroundColor DarkGray
    
    # Execute build
    $startTime = Get-Date
    
    if ($VerboseOutput) {
        wsl -d Ubuntu -- bash -c $buildCmd
    }
    else {
        $output = wsl -d Ubuntu -- bash -c $buildCmd 2>&1
        foreach ($line in $output) {
            if ($line -match 'Progress|Building|Complete|Error|Warning|✓|✗|►') {
                Write-Host "  $line" -ForegroundColor Gray
            }
        }
    }
    
    $buildResult = $LASTEXITCODE
    $endTime = Get-Date
    $duration = $endTime - $startTime
    
    Write-Host "─────────────────────────────────────────────────────────────────" -ForegroundColor DarkGray
    Write-Host ""
    
    if ($buildResult -ne 0) {
        Write-Status "Build failed with exit code: $buildResult" -Type Error
        return $false
    }
    
    Write-Status "Build completed in $($duration.ToString('hh\:mm\:ss'))" -Type Success
    
    # Find and copy ISO
    if (-not $IsSimulation) {
        $isoPattern = "aegis-$Edition-*.iso"
        $wslIsoPath = wsl -d Ubuntu -- bash -c "ls -t '$WslBuildDir/output/'$isoPattern 2>/dev/null | head -1"
        
        if ($wslIsoPath -and $wslIsoPath.Trim() -ne '') {
            $wslIsoPath = $wslIsoPath.Trim()
            $isoName = Split-Path $wslIsoPath -Leaf
            $destIso = Join-Path $OutputFolder $isoName
            
            Write-Status "Copying ISO to output folder..." -Type Info
            wsl -d Ubuntu -- cp "$wslIsoPath" "$WslOutputDir/"
            
            if (Test-Path $destIso) {
                $fileSize = (Get-Item $destIso).Length
                $fileSizeMB = [math]::Round($fileSize / 1MB, 2)
                $fileSizeGB = [math]::Round($fileSize / 1GB, 2)
                
                Write-Status "Calculating SHA256 checksum..." -Type Info
                $hash = (Get-FileHash $destIso -Algorithm SHA256).Hash
                
                Write-Host ""
                Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Green
                Write-Host "║  ✓ BUILD SUCCESSFUL!" -ForegroundColor Green
                Write-Host "╠══════════════════════════════════════════════════════════════╣" -ForegroundColor Green
                Write-Host "║  ISO File: $isoName" -ForegroundColor Green
                Write-Host "║  Location: $destIso" -ForegroundColor Green
                Write-Host "║  Size: $fileSizeGB GB ($fileSizeMB MB)" -ForegroundColor Green
                Write-Host "║  SHA256: $hash" -ForegroundColor Green
                Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Green
                Write-Host ""
                Write-Host "  Next Steps:" -ForegroundColor Cyan
                Write-Host "  1. Download Balena Etcher: https://etcher.balena.io/" -ForegroundColor White
                Write-Host "  2. Open Etcher and select the ISO file" -ForegroundColor White
                Write-Host "  3. Select your USB drive (8GB+ recommended)" -ForegroundColor White
                Write-Host "  4. Click 'Flash!' to create a bootable USB" -ForegroundColor White
                Write-Host ""
                
                # Save checksum file
                $checksumFile = Join-Path $OutputFolder "$isoName.sha256"
                "$hash  $isoName" | Out-File $checksumFile -Encoding ASCII
                Write-Status "Checksum saved to: $checksumFile" -Type Info
                
                return $true
            }
            else {
                Write-Status "ISO file not found after copy operation" -Type Error
                return $false
            }
        }
        else {
            Write-Status "No ISO file was generated" -Type Error
            return $false
        }
    }
    else {
        # Simulation mode
        Write-Host ""
        Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
        Write-Host "║  ✓ SIMULATION COMPLETED!" -ForegroundColor Cyan
        Write-Host "╠══════════════════════════════════════════════════════════════╣" -ForegroundColor Cyan
        Write-Host "║  No actual ISO was created (simulation mode)." -ForegroundColor Cyan
        Write-Host "║  Run with -RealBuild flag to create actual ISO." -ForegroundColor Cyan
        Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
        Write-Host ""
        
        return $true
    }
}

function Show-Help {
    Write-Host ""
    Write-Host "USAGE:" -ForegroundColor Yellow
    Write-Host "  .\aegis-builder.ps1 [OPTIONS]" -ForegroundColor White
    Write-Host ""
    Write-Host "EDITIONS:" -ForegroundColor Yellow
    foreach ($key in $EditionInfo.Keys) {
        $info = $EditionInfo[$key]
        Write-Host "  $($key.PadRight(12))" -NoNewline -ForegroundColor Cyan
        Write-Host " - $($info.Desc) (~$($info.Size))" -ForegroundColor Gray
    }
    Write-Host ""
    Write-Host "OPTIONS:" -ForegroundColor Yellow
    Write-Host "  -Edition <name>     Edition to build (default: freemium)" -ForegroundColor White
    Write-Host "  -OutputFolder <path> Where to save the ISO (default: Documents\AegisOS-Builds)" -ForegroundColor White
    Write-Host "  -Simulate           Run simulation (no ISO created)" -ForegroundColor White
    Write-Host "  -RealBuild          Create actual bootable ISO" -ForegroundColor White
    Write-Host "  -InstallDeps        Install WSL dependencies before build" -ForegroundColor White
    Write-Host "  -CheckOnly          Check prerequisites only" -ForegroundColor White
    Write-Host "  -VerboseOutput      Show detailed build output" -ForegroundColor White
    Write-Host ""
    Write-Host "EXAMPLES:" -ForegroundColor Yellow
    Write-Host "  # Check if system is ready for building" -ForegroundColor Gray
    Write-Host "  .\aegis-builder.ps1 -CheckOnly" -ForegroundColor White
    Write-Host ""
    Write-Host "  # Run simulation build" -ForegroundColor Gray
    Write-Host "  .\aegis-builder.ps1 -Edition freemium -Simulate" -ForegroundColor White
    Write-Host ""
    Write-Host "  # Build real Gamer edition ISO" -ForegroundColor Gray
    Write-Host "  .\aegis-builder.ps1 -Edition gamer -RealBuild" -ForegroundColor White
    Write-Host ""
    Write-Host "  # Build with custom output location" -ForegroundColor Gray
    Write-Host "  .\aegis-builder.ps1 -Edition ai -RealBuild -OutputFolder 'D:\ISOs'" -ForegroundColor White
    Write-Host ""
}

# Main execution
Write-Header

# Check prerequisites
$wslOk = Test-WSL2
if (-not $wslOk) {
    exit 1
}

$ubuntuOk = Test-Ubuntu
if (-not $ubuntuOk) {
    exit 1
}

$depsOk = Test-BuildDependencies

if ($CheckOnly) {
    Write-Host ""
    if ($wslOk -and $ubuntuOk -and $depsOk) {
        Write-Host "  ✓ All prerequisites are met. Ready to build!" -ForegroundColor Green
    }
    elseif ($wslOk -and $ubuntuOk) {
        Write-Host "  ⚠ WSL2 and Ubuntu ready, but build dependencies need installation." -ForegroundColor Yellow
        Write-Host "    Run with -InstallDeps flag to install them." -ForegroundColor Yellow
    }
    Write-Host ""
    exit 0
}

# Install dependencies if needed
if ($InstallDeps -or (-not $depsOk)) {
    $installed = Install-BuildDependencies
    if (-not $installed) {
        Write-Status "Failed to install dependencies. Please install manually." -Type Error
        exit 1
    }
}

# Determine build mode
$isSimulation = $true
if ($RealBuild) {
    $isSimulation = $false
}
elseif (-not $Simulate -and -not $RealBuild) {
    # Default to simulation if neither specified
    $isSimulation = $true
    Write-Status "No build mode specified. Running in SIMULATION mode." -Type Warning
    Write-Host "  Use -RealBuild flag to create actual ISO." -ForegroundColor Yellow
}

# Run build
$success = Start-AegisBuild -Edition $Edition -OutputFolder $OutputFolder -IsSimulation $isSimulation

if ($success) {
    exit 0
}
else {
    exit 1
}
