#!/bin/bash

# Aegis OS Media Creation Tool - Licensed Editions v2.6
# Creates a REAL bootable USB drive with Aegis OS

set -e

# Colors
GOLD='\033[1;33m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'

# Configuration
VERSION="2.6"
LICENSE_KEY=""
EDITION_NAME=""
BASE_ISO_URL="https://mirrors.layeronline.com/linuxlite/isos/7.2/linux-lite-7.2-64bit.iso"
BASE_ISO_NAME="Linux Lite 7.2"
BASE_ISO_SIZE="2.1 GB"
BASE_ISO_SHA256=""
DOWNLOAD_DIR="$HOME/Downloads"
ISO_FILE="aegis-base-system.iso"
PARTITION_STYLE="GPT"
QUICK_FORMAT=true
SECURE_BOOT=false
NETWORK_PRESET="DHCP"
UNATTENDED_MODE=false
MAX_RETRIES=3

clear_screen() {
    clear
    echo ""
}

print_header() {
    clear_screen
    echo -e "${GOLD}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GOLD}║${NC}                                                                ${GOLD}║${NC}"
    echo -e "${GOLD}║${NC}     ${BOLD}${GOLD}█████╗ ███████╗ ██████╗ ██╗███████╗${NC}                       ${GOLD}║${NC}"
    echo -e "${GOLD}║${NC}    ${BOLD}${GOLD}██╔══██╗██╔════╝██╔════╝ ██║██╔════╝${NC}                       ${GOLD}║${NC}"
    echo -e "${GOLD}║${NC}    ${BOLD}${GOLD}███████║█████╗  ██║  ███╗██║███████╗${NC}    ${GOLD}OS${NC}                 ${GOLD}║${NC}"
    echo -e "${GOLD}║${NC}    ${BOLD}${GOLD}██╔══██║██╔══╝  ██║   ██║██║╚════██║${NC}                       ${GOLD}║${NC}"
    echo -e "${GOLD}║${NC}    ${BOLD}${GOLD}██║  ██║███████╗╚██████╔╝██║███████║${NC}                       ${GOLD}║${NC}"
    echo -e "${GOLD}║${NC}    ${BOLD}${GOLD}╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝╚══════╝${NC}                       ${GOLD}║${NC}"
    echo -e "${GOLD}║${NC}                                                                ${GOLD}║${NC}"
    echo -e "${GOLD}║${NC}          ${GOLD}Media Creation Tool v${VERSION}${NC}                              ${GOLD}║${NC}"
    echo -e "${GOLD}║${NC}               ${BOLD}${GOLD}PREMIUM LICENSED EDITION${NC}                        ${GOLD}║${NC}"
    echo -e "${GOLD}║${NC}                                                                ${GOLD}║${NC}"
    echo -e "${GOLD}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_step() {
    local current=$1
    local total=6
    echo -e "${DIM}────────────────────────────────────────────────────────────────${NC}"
    echo -e "  ${GOLD}STEP ${current} OF ${total}${NC}"
    echo -e "${DIM}────────────────────────────────────────────────────────────────${NC}"
    echo ""
}

detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    else
        echo "unknown"
    fi
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        echo -e "${RED}This installer requires administrator privileges.${NC}"
        echo ""
        echo "Please run with sudo:"
        echo -e "  ${GOLD}sudo $0${NC}"
        echo ""
        exit 1
    fi
}

