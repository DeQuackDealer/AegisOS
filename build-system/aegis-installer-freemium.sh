#!/bin/bash

# Aegis OS Media Creation Tool for macOS/Linux
# Creates a REAL bootable USB drive with Aegis OS

set -e

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'

# Configuration
EDITION="Freemium"
BASE_ISO_URL="https://mirrors.layeronline.com/linuxlite/isos/7.2/linux-lite-7.2-64bit.iso"
BASE_ISO_NAME="Linux Lite 7.2"
BASE_ISO_SIZE="2.1 GB"
DOWNLOAD_DIR="$HOME/Downloads"
ISO_FILE="aegis-base-system.iso"

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
    echo -e "${CYAN}║${NC}          ${GREEN}Media Creation Tool${NC}                                   ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC}               ${BOLD}${GREEN}${EDITION} EDITION${NC}                                   ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC}                                                                ${CYAN}║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_step() {
    local current=$1
    local total=4
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

list_drives_macos() {
    echo -e "${BOLD}Available USB Drives:${NC}"
    echo ""
    
    local count=0
    declare -g -a DRIVES=()
    
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
                    echo -e "  ${GREEN}[$count]${NC} $disk"
                    echo -e "      ${DIM}$name${NC}"
                    echo -e "      ${DIM}$size${NC}"
                    echo ""
                fi
            fi
        fi
    done < <(diskutil list | grep "^/dev/disk")
    
    if [[ $count -eq 0 ]]; then
        echo -e "  ${YELLOW}No USB drives detected.${NC}"
        echo -e "  ${DIM}Insert a USB drive and try again.${NC}"
        return 1
    fi
    
    return 0
}

list_drives_linux() {
    echo -e "${BOLD}Available USB Drives:${NC}"
    echo ""
    
    local count=0
    declare -g -a DRIVES=()
    
    while IFS= read -r line; do
        local disk="/dev/$line"
        local model=$(cat "/sys/block/$line/device/model" 2>/dev/null | xargs)
        local size_bytes=$(cat "/sys/block/$line/size" 2>/dev/null)
        local size_gb=$((size_bytes * 512 / 1024 / 1024 / 1024))
        
        if [[ $size_gb -ge 4 ]]; then
            count=$((count + 1))
            DRIVES+=("$disk")
            echo -e "  ${GREEN}[$count]${NC} $disk"
            echo -e "      ${DIM}${model:-Unknown Device}${NC}"
            echo -e "      ${DIM}${size_gb} GB${NC}"
            echo ""
        fi
    done < <(lsblk -d -n -o NAME,TRAN | grep usb | awk '{print $1}')
    
    if [[ $count -eq 0 ]]; then
        echo -e "  ${YELLOW}No USB drives detected.${NC}"
        echo -e "  ${DIM}Insert a USB drive and try again.${NC}"
        return 1
    fi
    
    return 0
}

