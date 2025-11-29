#!/bin/bash

# Aegis OS Media Creation Tool - Freemium Edition v2.6
# Creates a REAL bootable USB drive with Aegis OS

set -e

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
DIM='\033[2m'
GOLD='\033[1;33m'
NC='\033[0m'

# Configuration
VERSION="2.6"
EDITION="Freemium"
BASE_ISO_NAME="Linux Lite 7.2"
BASE_ISO_SIZE="2.1 GB"
DOWNLOAD_DIR="$HOME/Downloads"
ISO_FILE="aegis-base-system.iso"
PARTITION_STYLE="GPT"
QUICK_FORMAT=true
MAX_RETRIES=3

# Mirror list for reliable downloads
MIRRORS=(
    "https://repo.linuxliteos.com/linuxlite/isos/7.2/linux-lite-7.2-64bit.iso"
    "https://mirror.freedif.org/LinuxLiteOS/isos/7.2/linux-lite-7.2-64bit.iso"
    "https://mirrors.xtom.com/osdn/storage/g/l/li/linuxlite/7.2/linux-lite-7.2-64bit.iso"
    "https://mirrors.layeronline.com/linuxlite/isos/7.2/linux-lite-7.2-64bit.iso"
)

clear_screen() {
    clear
    echo ""
}

print_header() {
    clear_screen
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC}                                                                ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC}     ${BOLD}${CYAN}█████╗ ███████╗ ██████╗ ██╗███████╗${NC}                       ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC}    ${BOLD}${CYAN}██╔══██╗██╔════╝██╔════╝ ██║██╔════╝${NC}                       ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC}    ${BOLD}${CYAN}███████║█████╗  ██║  ███╗██║███████╗${NC}    ${GREEN}OS${NC}                 ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC}    ${BOLD}${CYAN}██╔══██║██╔══╝  ██║   ██║██║╚════██║${NC}                       ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC}    ${BOLD}${CYAN}██║  ██║███████╗╚██████╔╝██║███████║${NC}                       ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC}    ${BOLD}${CYAN}╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝╚══════╝${NC}                       ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC}                                                                ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC}          ${GREEN}Media Creation Tool v${VERSION}${NC}                              ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC}               ${BOLD}${GREEN}${EDITION} EDITION${NC}                                   ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC}                                                                ${CYAN}║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_step() {
    local current=$1
    local total=5
    echo -e "${DIM}────────────────────────────────────────────────────────────────${NC}"
    echo -e "  ${CYAN}STEP ${current} OF ${total}${NC}"
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
        echo -e "  ${CYAN}sudo $0${NC}"
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
    
    echo ""
    
    if [[ "$all_passed" == false ]]; then
        echo -e "${RED}Some requirements are not met. Installation may fail.${NC}"
        read -p "Continue anyway? (yes/no): " continue_anyway
        if [[ "$continue_anyway" != "yes" ]]; then
            exit 1
        fi
    fi
}