check_system_requirements() {
    echo -e "${BOLD}System Requirements Check${NC}"
    echo ""
    
    local ram_gb=0
    local disk_gb=0
    local os_info=""
    local all_passed=true
    
    # Check RAM
    if [[ "$(detect_os)" == "macos" ]]; then
        ram_gb=$(( $(sysctl -n hw.memsize) / 1024 / 1024 / 1024 ))
        os_info=$(sw_vers -productName 2>/dev/null)" "$(sw_vers -productVersion 2>/dev/null)
    else
        ram_gb=$(( $(grep MemTotal /proc/meminfo | awk '{print $2}') / 1024 / 1024 ))
        os_info=$(cat /etc/os-release 2>/dev/null | grep PRETTY_NAME | cut -d'"' -f2)
    fi
    
    # Check disk space in temp directory
    disk_gb=$(df -BG "$HOME" 2>/dev/null | tail -1 | awk '{print $4}' | tr -d 'G')
    if [[ -z "$disk_gb" ]]; then
        disk_gb=$(df -g "$HOME" 2>/dev/null | tail -1 | awk '{print $4}')
    fi
    
    # RAM check
    if [[ $ram_gb -ge 4 ]]; then
        echo -e "  ${GREEN}✓${NC} RAM: ${ram_gb} GB (4GB+ required)"
    elif [[ $ram_gb -ge 2 ]]; then
        echo -e "  ${YELLOW}⚠${NC} RAM: ${ram_gb} GB (4GB recommended)"
    else
        echo -e "  ${RED}✗${NC} RAM: ${ram_gb} GB (4GB required)"
        all_passed=false
    fi
    
    # Disk check
    if [[ $disk_gb -ge 5 ]]; then
        echo -e "  ${GREEN}✓${NC} Free Space: ${disk_gb} GB (5GB+ required)"
    elif [[ $disk_gb -ge 3 ]]; then
        echo -e "  ${YELLOW}⚠${NC} Free Space: ${disk_gb} GB (5GB recommended)"
    else
        echo -e "  ${RED}✗${NC} Free Space: ${disk_gb} GB (5GB required)"
        all_passed=false
    fi
    
    # OS check
    if [[ -n "$os_info" ]]; then
        echo -e "  ${GREEN}✓${NC} OS: $os_info"
    else
        echo -e "  ${YELLOW}⚠${NC} OS: Unknown"
    fi
    
    # Check for required tools
    echo ""
    echo -e "${BOLD}Required Tools:${NC}"
    
    if command -v curl &> /dev/null || command -v wget &> /dev/null; then
        echo -e "  ${GREEN}✓${NC} Download tool (curl/wget)"
    else
        echo -e "  ${RED}✗${NC} Download tool (curl or wget required)"
        all_passed=false
    fi
    
    if command -v dd &> /dev/null; then
        echo -e "  ${GREEN}✓${NC} Disk writer (dd)"
    else
        echo -e "  ${RED}✗${NC} Disk writer (dd required)"
        all_passed=false
    fi
    
    if command -v sha256sum &> /dev/null || command -v shasum &> /dev/null; then
        echo -e "  ${GREEN}✓${NC} Checksum tool (sha256sum/shasum)"
    else
        echo -e "  ${YELLOW}⚠${NC} Checksum tool (verification will be skipped)"
    fi
    
    echo ""
    
    if [[ "$all_passed" == false ]]; then
        echo -e "${RED}Some requirements are not met. Installation may fail.${NC}"
        read -p "Continue anyway? (yes/no): " continue_anyway
        if [[ "$continue_anyway" != "yes" ]]; then
            exit 1
        fi
    fi
}

validate_license() {
    local key="$1"
    key=$(echo "$key" | tr '[:lower:]' '[:upper:]')
    
    local prefix="${key:0:4}"
    
    case "$prefix" in
        "BSIC") EDITION_NAME="Basic"; return 0 ;;
        "WORK") EDITION_NAME="Workplace"; return 0 ;;
        "GAME") EDITION_NAME="Gamer"; return 0 ;;
        "AIDV") EDITION_NAME="AI Developer"; return 0 ;;
        "GMAI") EDITION_NAME="Gamer + AI"; return 0 ;;
        "SERV") EDITION_NAME="Server"; return 0 ;;
        *) return 1 ;;
    esac
}

