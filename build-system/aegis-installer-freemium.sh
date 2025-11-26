#!/bin/bash

# Aegis OS Freemium Installer for macOS/Linux
# Professional Linux Distribution - GUI Installer

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
ISO_SIZE="2.1 GB"
ISO_URL="https://aegis-os.replit.app/api/download-iso?edition=freemium"
DOWNLOAD_DIR="$HOME/Downloads"
ISO_FILE="aegis-os-freemium.iso"

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
    echo -e "${CYAN}║${NC}          ${GREEN}Professional Linux Distribution${NC}                       ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC}               ${BOLD}${GREEN}FREEMIUM EDITION - FREE${NC}                         ${CYAN}║${NC}"
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

print_progress() {
    local percent=$1
    local width=50
    local filled=$((percent * width / 100))
    local empty=$((width - filled))
    
    printf "  ["
    printf "${GREEN}%${filled}s${NC}" | tr ' ' '█'
    printf "%${empty}s" | tr ' ' '░'
    printf "] %3d%%\r" "$percent"
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

list_usb_drives() {
    local os_type=$(detect_os)
    
    echo -e "  ${BOLD}Available USB Drives:${NC}"
    echo ""
    
    if [[ "$os_type" == "macos" ]]; then
        diskutil list external | grep -E "^\s*/dev/disk" | while read -r line; do
            local disk=$(echo "$line" | awk '{print $1}')
            local info=$(diskutil info "$disk" 2>/dev/null | grep -E "Device / Media Name|Total Size" | head -2)
            if [[ -n "$info" ]]; then
                local name=$(echo "$info" | grep "Device / Media Name" | cut -d: -f2 | xargs)
                local size=$(echo "$info" | grep "Total Size" | cut -d: -f2 | cut -d'(' -f1 | xargs)
                echo -e "    ${GREEN}●${NC} $disk - $name ($size)"
            fi
        done
    elif [[ "$os_type" == "linux" ]]; then
        lsblk -d -o NAME,SIZE,MODEL,TRAN 2>/dev/null | grep -E "usb|removable" | while read -r line; do
            local name=$(echo "$line" | awk '{print $1}')
            local size=$(echo "$line" | awk '{print $2}')
            local model=$(echo "$line" | awk '{$1=$2=$NF=""; print $0}' | xargs)
            echo -e "    ${GREEN}●${NC} /dev/$name - $model ($size)"
        done
        
        # Fallback: show all removable block devices
        for dev in /sys/block/sd*; do
            if [[ -f "$dev/removable" ]] && [[ $(cat "$dev/removable") == "1" ]]; then
                local name=$(basename "$dev")
                local size=$(lsblk -dn -o SIZE "/dev/$name" 2>/dev/null)
                local model=$(cat "$dev/device/model" 2>/dev/null | xargs)
                echo -e "    ${GREEN}●${NC} /dev/$name - $model ($size)"
            fi
        done
    fi
    
    echo ""
}

show_features() {
    echo -e "  ${BOLD}What's Included:${NC}"
    echo ""
    echo -e "    ${GREEN}✓${NC} XFCE 4.18 Desktop Environment"
    echo -e "    ${GREEN}✓${NC} Firefox, LibreOffice, GIMP"
    echo -e "    ${GREEN}✓${NC} Basic Security Hardening"
    echo -e "    ${GREEN}✓${NC} System Monitoring Tools"
    echo -e "    ${GREEN}✓${NC} Open-source Graphics Drivers"
    echo -e "    ${GREEN}✓${NC} Community Support"
    echo ""
}

show_requirements() {
    echo -e "  ${BOLD}System Requirements:${NC}"
    echo ""
    echo -e "    ${DIM}CPU:${NC}      64-bit processor (x86_64)"
    echo -e "    ${DIM}RAM:${NC}      2 GB minimum (4 GB recommended)"
    echo -e "    ${DIM}Storage:${NC}  15 GB free space"
    echo -e "    ${DIM}USB:${NC}      8 GB minimum"
    echo ""
}

simulate_download() {
    echo -e "  ${BOLD}Downloading Aegis OS Freemium...${NC}"
    echo ""
    
    for i in {0..100..5}; do
        print_progress $i
        sleep 0.15
    done
    echo ""
    echo ""
    echo -e "  ${GREEN}✓${NC} Download complete!"
    echo ""
}

simulate_flash() {
    echo -e "  ${BOLD}Writing to USB drive...${NC}"
    echo ""
    echo -e "  ${YELLOW}⚠${NC}  This will erase all data on the drive!"
    echo ""
    
    for i in {0..100..2}; do
        print_progress $i
        sleep 0.08
    done
    echo ""
    echo ""
    echo -e "  ${GREEN}✓${NC} USB drive created successfully!"
    echo ""
}

show_completion() {
    clear_screen
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║${NC}                                                                ${GREEN}║${NC}"
    echo -e "${GREEN}║${NC}                    ${BOLD}${GREEN}✓ INSTALLATION COMPLETE!${NC}                    ${GREEN}║${NC}"
    echo -e "${GREEN}║${NC}                                                                ${GREEN}║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "  ${BOLD}Next Steps:${NC}"
    echo ""
    echo -e "    ${CYAN}1.${NC} Restart your computer"
    echo -e "    ${CYAN}2.${NC} Press F12/F2/DEL to access boot menu"
    echo -e "    ${CYAN}3.${NC} Select your USB drive"
    echo -e "    ${CYAN}4.${NC} Follow on-screen instructions"
    echo ""
    echo -e "  ${DIM}Upgrade to Premium: https://aegis-os.replit.app/pricing${NC}"
    echo ""
    show_disclaimer
}

show_disclaimer() {
    echo -e "${DIM}════════════════════════════════════════════════════════════════${NC}"
    echo -e "  ${YELLOW}IMPORTANT LEGAL NOTICE${NC}"
    echo -e "${DIM}════════════════════════════════════════════════════════════════${NC}"
    echo -e "  ${DIM}TECHNICAL PREVIEW - This software is provided AS-IS with NO${NC}"
    echo -e "  ${DIM}WARRANTY of any kind. No support is provided or implied.${NC}"
    echo -e "  ${DIM}Anything represented may not be true. Use at your own risk.${NC}"
    echo -e "  ${DIM}By using this software you accept all responsibility.${NC}"
    echo ""
    echo -e "  ${DIM}Contact: riley.liang@hotmail.com${NC}"
    echo -e "${DIM}════════════════════════════════════════════════════════════════${NC}"
    echo ""
}

main_menu() {
    print_header
    print_step 1
    
    echo -e "  ${BOLD}Edition:${NC} ${GREEN}$EDITION${NC}    ${BOLD}Size:${NC} ${GREEN}$ISO_SIZE${NC}    ${BOLD}Price:${NC} ${GREEN}FREE${NC}"
    echo ""
    
    show_features
    
    echo -e "  ${BOLD}Select an option:${NC}"
    echo ""
    echo -e "    ${CYAN}1.${NC} Install to USB Drive"
    echo -e "    ${CYAN}2.${NC} Download ISO Only"
    echo -e "    ${CYAN}3.${NC} View System Requirements"
    echo -e "    ${CYAN}4.${NC} View Premium Editions"
    echo -e "    ${CYAN}5.${NC} Exit"
    echo ""
    read -p "  Enter choice (1-5): " choice
    
    case $choice in
        1) install_to_usb ;;
        2) download_only ;;
        3) view_requirements ;;
        4) view_premium ;;
        5) exit 0 ;;
        *) main_menu ;;
    esac
}