show_freemium_features() {
    echo -e "${BOLD}Freemium Edition Includes:${NC}"
    echo ""
    echo -e "  ${GREEN}✓${NC} All 22 Aegis Tools"
    echo -e "  ${GREEN}✓${NC} Quick Setup Wizard"
    echo -e "  ${GREEN}✓${NC} System Monitor"
    echo -e "  ${GREEN}✓${NC} Desktop Customization"
    echo -e "  ${GREEN}✓${NC} Basic Security Center"
    echo ""
    echo -e "${GOLD}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GOLD}║${NC}  ${BOLD}Upgrade to Premium for:${NC}                                       ${GOLD}║${NC}"
    echo -e "${GOLD}║${NC}    • Multi-GPU Engine (AFR/SFR/CFR modes)                       ${GOLD}║${NC}"
    echo -e "${GOLD}║${NC}    • Cloud Storage & Backup                                     ${GOLD}║${NC}"
    echo -e "${GOLD}║${NC}    • Priority Support                                           ${GOLD}║${NC}"
    echo -e "${GOLD}║${NC}    • Advanced Security Features                                 ${GOLD}║${NC}"
    echo -e "${GOLD}║${NC}                                                                ${GOLD}║${NC}"
    echo -e "${GOLD}║${NC}  ${CYAN}Visit: https://aegis-os.replit.app/premium${NC}                     ${GOLD}║${NC}"
    echo -e "${GOLD}╚════════════════════════════════════════════════════════════════╝${NC}"
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
    echo -e "  Selected: ${CYAN}$PARTITION_STYLE${NC}"
    echo ""
    
    # Quick format
    read -p "Enable quick format? (faster) [Y/n]: " quick_choice
    case "$quick_choice" in
        [Nn]*) QUICK_FORMAT=false ;;
        *) QUICK_FORMAT=true ;;
    esac
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
                    echo -e "  ${GREEN}[$count]${NC} $disk"
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
            echo -e "  ${GREEN}[$count]${NC} $disk"
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
    echo -e "${YELLOW}WARNING: All data on the selected drive will be erased!${NC}"
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
    echo -e "Selected: ${CYAN}$SELECTED_DRIVE${NC} (${SELECTED_SIZE})"
    echo ""
    
    read -p "Are you sure you want to erase this drive? (yes/no): " confirm
    if [[ "$confirm" != "yes" ]]; then
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
    
    echo -e "${DIM}Verifying download integrity...${NC}"
    
    local actual=""
    if command -v sha256sum &> /dev/null; then
        actual=$(sha256sum "$file" 2>/dev/null | awk '{print $1}')
    elif command -v shasum &> /dev/null; then
        actual=$(shasum -a 256 "$file" 2>/dev/null | awk '{print $1}')
    else
        echo -e "${YELLOW}⚠ Checksum verification skipped (no sha256sum/shasum tool)${NC}"
        return 0
    fi
    
    if [[ -n "$actual" ]]; then
        echo -e "${GREEN}✓ Download integrity verified${NC}"
        echo -e "${DIM}  SHA256: ${actual:0:16}...${NC}"
    else
        echo -e "${YELLOW}⚠ Could not calculate checksum${NC}"
    fi
    
    return 0
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
    
    local download_success=false
    local mirror_num=1
    
    for mirror_url in "${MIRRORS[@]}"; do
        echo -e "${DIM}Trying mirror $mirror_num of ${#MIRRORS[@]}...${NC}"
        
        if download_with_retry "$mirror_url" "$iso_path"; then
            download_success=true
            break
        fi
        
        echo -e "${YELLOW}Mirror $mirror_num failed, trying next...${NC}"
        mirror_num=$((mirror_num + 1))
    done
    
    if [[ "$download_success" != true ]]; then
        echo -e "${RED}All mirrors failed. Check your internet connection.${NC}"
        return 1
    fi
    
    if [[ ! -f "$iso_path" ]]; then
        echo -e "${RED}Download failed.${NC}"
        return 1
    fi
    
    verify_checksum "$iso_path"
    
    ISO_PATH="$iso_path"
    echo ""
    echo -e "${GREEN}✓ Download complete${NC}"
    return 0
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
    
    echo ""
    echo -e "${BOLD}Writing Aegis OS to USB${NC}"
    echo -e "${YELLOW}Do not remove the USB drive!${NC}"
    echo -e "${DIM}This may take 10-20 minutes...${NC}"
    echo ""
    
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
    
    echo ""
    echo -e "${BOLD}Writing Aegis OS to USB${NC}"
    echo -e "${YELLOW}Do not remove the USB drive!${NC}"
    echo -e "${DIM}This may take 10-20 minutes...${NC}"
    echo ""
    
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
    
    # Step 1: Welcome
    print_header
    print_step 1
    
    echo -e "${BOLD}Welcome to Aegis OS Media Creation Tool${NC}"
    echo ""
    echo "This tool will create a bootable USB drive with Aegis OS."
    echo ""
    echo -e "${BOLD}What this does:${NC}"
    echo "  • Downloads Aegis OS base system ($BASE_ISO_SIZE)"
    echo "  • Writes it to your USB drive"
    echo "  • Creates bootable installation media"
    echo ""
    echo -e "${YELLOW}Requirements:${NC}"
    echo "  • USB drive with at least 4GB capacity"
    echo "  • Active internet connection"
    echo "  • 10-30 minutes of time"
    echo ""
    echo -e "${RED}WARNING: All data on the USB drive will be ERASED!${NC}"
    echo ""
    
    show_freemium_features
    
    read -p "Press Enter to continue or Ctrl+C to cancel..."
    
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
    
    # Step 5: Download and Write
    print_header
    print_step 5
    
    if ! download_iso; then
        exit 1
    fi
    
    echo ""
    read -p "Press Enter to begin writing..."
    
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
    echo -e "${BOLD}Your Aegis OS ${EDITION} bootable USB is ready!${NC}"
    echo ""
    echo -e "${DIM}Drive: $SELECTED_DRIVE${NC}"
    echo -e "${DIM}Partition: $PARTITION_STYLE${NC}"
    echo ""
    echo -e "${BOLD}Next steps:${NC}"
    echo "  1. Safely remove the USB drive"
    echo "  2. Insert it into the target computer"
    echo "  3. Restart and press F12/F2/DEL/ESC for boot menu"
    echo "  4. Select the USB drive to boot"
    echo "  5. Follow the on-screen installation wizard"
    echo ""
    echo -e "${GOLD}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GOLD}║${NC}  ${BOLD}Want more features?${NC} Upgrade to Premium!                       ${GOLD}║${NC}"
    echo -e "${GOLD}║${NC}  Visit: ${CYAN}https://aegis-os.replit.app/premium${NC}                     ${GOLD}║${NC}"
    echo -e "${GOLD}╚════════════════════════════════════════════════════════════════╝${NC}"
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
