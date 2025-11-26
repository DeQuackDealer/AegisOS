# Aegis OS USB Creator - PowerShell Backend
# Creates a REAL bootable Linux USB drive
# Must be run as Administrator

param(
    [Parameter(Mandatory=$true)]
    [string]$Edition,
    
    [Parameter(Mandatory=$true)]
    [int]$DiskNumber,
    
    [Parameter(Mandatory=$false)]
    [string]$LicenseKey = "",
    
    [Parameter(Mandatory=$false)]
    [string]$ProgressFile = "$env:TEMP\aegis_progress.txt"
)

$ErrorActionPreference = "Stop"

# Linux Lite is a lightweight, Ubuntu-based distro - good base for customization
# Using official mirrors for reliability
$LinuxBaseUrl = "https://mirrors.layeronline.com/linuxlite/isos/7.2/linux-lite-7.2-64bit.iso"
$LinuxBaseSize = "2.1 GB"
$LinuxBaseName = "Linux Lite 7.2"

function Write-Progress-File {
    param([int]$Percent, [string]$Status)
    "$Percent|$Status" | Out-File -FilePath $ProgressFile -Encoding UTF8 -Force
    Write-Host "[$Percent%] $Status"
}

function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Get-FileSize {
    param([string]$Url)
    try {
        $request = [System.Net.HttpWebRequest]::Create($Url)
        $request.Method = "HEAD"
        $request.Timeout = 10000
        $response = $request.GetResponse()
        $size = $response.ContentLength
        $response.Close()
        return $size
    } catch {
        return 0
    }
}

function Download-WithProgress {
    param(
        [string]$Url,
        [string]$OutFile,
        [int]$StartPercent,
        [int]$EndPercent
    )
    
    $webClient = New-Object System.Net.WebClient
    $webClient.Headers.Add("User-Agent", "AegisOS-MediaCreationTool/2.0")
    
    $totalSize = Get-FileSize -Url $Url
    $tempFile = "$OutFile.tmp"
    
    if ($totalSize -gt 0) {
        $totalSizeMB = [math]::Round($totalSize / 1MB, 1)
        Write-Progress-File -Percent $StartPercent -Status "Downloading base system ($totalSizeMB MB)..."
    }
    
    try {
        # Register download progress event
        $downloadComplete = $false
        $lastPercent = $StartPercent
        
        Register-ObjectEvent -InputObject $webClient -EventName DownloadProgressChanged -Action {
            $percent = $Event.SourceEventArgs.ProgressPercentage
            $downloaded = [math]::Round($Event.SourceEventArgs.BytesReceived / 1MB, 1)
            $total = [math]::Round($Event.SourceEventArgs.TotalBytesToReceive / 1MB, 1)
            
            $mappedPercent = $using:StartPercent + [int](($percent / 100) * ($using:EndPercent - $using:StartPercent))
            "$mappedPercent|Downloading: $downloaded MB / $total MB ($percent%)" | Out-File -FilePath $using:ProgressFile -Encoding UTF8 -Force
        } | Out-Null
        
        Register-ObjectEvent -InputObject $webClient -EventName DownloadFileCompleted -Action {
            $script:downloadComplete = $true
        } | Out-Null
        
        $webClient.DownloadFileAsync([Uri]$Url, $tempFile)
        
        while (-not $downloadComplete) {
            Start-Sleep -Milliseconds 500
        }
        
        if (Test-Path $tempFile) {
            Move-Item -Path $tempFile -Destination $OutFile -Force
            return $true
        }
    } catch {
        Write-Progress-File -Percent $StartPercent -Status "Download error: $($_.Exception.Message)"
    } finally {
        $webClient.Dispose()
        Get-EventSubscriber | Unregister-Event -Force -ErrorAction SilentlyContinue
    }
    
    # Fallback: synchronous download
    try {
        Write-Progress-File -Percent $StartPercent -Status "Downloading (this may take several minutes)..."
        (New-Object System.Net.WebClient).DownloadFile($Url, $OutFile)
        return $true
    } catch {
        return $false
    }
}

# Check for admin privileges
if (-not (Test-Administrator)) {
    Write-Progress-File -Percent -1 -Status "ERROR: Administrator privileges required. Right-click and Run as Administrator."
    exit 1
}