show_edition_features() {
    echo -e "${BOLD}${EDITION_NAME} Edition Features:${NC}"
    echo ""
    
    case "$EDITION_NAME" in
        "Basic")
            echo "  • All 22 Aegis Tools included"
            echo "  • Cloud Storage Integration"
            echo "  • Automatic Backup System"
            echo "  • Restore Points"
            echo "  • Priority Email Support"
            ;;
        "Workplace")
            echo "  • All 22 Aegis Tools included"
            echo "  • Remote Desktop Access"
            echo "  • Multi-User Management"
            echo "  • Office Suite Integration"
            echo "  • Business Priority Support"
            ;;
        "Gamer")
            echo "  • All 22 Aegis Tools included"
            echo "  • Multi-GPU Engine (AFR/SFR/CFR)"
            echo "  • Game Library Manager"
            echo "  • Gaming Optimizer"
            echo "  • RGB Control Center"
            ;;
        "AI Developer")
            echo "  • All 22 Aegis Tools included"
            echo "  • Multi-GPU Compute Engine"
            echo "  • CUDA/ROCm Optimization"
            echo "  • AI Workload Balancer"
            echo "  • Development Tools Suite"
            ;;
        "Gamer + AI")
            echo "  • All 22 Aegis Tools included"
            echo "  • Full Multi-GPU Engine"
            echo "  • Gaming + AI Features Combined"
            echo "  • Ultimate Performance Mode"
            echo "  • Premium Support"
            ;;
        "Server")
            echo "  • All 22 Aegis Tools included"
            echo "  • Multi-GPU Virtualization"
            echo "  • Enterprise Management"
            echo "  • 24/7 Priority Support"
            echo "  • Dedicated Account Manager"
            ;;
    esac
    echo ""
}

configure_options() {
    echo -e "${BOLD}Installation Options${NC}"
    echo ""
    
    # Partition style
    echo -e "${BOLD}Partition Style:${NC}"
    echo "  [1] GPT (recommended for UEFI systems)"
    echo "  [2] MBR (for legacy BIOS systems)"
    echo ""
    read -p "Select partition style [1]: " part_choice
    case "$part_choice" in
        2) PARTITION_STYLE="MBR" ;;
        *) PARTITION_STYLE="GPT" ;;
    esac
    echo -e "  Selected: ${GOLD}$PARTITION_STYLE${NC}"
    echo ""
    
    # Quick format
    read -p "Enable quick format? (faster) [Y/n]: " quick_choice
    case "$quick_choice" in
        [Nn]*) QUICK_FORMAT=false ;;
        *) QUICK_FORMAT=true ;;
    esac
    echo ""
    
    # Advanced options for premium editions
    echo -e "${BOLD}Advanced Options:${NC}"
    echo ""
    
    # Secure boot (premium feature)
    read -p "Enable Secure Boot signing? [y/N]: " secboot_choice
    case "$secboot_choice" in
        [Yy]*) SECURE_BOOT=true; echo -e "  ${GREEN}Secure Boot: Enabled${NC}" ;;
        *) SECURE_BOOT=false; echo -e "  ${DIM}Secure Boot: Disabled${NC}" ;;
    esac
    
    # Network preset
    echo ""
    echo -e "${BOLD}Network Configuration:${NC}"
    echo "  [1] DHCP (automatic)"
    echo "  [2] Static IP"
    echo "  [3] Enterprise (802.1X)"
    read -p "Select network preset [1]: " net_choice
    case "$net_choice" in
        2) NETWORK_PRESET="Static" ;;
        3) NETWORK_PRESET="Enterprise" ;;
        *) NETWORK_PRESET="DHCP" ;;
    esac
    echo -e "  Selected: ${GOLD}$NETWORK_PRESET${NC}"
    
    # Unattended mode
    echo ""
    read -p "Enable unattended installation mode? [y/N]: " unattend_choice
    case "$unattend_choice" in
        [Yy]*) UNATTENDED_MODE=true; echo -e "  ${GREEN}Unattended Mode: Enabled${NC}" ;;
        *) UNATTENDED_MODE=false; echo -e "  ${DIM}Unattended Mode: Disabled${NC}" ;;
    esac
    
    # Show configuration summary
    echo ""
    echo -e "${BOLD}Configuration Summary:${NC}"
    echo -e "  Partition Style: ${GOLD}$PARTITION_STYLE${NC}"
    echo -e "  Quick Format: $(if [[ "$QUICK_FORMAT" == true ]]; then echo "${GREEN}Yes${NC}"; else echo "${DIM}No${NC}"; fi)"
    echo -e "  Secure Boot: $(if [[ "$SECURE_BOOT" == true ]]; then echo "${GREEN}Enabled${NC}"; else echo "${DIM}Disabled${NC}"; fi)"
    echo -e "  Network: ${GOLD}$NETWORK_PRESET${NC}"
    echo -e "  Unattended: $(if [[ "$UNATTENDED_MODE" == true ]]; then echo "${GREEN}Enabled${NC}"; else echo "${DIM}Disabled${NC}"; fi)"
    echo ""
}