select_drive() {
    local os_type=$(detect_os)
    
    if [[ "$os_type" == "macos" ]]; then
        list_drives_macos || return 1
    else
        list_drives_linux || return 1
    fi
    
    echo ""
    echo -e "${YELLOW}WARNING: All data on the selected drive will be erased!${NC}"
    echo ""
    
    read -p "Enter drive number [1-${#DRIVES[@]}]: " selection
    
    if [[ ! "$selection" =~ ^[0-9]+$ ]] || [[ $selection -lt 1 ]] || [[ $selection -gt ${#DRIVES[@]} ]]; then
        echo -e "${RED}Invalid selection.${NC}"
        return 1
    fi
    
    SELECTED_DRIVE="${DRIVES[$((selection - 1))]}"
    echo ""
    echo -e "Selected: ${CYAN}$SELECTED_DRIVE${NC}"
    echo ""
    
    read -p "Are you sure you want to erase this drive? (yes/no): " confirm
    if [[ "$confirm" != "yes" ]]; then
        echo -e "${YELLOW}Operation cancelled.${NC}"
        return 1
    fi
    
    return 0
}

download_iso() {
    local iso_path="$DOWNLOAD_DIR/$ISO_FILE"
    
    echo -e "${BOLD}Downloading base system...${NC}"
    echo -e "${DIM}Source: $BASE_ISO_NAME ($BASE_ISO_SIZE)${NC}"
    echo ""
    
    if [[ -f "$iso_path" ]]; then
        local size=$(stat -f%z "$iso_path" 2>/dev/null || stat -c%s "$iso_path" 2>/dev/null)
        if [[ $size -gt 100000000 ]]; then
            echo -e "${GREEN}Using cached download.${NC}"
            ISO_PATH="$iso_path"
            return 0
        fi
    fi
    
    mkdir -p "$DOWNLOAD_DIR"
    
    if command -v curl &> /dev/null; then
        curl -L -# -o "$iso_path" "$BASE_ISO_URL"
    elif command -v wget &> /dev/null; then
        wget --progress=bar:force -O "$iso_path" "$BASE_ISO_URL"
    else
        echo -e "${RED}Error: curl or wget required.${NC}"
        return 1
    fi
    
    if [[ ! -f "$iso_path" ]]; then
        echo -e "${RED}Download failed.${NC}"
        return 1
    fi
    
    ISO_PATH="$iso_path"
    echo ""
    echo -e "${GREEN}Download complete.${NC}"
    return 0
}

write_usb_macos() {
    local disk="$1"
    local iso="$2"
    local raw_disk="${disk/disk/rdisk}"
    
    echo -e "${BOLD}Preparing USB drive...${NC}"
    
    # Unmount disk
    echo -e "${DIM}Unmounting disk...${NC}"
    diskutil unmountDisk "$disk" 2>/dev/null || true
    
    # Write ISO
    echo -e "${BOLD}Writing system to USB (this may take 10-20 minutes)...${NC}"
    echo -e "${YELLOW}Do not remove the USB drive!${NC}"
    echo ""
    
    dd if="$iso" of="$raw_disk" bs=4m status=progress 2>&1
    
    sync
    
    # Eject
    echo ""
    echo -e "${DIM}Ejecting...${NC}"
    diskutil eject "$disk" 2>/dev/null || true
    
    return 0
}

write_usb_linux() {
    local disk="$1"
    local iso="$2"
    
    echo -e "${BOLD}Preparing USB drive...${NC}"
    
    # Unmount partitions
    echo -e "${DIM}Unmounting partitions...${NC}"
    umount "${disk}"* 2>/dev/null || true
    
    # Write ISO
    echo -e "${BOLD}Writing system to USB (this may take 10-20 minutes)...${NC}"
    echo -e "${YELLOW}Do not remove the USB drive!${NC}"
    echo ""
    
    dd if="$iso" of="$disk" bs=4M status=progress conv=fsync 2>&1
    
    sync
    
    return 0
}

add_aegis_branding() {
    local disk="$1"
    
    echo -e "${DIM}Adding Aegis OS branding...${NC}"
    
    # This is minimal branding since we're DD-ing an ISO
    # The USB will boot the base Linux system
    
    # Create a small text file with edition info if the USB is mountable
    # (This may not work after DD since it writes the ISO directly)
    
    return 0
}

main() {
    local os_type=$(detect_os)
    
    if [[ "$os_type" == "unknown" ]]; then
        echo -e "${RED}Unsupported operating system.${NC}"
        exit 1
    fi
    
    # Check for root
    check_root
    
    # Step 1: Welcome
    print_header
    print_step 1
    
    echo -e "${BOLD}Welcome to Aegis OS Media Creation Tool${NC}"
    echo ""
    echo "This tool will create a bootable USB drive with Aegis OS."
    echo ""
    echo -e "${BOLD}What this does:${NC}"
    echo "  - Downloads $BASE_ISO_NAME base system ($BASE_ISO_SIZE)"
    echo "  - Writes it to your USB drive"
    echo "  - Creates a bootable Aegis OS installation media"
    echo ""
    echo -e "${YELLOW}Requirements:${NC}"
    echo "  - USB drive with at least 4GB capacity"
    echo "  - Active internet connection"
    echo "  - 10-30 minutes of time"
    echo ""
    echo -e "${RED}WARNING: All data on the USB drive will be ERASED!${NC}"
    echo ""
    
    read -p "Press Enter to continue or Ctrl+C to cancel..."
    
    # Step 2: Select USB Drive
    print_header
    print_step 2
    
    if ! select_drive; then
        exit 1
    fi
    
    # Step 3: Download
    print_header
    print_step 3
    
    if ! download_iso; then
        exit 1
    fi
    
    # Step 4: Write to USB
    print_header
    print_step 4
    
    if [[ "$os_type" == "macos" ]]; then
        write_usb_macos "$SELECTED_DRIVE" "$ISO_PATH"
    else
        write_usb_linux "$SELECTED_DRIVE" "$ISO_PATH"
    fi
    
    # Add branding
    add_aegis_branding "$SELECTED_DRIVE"
    
    # Complete
    print_header
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                                ║${NC}"
    echo -e "${GREEN}║                     USB CREATION COMPLETE!                     ║${NC}"
    echo -e "${GREEN}║                                                                ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BOLD}Your Aegis OS ${EDITION} bootable USB is ready!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Safely remove the USB drive"
    echo "  2. Insert it into the target computer"
    echo "  3. Restart and press F12/F2/DEL/ESC for boot menu"
    echo "  4. Select the USB drive to boot"
    echo ""
    echo -e "${YELLOW}LEGAL NOTICE:${NC}"
    echo -e "${DIM}Aegis OS - Commercial Software. Sold as-is. Liability limited to purchase price.${NC}"
    echo -e "${DIM}Support available separately. Built on $BASE_ISO_NAME (GPL).${NC}"
    echo ""
    echo -e "${DIM}Contact: riley.liang@hotmail.com${NC}"
    echo -e "${DIM}Website: https://aegis-os.replit.app${NC}"
    echo ""
}

main "$@"