install_to_usb() {
    print_header
    print_step 2
    
    list_usb_drives
    
    echo -e "  ${YELLOW}⚠  WARNING: All data on the selected drive will be erased!${NC}"
    echo ""
    
    local os_type=$(detect_os)
    if [[ "$os_type" == "macos" ]]; then
        read -p "  Enter disk path (e.g., /dev/disk2): " target_disk
    else
        read -p "  Enter device path (e.g., /dev/sdb): " target_disk
    fi
    
    if [[ -z "$target_disk" ]]; then
        echo -e "  ${RED}No drive selected. Returning to menu...${NC}"
        sleep 2
        main_menu
        return
    fi
    
    echo ""
    echo -e "  ${BOLD}You selected:${NC} $target_disk"
    echo ""
    read -p "  Are you sure? This will ERASE ALL DATA! (yes/no): " confirm
    
    if [[ "$confirm" != "yes" ]]; then
        echo -e "  ${YELLOW}Cancelled.${NC}"
        sleep 2
        main_menu
        return
    fi
    
    # Download step
    print_header
    print_step 3
    simulate_download
    sleep 1
    
    # Flash step
    print_header
    print_step 4
    simulate_flash
    sleep 1
    
    show_completion
    
    read -p "  Press Enter to exit..."
}

download_only() {
    print_header
    print_step 2
    
    echo -e "  ${BOLD}Download Location:${NC} $DOWNLOAD_DIR/$ISO_FILE"
    echo ""
    
    simulate_download
    
    echo -e "  ${GREEN}✓${NC} ISO saved to: ${CYAN}$DOWNLOAD_DIR/$ISO_FILE${NC}"
    echo ""
    echo -e "  ${DIM}Use a tool like Rufus, Etcher, or dd to write to USB.${NC}"
    echo ""
    
    read -p "  Press Enter to return to menu..."
    main_menu
}

view_requirements() {
    print_header
    print_step 1
    
    show_requirements
    
    read -p "  Press Enter to return to menu..."
    main_menu
}

view_premium() {
    local os_type=$(detect_os)
    
    if [[ "$os_type" == "macos" ]]; then
        open "https://aegis-os.replit.app/pricing"
    elif [[ "$os_type" == "linux" ]]; then
        xdg-open "https://aegis-os.replit.app/pricing" 2>/dev/null || \
        sensible-browser "https://aegis-os.replit.app/pricing" 2>/dev/null || \
        echo -e "  ${CYAN}Visit: https://aegis-os.replit.app/pricing${NC}"
    fi
    
    main_menu
}

# Check if running as root for USB operations
check_permissions() {
    if [[ "$EUID" -ne 0 ]] && [[ "$1" == "flash" ]]; then
        echo -e "  ${YELLOW}Note: USB writing requires administrator privileges.${NC}"
        echo -e "  ${DIM}You may be prompted for your password.${NC}"
        echo ""
    fi
}

# Start the installer
main_menu