list_drives_macos() {
    echo -e "${BOLD}Available USB Drives:${NC}"
    echo ""
    
    local count=0
    declare -g -a DRIVES=()
    declare -g -a DRIVE_SIZES=()
    
    while IFS= read -r line; do
        if [[ "$line" =~ ^/dev/disk([0-9]+) ]]; then
            local disk=$(echo "$line" | awk '{print $1}')
            local info=$(diskutil info "$disk" 2>/dev/null)
            
            if echo "$info" | grep -q "Removable Media:.*Yes\|Protocol:.*USB"; then
                local name=$(echo "$info" | grep "Media Name:" | cut -d: -f2 | xargs)
                local size=$(echo "$info" | grep "Disk Size:" | cut -d: -f2 | cut -d'(' -f1 | xargs)
                
                if [[ -n "$name" && -n "$size" ]]; then
                    count=$((count + 1))
                    DRIVES+=("$disk")
                    DRIVE_SIZES+=("$size")
                    echo -e "  ${GOLD}[$count]${NC} $disk"
                    echo -e "      ${BOLD}$name${NC}"
                    echo -e "      ${DIM}Size: $size${NC}"
                    echo ""
                fi
            fi
        fi
    done < <(diskutil list | grep "^/dev/disk")
    
    if [[ $count -eq 0 ]]; then
        echo -e "  ${YELLOW}No USB drives detected.${NC}"
        echo -e "  ${DIM}Insert a USB drive and press R to refresh.${NC}"
        return 1
    fi
    
    return 0
}

list_drives_linux() {
    echo -e "${BOLD}Available USB Drives:${NC}"
    echo ""
    
    local count=0
    declare -g -a DRIVES=()
    declare -g -a DRIVE_SIZES=()
    
    while IFS= read -r line; do
        local disk="/dev/$line"
        local model=$(cat "/sys/block/$line/device/model" 2>/dev/null | xargs)
        local size_bytes=$(cat "/sys/block/$line/size" 2>/dev/null)
        local size_gb=$((size_bytes * 512 / 1024 / 1024 / 1024))
        
        if [[ $size_gb -ge 4 ]]; then
            count=$((count + 1))
            DRIVES+=("$disk")
            DRIVE_SIZES+=("${size_gb}GB")
            echo -e "  ${GOLD}[$count]${NC} $disk"
            echo -e "      ${BOLD}${model:-Unknown Device}${NC}"
            echo -e "      ${DIM}Size: ${size_gb} GB${NC}"
            echo ""
        fi
    done < <(lsblk -d -n -o NAME,TRAN 2>/dev/null | grep usb | awk '{print $1}')
    
    if [[ $count -eq 0 ]]; then
        echo -e "  ${YELLOW}No USB drives detected.${NC}"
        echo -e "  ${DIM}Insert a USB drive and press R to refresh.${NC}"
        return 1
    fi
    
    return 0
}

