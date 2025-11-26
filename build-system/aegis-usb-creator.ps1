# Aegis OS USB Creator - PowerShell Backend
# Creates a REAL bootable Linux USB drive by writing ISO directly
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

# Linux Lite - lightweight, Ubuntu-based distro with live boot capability
$LinuxBaseUrl = "https://mirrors.layeronline.com/linuxlite/isos/7.2/linux-lite-7.2-64bit.iso"
$LinuxBaseName = "Linux Lite 7.2"
$LinuxBaseSize = "2.1 GB"

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
        $request.Timeout = 15000
        $response = $request.GetResponse()
        $size = $response.ContentLength
        $response.Close()
        return $size
    } catch {
        return 0
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
    
    # Validate disk exists and is safe to use
    Write-Progress-File -Percent 2 -Status "Validating USB drive..."
    $disk = Get-Disk -Number $DiskNumber -ErrorAction Stop
    
    # Safety checks
    if ($disk.IsSystem -or $disk.IsBoot) {
        Write-Progress-File -Percent -1 -Status "ERROR: Cannot use system/boot drive. Select a USB drive."
        exit 1
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
    
    # Check if we have a cached download
    $cachedPath = "$env:TEMP\aegis_cached_iso.iso"
    if (Test-Path $cachedPath) {
        $cachedSize = (Get-Item $cachedPath).Length
        if ($cachedSize -gt 1GB) {
            Write-Progress-File -Percent 8 -Status "Using cached download..."
            Copy-Item $cachedPath $isoPath
            $downloadNeeded = $false
        } else {
            $downloadNeeded = $true
        }
    } else {
        $downloadNeeded = $true
    }
    
    if ($downloadNeeded) {
        # Download the base Linux ISO
        Write-Progress-File -Percent 8 -Status "Connecting to download server..."
        Start-Sleep -Seconds 1
        
        $totalSize = Get-FileSize -Url $LinuxBaseUrl
        $totalSizeMB = if ($totalSize -gt 0) { [math]::Round($totalSize / 1MB, 0) } else { "~2100" }
        
        Write-Progress-File -Percent 10 -Status "Downloading $LinuxBaseName ($totalSizeMB MB)..."
        
        # Use BITS for background download with progress
        try {
            $job = Start-BitsTransfer -Source $LinuxBaseUrl -Destination $isoPath -Asynchronous -Priority High -DisplayName "Aegis OS Download"
            
            while (($job.JobState -eq "Transferring") -or ($job.JobState -eq "Connecting")) {
                $percentComplete = 0
                if ($job.BytesTotal -gt 0) {
                    $percentComplete = [int](($job.BytesTransferred / $job.BytesTotal) * 100)
                }
                $mappedPercent = 10 + [int]($percentComplete * 0.40)
                $downloadedMB = [math]::Round($job.BytesTransferred / 1MB, 1)
                $totalMB = [math]::Round($job.BytesTotal / 1MB, 1)
                Write-Progress-File -Percent $mappedPercent -Status "Downloading: $downloadedMB MB / $totalMB MB ($percentComplete%)"
                Start-Sleep -Seconds 2
            }
            
            if ($job.JobState -eq "Transferred") {
                Complete-BitsTransfer -BitsJob $job
            } else {
                throw "BITS download failed: $($job.JobState)"
            }
        } catch {
            # Fallback to WebClient download
            Write-Progress-File -Percent 10 -Status "Downloading (this may take 10-20 minutes)..."
            
            try {
                $webClient = New-Object System.Net.WebClient
                $webClient.Headers.Add("User-Agent", "AegisOS-MediaCreationTool/2.0")
                $webClient.DownloadFile($LinuxBaseUrl, $isoPath)
                $webClient.Dispose()
            } catch {
                Write-Progress-File -Percent -1 -Status "ERROR: Download failed. Check your internet connection."
                exit 1
            }
        }
        
        # Cache the download for future use
        Copy-Item $isoPath $cachedPath -Force -ErrorAction SilentlyContinue
    }
    
    # Verify download
    if (-not (Test-Path $isoPath)) {
        Write-Progress-File -Percent -1 -Status "ERROR: Failed to download base system."
        exit 1
    }
    
    $isoSize = (Get-Item $isoPath).Length
    if ($isoSize -lt 500MB) {
        Write-Progress-File -Percent -1 -Status "ERROR: Downloaded file is incomplete."
        exit 1
    }
    
    Write-Progress-File -Percent 50 -Status "Download complete. Preparing to write to USB..."
    Start-Sleep -Seconds 2
    
    # Get physical path for disk
    $physicalDisk = "\\.\PhysicalDrive$DiskNumber"
    
    # Clear the disk first (required for clean write)
    Write-Progress-File -Percent 52 -Status "WARNING: Erasing USB drive..."
    Start-Sleep -Seconds 1
    
    # Take disk offline, clean, then prepare for raw write
    Write-Progress-File -Percent 54 -Status "Clearing disk..."
    
    # Use diskpart to clean the disk
    $diskpartScript = @"
select disk $DiskNumber
clean
"@
    $diskpartScript | Out-File "$tempDir\diskpart.txt" -Encoding ASCII
    diskpart /s "$tempDir\diskpart.txt" | Out-Null
    Start-Sleep -Seconds 2
    
    Write-Progress-File -Percent 58 -Status "Writing ISO to USB drive..."
    Write-Progress-File -Percent 60 -Status "This will take 5-15 minutes. Do not remove the USB!"
    
    # Use dd-style raw write via .NET FileStream
    # This writes the ISO sector-by-sector to create a bootable USB
    try {
        $blockSize = 4MB
        $sourceStream = [System.IO.File]::OpenRead($isoPath)
        $totalBytes = $sourceStream.Length
        
        # Open physical disk for raw write
        $diskStream = New-Object System.IO.FileStream($physicalDisk, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None, $blockSize, [System.IO.FileOptions]::WriteThrough)
        
        $buffer = New-Object byte[] $blockSize
        $bytesWritten = 0
        $lastPercent = 60
        
        while (($bytesRead = $sourceStream.Read($buffer, 0, $buffer.Length)) -gt 0) {
            $diskStream.Write($buffer, 0, $bytesRead)
            $bytesWritten += $bytesRead
            
            $percentComplete = [int](($bytesWritten / $totalBytes) * 100)
            $mappedPercent = 60 + [int]($percentComplete * 0.35)
            
            if ($mappedPercent -gt $lastPercent) {
                $writtenMB = [math]::Round($bytesWritten / 1MB, 0)
                $totalMB = [math]::Round($totalBytes / 1MB, 0)
                Write-Progress-File -Percent $mappedPercent -Status "Writing: $writtenMB MB / $totalMB MB ($percentComplete%)"
                $lastPercent = $mappedPercent
            }
        }
        
        $diskStream.Flush()
        $diskStream.Close()
        $sourceStream.Close()
        
    } catch {
        Write-Progress-File -Percent -1 -Status "ERROR: Failed to write to USB - $($_.Exception.Message)"
        if ($sourceStream) { $sourceStream.Close() }
        if ($diskStream) { $diskStream.Close() }
        exit 1
    }
    
    Write-Progress-File -Percent 95 -Status "Syncing data..."
    Start-Sleep -Seconds 3
    
    # Rescan disk to update drive letters
    Write-Progress-File -Percent 97 -Status "Refreshing drives..."
    
    $rescanScript = @"
rescan
"@
    $rescanScript | Out-File "$tempDir\rescan.txt" -Encoding ASCII
    diskpart /s "$tempDir\rescan.txt" | Out-Null
    Start-Sleep -Seconds 2
    
    Write-Progress-File -Percent 98 -Status "Cleaning up..."
    
    # Cleanup temp files
    Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue
    
    Write-Progress-File -Percent 100 -Status "SUCCESS! Aegis OS $Edition bootable USB is ready!"
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  USB CREATION COMPLETE!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your Aegis OS bootable USB is ready."
    Write-Host "Edition: $Edition"
    Write-Host ""
    Write-Host "To use:"
    Write-Host "  1. Safely remove the USB drive"
    Write-Host "  2. Insert into target computer"
    Write-Host "  3. Restart and press F12/F2/DEL/ESC for boot menu"
    Write-Host "  4. Select USB drive to boot"
    Write-Host ""
    Write-Host "LEGAL NOTICE:" -ForegroundColor Yellow
    Write-Host "Technical Preview - Provided AS-IS without warranty."
    Write-Host "No support is provided or implied. Use at your own risk."
    Write-Host ""
    
    exit 0
    
} catch {
    Write-Progress-File -Percent -1 -Status "ERROR: $($_.Exception.Message)"
    
    # Cleanup on error
    if (Test-Path "$env:TEMP\AegisOS_Creator") {
        Remove-Item "$env:TEMP\AegisOS_Creator" -Recurse -Force -ErrorAction SilentlyContinue
    }
    
    exit 1
}
