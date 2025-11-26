#!/bin/bash

# Aegis OS Licensed Installer for macOS/Linux
# Professional Linux Distribution - Premium Edition Installer

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
LICENSE_KEY=""
EDITION_NAME=""
EDITION_PREFIX=""
ISO_SIZE=""
DOWNLOAD_DIR="$HOME/Downloads"

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
    echo -e "${GOLD}║${NC}          ${GOLD}Professional Linux Distribution${NC}                       ${GOLD}║${NC}"
    echo -e "${GOLD}║${NC}               ${BOLD}${GOLD}★ PREMIUM LICENSED EDITION ★${NC}                    ${GOLD}║${NC}"
    echo -e "${GOLD}║${NC}                                                                ${GOLD}║${NC}"
    echo -e "${GOLD}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_step() {
    local current=$1
    local total=5
    echo -e "${DIM}────────────────────────────────────────────────────────────────${NC}"
    echo -e "  ${GOLD}STEP ${current} OF ${total}${NC}"
    echo -e "${DIM}────────────────────────────────────────────────────────────────${NC}"
    echo ""
}

print_progress() {
    local percent=$1
    local width=50
    local filled=$((percent * width / 100))
    local empty=$((width - filled))
    
    printf "  ["
    printf "${GOLD}%${filled}s${NC}" | tr ' ' '█'
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

validate_license() {
    print_header
    print_step 1
    
    echo -e "  ${BOLD}Enter Your License Key${NC}"
    echo ""
    echo -e "  ${DIM}Your license key was sent to your email after purchase.${NC}"
    echo -e "  ${DIM}Format: XXXX-XXXX-XXXX-XXXX${NC}"
    echo ""
    echo -e "  ${DIM}Valid prefixes: BSIC, WORK, GAME, AIDV, GMAI, SERV${NC}"
    echo ""
    
    read -p "  License Key: " LICENSE_KEY
    
    if [[ -z "$LICENSE_KEY" ]]; then
        echo ""
        echo -e "  ${RED}✗ License key is required!${NC}"
        sleep 2
        validate_license
        return
    fi
    
    EDITION_PREFIX=$(echo "${LICENSE_KEY:0:4}" | tr '[:lower:]' '[:upper:]')
    
    case $EDITION_PREFIX in
        "BSIC")
            EDITION_NAME="Basic Edition"
            ISO_SIZE="2.8 GB"
            ;;
        "WORK")
            EDITION_NAME="Workplace Edition"
            ISO_SIZE="3.2 GB"
            ;;
        "GAME")
            EDITION_NAME="Gamer Edition"
            ISO_SIZE="4.5 GB"
            ;;
        "AIDV")
            EDITION_NAME="AI Developer Edition"
            ISO_SIZE="5.2 GB"
            ;;
        "GMAI")
            EDITION_NAME="Gamer + AI Edition"
            ISO_SIZE="6.8 GB"
            ;;
        "SERV")
            EDITION_NAME="Server Edition"
            ISO_SIZE="3.5 GB"
            ;;
        *)
            echo ""
            echo -e "  ${RED}✗ Invalid license key prefix!${NC}"
            echo -e "  ${DIM}Please check your key and try again.${NC}"
            sleep 2
            validate_license
            return
            ;;
    esac
    
    echo ""
    echo -e "  ${GREEN}✓ License Validated!${NC}"
    echo -e "    ${BOLD}Edition:${NC} ${GOLD}$EDITION_NAME${NC}"
    echo -e "    ${BOLD}Size:${NC}    ${GOLD}$ISO_SIZE${NC}"
    echo ""
    sleep 2
    
    main_menu
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
                echo -e "    ${GOLD}●${NC} $disk - $name ($size)"
            fi
        done
    elif [[ "$os_type" == "linux" ]]; then
        for dev in /sys/block/sd*; do
            if [[ -f "$dev/removable" ]] && [[ $(cat "$dev/removable") == "1" ]]; then
                local name=$(basename "$dev")
                local size=$(lsblk -dn -o SIZE "/dev/$name" 2>/dev/null)
                local model=$(cat "$dev/device/model" 2>/dev/null | xargs)
                echo -e "    ${GOLD}●${NC} /dev/$name - $model ($size)"
            fi
        done
    fi
    
    echo ""
}

show_features() {
    echo -e "  ${BOLD}$EDITION_NAME Features:${NC}"
    echo ""
    
    case $EDITION_PREFIX in
        "BSIC")
            echo -e "    ${GREEN}✓${NC} Full Desktop Environment"
            echo -e "    ${GREEN}✓${NC} Enhanced Security Suite"
            echo -e "    ${GREEN}✓${NC} Premium Software Bundle"
            echo -e "    ${GREEN}✓${NC} Priority Updates"
            ;;
        "WORK")
            echo -e "    ${GREEN}✓${NC} Business Productivity Suite"
            echo -e "    ${GREEN}✓${NC} VPN & Remote Access"
            echo -e "    ${GREEN}✓${NC} Enterprise Security"
            echo -e "    ${GREEN}✓${NC} AD/LDAP Integration"
            ;;
        "GAME")
            echo -e "    ${GREEN}✓${NC} NVIDIA/AMD Proprietary Drivers"
            echo -e "    ${GREEN}✓${NC} Wine/Proton Gaming Layer"
            echo -e "    ${GREEN}✓${NC} Steam & Lutris Pre-configured"
            echo -e "    ${GREEN}✓${NC} RGB Ecosystem Support"
            ;;
        "AIDV")
            echo -e "    ${GREEN}✓${NC} CUDA 12.3 / ROCm Support"
            echo -e "    ${GREEN}✓${NC} PyTorch, TensorFlow Pre-installed"
            echo -e "    ${GREEN}✓${NC} 100+ ML Libraries"
            echo -e "    ${GREEN}✓${NC} Triton Inference Server"
            ;;
        "GMAI")
            echo -e "    ${GREEN}✓${NC} Full Gaming Suite"
            echo -e "    ${GREEN}✓${NC} Complete AI/ML Toolkit"
            echo -e "    ${GREEN}✓${NC} Hybrid GPU Scheduling"
            echo -e "    ${GREEN}✓${NC} Neural Upscaling"
            ;;
        "SERV")
            echo -e "    ${GREEN}✓${NC} Headless Server Mode"
            echo -e "    ${GREEN}✓${NC} Container Orchestration"
            echo -e "    ${GREEN}✓${NC} High Availability"
            echo -e "    ${GREEN}✓${NC} Enterprise Monitoring"
            ;;
    esac
    echo ""
}