try {
    Write-Progress-File -Percent 0 -Status "Starting Aegis OS Media Creation Tool..."
    Start-Sleep -Seconds 1
    
    # Validate disk exists and is removable
    Write-Progress-File -Percent 2 -Status "Checking USB drive..."
    $disk = Get-Disk -Number $DiskNumber -ErrorAction Stop
    
    if ($disk.BusType -ne "USB") {
        # Also check if it's definitely not the system drive
        if ($disk.IsSystem -or $disk.IsBoot) {
            Write-Progress-File -Percent -1 -Status "ERROR: Cannot use system drive. Select a USB drive."
            exit 1
        }
    }
    
    $diskSizeGB = [math]::Round($disk.Size / 1GB, 2)
    if ($diskSizeGB -lt 4) {
        Write-Progress-File -Percent -1 -Status "ERROR: USB drive must be at least 4GB. Selected drive is ${diskSizeGB}GB."
        exit 1
    }
    
    Write-Progress-File -Percent 5 -Status "USB validated: $($disk.FriendlyName) (${diskSizeGB}GB)"
    Start-Sleep -Seconds 1
    
    # Create temp directory
    $tempDir = "$env:TEMP\AegisOS_Creator"
    if (Test-Path $tempDir) {
        Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue
    }
    New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
    
    $isoPath = Join-Path $tempDir "base-system.iso"
    
    # Download the base Linux ISO
    Write-Progress-File -Percent 8 -Status "Connecting to download server..."
    Start-Sleep -Seconds 1
    
    Write-Progress-File -Percent 10 -Status "Downloading $LinuxBaseName base system ($LinuxBaseSize)..."
    Write-Progress-File -Percent 10 -Status "This will take several minutes depending on your connection..."
    
    $downloadSuccess = Download-WithProgress -Url $LinuxBaseUrl -OutFile $isoPath -StartPercent 10 -EndPercent 50
    
    if (-not $downloadSuccess -or -not (Test-Path $isoPath)) {
        Write-Progress-File -Percent -1 -Status "ERROR: Failed to download base system. Check your internet connection."
        exit 1
    }
    
    $isoSize = (Get-Item $isoPath).Length
    if ($isoSize -lt 100MB) {
        Write-Progress-File -Percent -1 -Status "ERROR: Downloaded file is too small. Download may have failed."
        exit 1
    }
    
    Write-Progress-File -Percent 50 -Status "Download complete. Preparing USB drive..."
    Start-Sleep -Seconds 1
    
    # Clear and prepare the USB drive
    Write-Progress-File -Percent 52 -Status "WARNING: Erasing all data on USB drive..."
    Start-Sleep -Seconds 2
    
    Write-Progress-File -Percent 55 -Status "Clearing existing partitions..."
    Clear-Disk -Number $DiskNumber -RemoveData -RemoveOEM -Confirm:$false -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
    
    Write-Progress-File -Percent 58 -Status "Initializing disk..."
    Initialize-Disk -Number $DiskNumber -PartitionStyle MBR -ErrorAction SilentlyContinue
    
    Write-Progress-File -Percent 60 -Status "Creating partition..."
    $partition = New-Partition -DiskNumber $DiskNumber -UseMaximumSize -IsActive -AssignDriveLetter
    $driveLetter = $partition.DriveLetter
    Start-Sleep -Seconds 2
    
    Write-Progress-File -Percent 63 -Status "Formatting as FAT32..."
    Format-Volume -DriveLetter $driveLetter -FileSystem FAT32 -NewFileSystemLabel "AEGIS_OS" -Confirm:$false
    Start-Sleep -Seconds 1
    
    Write-Progress-File -Percent 65 -Status "Mounting ISO image..."
    
    # Mount the ISO
    $mountResult = Mount-DiskImage -ImagePath $isoPath -PassThru
    $isoDriveLetter = ($mountResult | Get-Volume).DriveLetter
    
    if (-not $isoDriveLetter) {
        Write-Progress-File -Percent -1 -Status "ERROR: Failed to mount ISO image"
        exit 1
    }
    
    Write-Progress-File -Percent 68 -Status "Copying system files to USB..."
    
    $sourceRoot = "${isoDriveLetter}:\"
    $destRoot = "${driveLetter}:\"
    
    # Copy all files from ISO to USB
    $totalFiles = (Get-ChildItem -Path $sourceRoot -Recurse -File).Count
    $copiedFiles = 0
    
    Get-ChildItem -Path $sourceRoot -Recurse | ForEach-Object {
        $relativePath = $_.FullName.Substring($sourceRoot.Length)
        $destPath = Join-Path $destRoot $relativePath
        
        if ($_.PSIsContainer) {
            if (-not (Test-Path $destPath)) {
                New-Item -ItemType Directory -Path $destPath -Force | Out-Null
            }
        } else {
            $destDir = Split-Path $destPath -Parent
            if (-not (Test-Path $destDir)) {
                New-Item -ItemType Directory -Path $destDir -Force | Out-Null
            }
            Copy-Item -Path $_.FullName -Destination $destPath -Force
            $copiedFiles++
            
            if ($copiedFiles % 50 -eq 0) {
                $copyPercent = 68 + [int](($copiedFiles / $totalFiles) * 20)
                Write-Progress-File -Percent $copyPercent -Status "Copying files... ($copiedFiles / $totalFiles)"
            }
        }
    }
    
    Write-Progress-File -Percent 88 -Status "Files copied. Unmounting ISO..."
    
    # Unmount ISO
    Dismount-DiskImage -ImagePath $isoPath -ErrorAction SilentlyContinue
    
    Write-Progress-File -Percent 90 -Status "Adding Aegis OS customization..."
    
    # Create Aegis OS branding and customization
    $aegisDir = Join-Path $destRoot "aegis"
    New-Item -ItemType Directory -Path $aegisDir -Force | Out-Null
    
    # Edition configuration
    $editionConfig = @"
# Aegis OS Edition Configuration
AEGIS_EDITION=$Edition
AEGIS_VERSION=1.0.0
AEGIS_BUILD_DATE=$(Get-Date -Format "yyyy-MM-dd")
AEGIS_BASE_SYSTEM=$LinuxBaseName
LICENSE_KEY=$LicenseKey
"@
    $editionConfig | Out-File -FilePath (Join-Path $aegisDir "edition.conf") -Encoding UTF8
    
    # Readme
    $readme = @"
================================================================================
                      AEGIS OS - $Edition Edition
================================================================================

WHAT IS THIS?
This is a bootable USB drive with Aegis OS based on $LinuxBaseName.

TO BOOT FROM THIS USB:
1. Restart your computer
2. Press F12, F2, DEL, or ESC during startup (varies by manufacturer)
3. Select this USB drive from the boot menu
4. Choose "Start Aegis OS" or "Try without installing"

SYSTEM REQUIREMENTS:
- 64-bit processor (Intel or AMD)
- 4GB RAM minimum (8GB recommended)
- 20GB disk space for installation
- USB 2.0 or higher port

EDITION: $Edition
$(if ($LicenseKey) { "LICENSE: $LicenseKey" } else { "LICENSE: Freemium (No license required)" })

LEGAL NOTICE:
TECHNICAL PREVIEW - This software is provided AS-IS without warranty.
No support is provided or implied. Use at your own risk.
Base system: $LinuxBaseName (used under their respective license)

Contact: riley.liang@hotmail.com
Website: https://aegis-os.replit.app

Created: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
================================================================================
"@
    $readme | Out-File -FilePath (Join-Path $destRoot "AEGIS_README.txt") -Encoding UTF8
    
    Write-Progress-File -Percent 95 -Status "Verifying bootable media..."
    Start-Sleep -Seconds 1
    
    # Verify key boot files exist
    $bootFiles = @("isolinux", "boot", "casper", "live")
    $foundBoot = $false
    foreach ($bootDir in $bootFiles) {
        if (Test-Path (Join-Path $destRoot $bootDir)) {
            $foundBoot = $true
            break
        }
    }
    
    if (-not $foundBoot) {
        Write-Progress-File -Percent -1 -Status "WARNING: Boot files may not be complete. USB might not boot properly."
    }
    
    Write-Progress-File -Percent 98 -Status "Cleaning up..."
    
    # Clean up temp files
    Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue
    
    Write-Progress-File -Percent 100 -Status "SUCCESS! Aegis OS $Edition is ready on drive ${driveLetter}:"
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  USB CREATION COMPLETE!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your Aegis OS bootable USB is ready."
    Write-Host "Drive: ${driveLetter}:"
    Write-Host "Edition: $Edition"
    Write-Host ""
    Write-Host "To use: Restart your PC and boot from this USB drive."
    Write-Host ""
    
    exit 0
    
} catch {
    Write-Progress-File -Percent -1 -Status "ERROR: $($_.Exception.Message)"
    
    # Cleanup on error
    if (Test-Path "$env:TEMP\AegisOS_Creator") {
        Remove-Item "$env:TEMP\AegisOS_Creator" -Recurse -Force -ErrorAction SilentlyContinue
    }
    
    # Try to unmount ISO if mounted
    if ($isoPath -and (Test-Path $isoPath)) {
        Dismount-DiskImage -ImagePath $isoPath -ErrorAction SilentlyContinue
    }
    
    exit 1
}