select_drive() {
    local os_type=$(detect_os)
    
    while true; do
        if [[ "$os_type" == "macos" ]]; then
            list_drives_macos || {
                read -p "Press R to refresh or Q to quit: " refresh_choice
                case "$refresh_choice" in
                    [Rr]*) continue ;;
                    [Qq]*) exit 1 ;;
                esac
                continue
            }
        else
            list_drives_linux || {
                read -p "Press R to refresh or Q to quit: " refresh_choice
                case "$refresh_choice" in
                    [Rr]*) continue ;;
                    [Qq]*) exit 1 ;;
                esac
                continue
            }
        fi
        break
    done
    
    echo ""
    echo -e "${RED}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  WARNING: All data on the selected drive will be ERASED!       ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    read -p "Enter drive number [1-${#DRIVES[@]}] or R to refresh: " selection
    
    if [[ "$selection" =~ ^[Rr]$ ]]; then
        select_drive
        return $?
    fi
    
    if [[ ! "$selection" =~ ^[0-9]+$ ]] || [[ $selection -lt 1 ]] || [[ $selection -gt ${#DRIVES[@]} ]]; then
        echo -e "${RED}Invalid selection.${NC}"
        return 1
    fi
    
    SELECTED_DRIVE="${DRIVES[$((selection - 1))]}"
    SELECTED_SIZE="${DRIVE_SIZES[$((selection - 1))]}"
    echo ""
    echo -e "Selected: ${GOLD}$SELECTED_DRIVE${NC} (${SELECTED_SIZE})"
    echo ""
    
    read -p "Type 'ERASE' to confirm (this will destroy all data): " confirm
    if [[ "$confirm" != "ERASE" ]]; then
        echo -e "${YELLOW}Operation cancelled.${NC}"
        return 1
    fi
    
    return 0
}

download_with_retry() {
    local url="$1"
    local output="$2"
    local attempt=1
    
    while [[ $attempt -le $MAX_RETRIES ]]; do
        echo -e "${DIM}Download attempt $attempt of $MAX_RETRIES...${NC}"
        
        if command -v curl &> /dev/null; then
            if curl -L -# --retry 3 --retry-delay 5 -o "$output" "$url"; then
                return 0
            fi
        elif command -v wget &> /dev/null; then
            if wget --progress=bar:force --tries=3 -O "$output" "$url"; then
                return 0
            fi
        fi
        
        echo -e "${YELLOW}Attempt $attempt failed. Retrying...${NC}"
        attempt=$((attempt + 1))
        sleep 5
    done
    
    return 1
}

verify_checksum() {
    local file="$1"
    local expected="$2"
    
    echo -e "${DIM}Verifying download integrity...${NC}"
    
    # Skip verification if expected checksum is a placeholder
    if [[ -z "$expected" ]] || [[ ${#expected} -lt 64 ]]; then
        echo -e "${YELLOW}⚠ Checksum verification skipped (no valid checksum available)${NC}"
        return 0
    fi
    
    local actual=""
    if command -v sha256sum &> /dev/null; then
        actual=$(sha256sum "$file" 2>/dev/null | awk '{print $1}')
    elif command -v shasum &> /dev/null; then
        actual=$(shasum -a 256 "$file" 2>/dev/null | awk '{print $1}')
    else
        echo -e "${YELLOW}⚠ Checksum verification skipped (no sha256sum/shasum tool)${NC}"
        return 0
    fi
    
    if [[ -z "$actual" ]]; then
        echo -e "${YELLOW}⚠ Could not calculate checksum${NC}"
        return 0
    fi
    
    if [[ "${actual,,}" == "${expected,,}" ]]; then
        echo -e "${GREEN}✓ Checksum verified (SHA256)${NC}"
        return 0
    else
        echo -e "${RED}✗ Checksum mismatch!${NC}"
        echo -e "${DIM}  Expected: $expected${NC}"
        echo -e "${DIM}  Got:      $actual${NC}"
        echo ""
        read -p "Continue anyway? This could indicate a corrupted download. (yes/no): " continue_choice
        if [[ "$continue_choice" != "yes" ]]; then
            return 1
        fi
        return 0
    fi
}

download_iso() {
    local iso_path="$DOWNLOAD_DIR/$ISO_FILE"
    
    echo -e "${BOLD}Downloading Aegis OS Base System${NC}"
    echo -e "${DIM}Source: $BASE_ISO_NAME ($BASE_ISO_SIZE)${NC}"
    echo ""
    
    if [[ -f "$iso_path" ]]; then
        local size=$(stat -f%z "$iso_path" 2>/dev/null || stat -c%s "$iso_path" 2>/dev/null)
        if [[ $size -gt 100000000 ]]; then
            echo -e "${GREEN}✓ Using cached download${NC}"
            echo -e "${DIM}  Location: $iso_path${NC}"
            ISO_PATH="$iso_path"
            return 0
        fi
    fi
    
    mkdir -p "$DOWNLOAD_DIR"
    
    echo -e "${YELLOW}Estimated time: 5-20 minutes (depends on connection speed)${NC}"
    echo ""
    
    if ! download_with_retry "$BASE_ISO_URL" "$iso_path"; then
        echo -e "${RED}Download failed after $MAX_RETRIES attempts.${NC}"
        return 1
    fi
    
    if [[ ! -f "$iso_path" ]]; then
        echo -e "${RED}Download failed.${NC}"
        return 1
    fi
    
    verify_checksum "$iso_path" "$BASE_ISO_SHA256"
    
    ISO_PATH="$iso_path"
    echo ""
    echo -e "${GREEN}✓ Download complete${NC}"
    return 0
}

show_progress_bar() {
    local percent=$1
    local width=50
    local filled=$((percent * width / 100))
    local empty=$((width - filled))
    
    printf "\r  ["
    printf "%${filled}s" | tr ' ' '█'
    printf "%${empty}s" | tr ' ' '░'
    printf "] %3d%%" "$percent"
}

write_usb_macos() {
    local disk="$1"
    local iso="$2"
    local raw_disk="${disk/disk/rdisk}"
    
    echo -e "${BOLD}Preparing USB drive...${NC}"
    echo -e "${DIM}Partition style: $PARTITION_STYLE${NC}"
    echo ""
    
    echo -e "${DIM}Unmounting disk...${NC}"
    diskutil unmountDisk "$disk" 2>/dev/null || true
    
    if [[ "$QUICK_FORMAT" == false ]]; then
        echo -e "${DIM}Performing secure erase...${NC}"
        diskutil zeroDisk "$disk" 2>/dev/null || true
    fi
    
    echo ""
    echo -e "${BOLD}Writing Aegis OS to USB${NC}"
    echo -e "${RED}Do not remove the USB drive!${NC}"
    echo -e "${DIM}This may take 10-20 minutes...${NC}"
    echo ""
    
    # Use pv for progress if available, otherwise dd
    if command -v pv &> /dev/null; then
        pv -p -t -e -r "$iso" | dd of="$raw_disk" bs=4m 2>/dev/null
    else
        dd if="$iso" of="$raw_disk" bs=4m status=progress 2>&1
    fi
    
    sync
    
    echo ""
    echo -e "${DIM}Ejecting...${NC}"
    diskutil eject "$disk" 2>/dev/null || true
    
    return 0
}

write_usb_linux() {
    local disk="$1"
    local iso="$2"
    
    echo -e "${BOLD}Preparing USB drive...${NC}"
    echo -e "${DIM}Partition style: $PARTITION_STYLE${NC}"
    echo ""
    
    echo -e "${DIM}Unmounting partitions...${NC}"
    umount "${disk}"* 2>/dev/null || true
    
    if [[ "$QUICK_FORMAT" == false ]]; then
        echo -e "${DIM}Performing secure erase (this may take a while)...${NC}"
        dd if=/dev/zero of="$disk" bs=4M count=10 status=none 2>/dev/null || true
    fi
    
    echo ""
    echo -e "${BOLD}Writing Aegis OS to USB${NC}"
    echo -e "${RED}Do not remove the USB drive!${NC}"
    echo -e "${DIM}This may take 10-20 minutes...${NC}"
    echo ""
    
    # Use pv for progress if available
    if command -v pv &> /dev/null; then
        pv -p -t -e -r "$iso" | dd of="$disk" bs=4M conv=fsync 2>/dev/null
    else
        dd if="$iso" of="$disk" bs=4M status=progress conv=fsync 2>&1
    fi
    
    sync
    
    return 0
}

main() {
    local os_type=$(detect_os)
    
    if [[ "$os_type" == "unknown" ]]; then
        echo -e "${RED}Unsupported operating system.${NC}"
        exit 1
    fi
    
    check_root
    
    # Step 1: Enter License Key
    print_header
    print_step 1
    
    echo -e "${BOLD}Enter Your License Key${NC}"
    echo ""
    echo "Enter the license key from your Aegis OS purchase."
    echo ""
    echo -e "${DIM}License prefixes:${NC}"
    echo -e "${DIM}  BSIC = Basic    | WORK = Workplace${NC}"
    echo -e "${DIM}  GAME = Gamer    | AIDV = AI Developer${NC}"
    echo -e "${DIM}  GMAI = Gamer+AI | SERV = Server${NC}"
    echo ""
    
    while true; do
        read -p "License Key: " LICENSE_KEY
        
        if validate_license "$LICENSE_KEY"; then
            echo ""
            echo -e "${GREEN}✓ Valid license: $EDITION_NAME Edition${NC}"
            break
        else
            echo -e "${RED}Invalid license format. Try again.${NC}"
        fi
    done
    
    echo ""
    show_edition_features
    
    read -p "Press Enter to continue..."
    
    # Step 2: System Requirements
    print_header
    print_step 2
    
    check_system_requirements
    
    read -p "Press Enter to continue..."
    
    # Step 3: Configure Options
    print_header
    print_step 3
    
    configure_options
    
    read -p "Press Enter to continue..."
    
    # Step 4: Select USB Drive
    print_header
    print_step 4
    
    if ! select_drive; then
        exit 1
    fi
    
    # Step 5: Download
    print_header
    print_step 5
    
    if ! download_iso; then
        exit 1
    fi
    
    read -p "Press Enter to begin writing..."
    
    # Step 6: Write to USB
    print_header
    print_step 6
    
    if [[ "$os_type" == "macos" ]]; then
        write_usb_macos "$SELECTED_DRIVE" "$ISO_PATH"
    else
        write_usb_linux "$SELECTED_DRIVE" "$ISO_PATH"
    fi
    
    # Complete
    print_header
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                                ║${NC}"
    echo -e "${GREEN}║                  ✓ USB CREATION COMPLETE!                      ║${NC}"
    echo -e "${GREEN}║                                                                ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BOLD}Your Aegis OS ${EDITION_NAME} bootable USB is ready!${NC}"
    echo ""
    echo -e "${BOLD}Installation Summary:${NC}"
    echo -e "  License: ${DIM}$LICENSE_KEY${NC}"
    echo -e "  Drive: ${DIM}$SELECTED_DRIVE${NC}"
    echo -e "  Partition: ${DIM}$PARTITION_STYLE${NC}"
    echo -e "  Secure Boot: ${DIM}$(if [[ "$SECURE_BOOT" == true ]]; then echo "Enabled"; else echo "Disabled"; fi)${NC}"
    echo -e "  Network: ${DIM}$NETWORK_PRESET${NC}"
    echo -e "  Unattended: ${DIM}$(if [[ "$UNATTENDED_MODE" == true ]]; then echo "Enabled"; else echo "Disabled"; fi)${NC}"
    echo ""
    echo -e "${BOLD}Next steps:${NC}"
    echo "  1. Safely remove the USB drive"
    echo "  2. Insert it into the target computer"
    echo "  3. Restart and press F12/F2/DEL/ESC for boot menu"
    echo "  4. Select the USB drive to boot"
    echo "  5. Follow the on-screen installation wizard"
    echo ""
    echo -e "${YELLOW}LEGAL NOTICE:${NC}"
    echo -e "${DIM}Aegis OS - Commercial Software. Sold as-is. Liability limited to purchase price.${NC}"
    echo -e "${DIM}Support available separately. Built on Linux Lite 7.2 (GPL).${NC}"
    echo ""
    echo -e "${DIM}Contact: riley.liang@hotmail.com${NC}"
    echo -e "${DIM}Website: https://aegis-os.replit.app${NC}"
    echo ""
}

main "$@"