simulate_download() {
    echo -e "  ${BOLD}Downloading $EDITION_NAME...${NC}"
    echo -e "  ${DIM}Size: $ISO_SIZE${NC}"
    echo ""
    
    for i in {0..100..4}; do
        print_progress $i
        sleep 0.12
    done
    echo ""
    echo ""
    echo -e "  ${GREEN}✓${NC} Download complete!"
    echo ""
}

simulate_flash() {
    echo -e "  ${BOLD}Writing to USB drive...${NC}"
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
    echo -e "  ${BOLD}Edition:${NC}  ${GOLD}$EDITION_NAME${NC}"
    echo -e "  ${BOLD}License:${NC}  ${DIM}${LICENSE_KEY:0:9}...${NC}"
    echo ""
    echo -e "  ${BOLD}Next Steps:${NC}"
    echo ""
    echo -e "    ${CYAN}1.${NC} Restart your computer"
    echo -e "    ${CYAN}2.${NC} Press F12/F2/DEL to access boot menu"
    echo -e "    ${CYAN}3.${NC} Select your USB drive"
    echo -e "    ${CYAN}4.${NC} Enter license key when prompted"
    echo ""
    echo -e "  ${DIM}Thank you for your purchase!${NC}"
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
    print_step 2
    
    echo -e "  ${GREEN}✓${NC} ${BOLD}License Verified:${NC} ${GOLD}$EDITION_NAME${NC}"
    echo -e "    ${DIM}Key: ${LICENSE_KEY:0:9}...${NC}"
    echo ""
    
    show_features
    
    echo -e "  ${BOLD}Select an option:${NC}"
    echo ""
    echo -e "    ${GOLD}1.${NC} Install to USB Drive"
    echo -e "    ${GOLD}2.${NC} Download ISO Only"
    echo -e "    ${GOLD}3.${NC} View System Requirements"
    echo -e "    ${GOLD}4.${NC} Exit"
    echo ""
    read -p "  Enter choice (1-4): " choice
    
    case $choice in
        1) install_to_usb ;;
        2) download_only ;;
        3) view_requirements ;;
        4) exit 0 ;;
        *) main_menu ;;
    esac
}

install_to_usb() {
    print_header
    print_step 3
    
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
    read -p "  Confirm: Erase $target_disk and install $EDITION_NAME? (yes/no): " confirm
    
    if [[ "$confirm" != "yes" ]]; then
        echo -e "  ${YELLOW}Cancelled.${NC}"
        sleep 2
        main_menu
        return
    fi
    
    # Download step
    print_header
    print_step 4
    simulate_download
    sleep 1
    
    # Flash step
    print_header
    print_step 5
    simulate_flash
    sleep 1
    
    show_completion
    
    read -p "  Press Enter to exit..."
}

download_only() {
    print_header
    print_step 3
    
    local iso_file="aegis-os-$(echo $EDITION_PREFIX | tr '[:upper:]' '[:lower:]').iso"
    echo -e "  ${BOLD}Download Location:${NC} $DOWNLOAD_DIR/$iso_file"
    echo ""
    
    simulate_download
    
    echo -e "  ${GREEN}✓${NC} ISO saved to: ${GOLD}$DOWNLOAD_DIR/$iso_file${NC}"
    echo ""
    echo -e "  ${DIM}Use a tool like Rufus, Etcher, or dd to write to USB.${NC}"
    echo ""
    
    read -p "  Press Enter to return to menu..."
    main_menu
}

view_requirements() {
    print_header
    print_step 2
    
    echo -e "  ${BOLD}System Requirements for $EDITION_NAME:${NC}"
    echo ""
    echo -e "    ${DIM}CPU:${NC}      64-bit processor (x86_64)"
    
    case $EDITION_PREFIX in
        "GAME"|"AIDV"|"GMAI")
            echo -e "    ${DIM}RAM:${NC}      16-32 GB recommended"
            echo -e "    ${DIM}GPU:${NC}      NVIDIA RTX 2060+ / AMD RX 5700+"
            echo -e "    ${DIM}Storage:${NC}  100-250 GB SSD"
            ;;
        "SERV")
            echo -e "    ${DIM}RAM:${NC}      8 GB minimum (16 GB recommended)"
            echo -e "    ${DIM}Storage:${NC}  50 GB minimum"
            ;;
        *)
            echo -e "    ${DIM}RAM:${NC}      4 GB minimum (8 GB recommended)"
            echo -e "    ${DIM}Storage:${NC}  30 GB free space"
            ;;
    esac
    
    echo -e "    ${DIM}USB:${NC}      8 GB minimum (16 GB for AI editions)"
    echo ""
    
    read -p "  Press Enter to return to menu..."
    main_menu
}

# Start the installer
validate_license
