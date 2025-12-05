#!/bin/bash
#
# Aegis OS USB Creator for Linux
# Version: 4.0
# Cross-distribution installer for creating bootable Aegis OS USB drives
#
# Supports: Ubuntu, Debian, Fedora, Arch, openSUSE, and derivatives
# Author: Aegis OS Team
# License: MIT
#

set -e

readonly VERSION="4.0"
readonly SCRIPT_NAME="Aegis OS USB Creator"
readonly LOG_FILE="/tmp/aegis-usb-creator.log"
readonly TEMP_DIR="/tmp/aegis-os-installer"
readonly MIN_USB_SIZE=$((4 * 1024 * 1024 * 1024))  # 4GB minimum

readonly PRIMARY_MIRROR="https://repo.linuxliteos.com/linuxlite/isos/7.2/linux-lite-7.2-64bit.iso"
readonly FALLBACK_MIRROR="https://mirror.freedif.org/LinuxLiteOS/isos/7.2/linux-lite-7.2-64bit.iso"
readonly EXPECTED_SHA256="DC8955E02C68537815ED0010F7C4C035CE786BBA2C679DD74532B22205DF8216"
readonly ISO_SIZE_APPROX=$((3 * 1024 * 1024 * 1024))  # ~3GB

declare -A EDITIONS
EDITIONS=(
    ["1"]="freemium|Freemium|FREE|Base Linux OS, XFCE Desktop, Wine, Proton, DeskLink Basic (2 PCs), Gaming/AI/Workplace Lite packs"
    ["2"]="basic|Basic|$69 lifetime|All Freemium + Pro apps, Unlimited DeskLink, Mobile Link Pro, 50+ themes, Cloud sync, 24/7 support"
    ["3"]="gamer|Gamer|$89 lifetime|All Basic + Low-latency kernel, Aegis Game Launcher, Wallpaper Engine, Audio Router, Stream, Game Library"
    ["4"]="ai-dev|AI Developer|$129 lifetime|All Basic + CUDA/ROCm support, Jupyter, PyTorch, TensorFlow, AI Toolkit, Model Hub, Training tools"
    ["5"]="workplace|Workplace|$99 lifetime|All Basic + Enterprise VPN, Meeting tools, Remote desktop, SSO, MDM, Compliance tools"
    ["6"]="gamer-ai|Gamer+AI|$149 lifetime|All Gamer + All AI Developer features combined, best for gaming + AI development"
    ["7"]="server|Server|$129 lifetime|Headless server, Docker/K8s, Web hosting, Monitoring, Hardened security, Server management"
)

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'
BOLD='\033[1m'

HAS_COLORS=false
HAS_DIALOG=false
HAS_WHIPTAIL=false
DETECTED_DISTRO=""
DETECTED_PKG_MGR=""
SELECTED_EDITION=""
SELECTED_DRIVE=""
SELECTED_DRIVE_PATH=""
LICENSE_KEY=""

log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
}

print_color() {
    local color="$1"
    shift
    if $HAS_COLORS; then
        echo -e "${color}$*${NC}"
    else
        echo "$*"
    fi
}

print_header() {
    clear
    print_color "$CYAN" "╔══════════════════════════════════════════════════════════════════╗"
    print_color "$CYAN" "║                                                                  ║"
    print_color "$CYAN" "║        ${WHITE}${BOLD}Aegis OS USB Creator v${VERSION}${NC}${CYAN}                              ║"
    print_color "$CYAN" "║        ${WHITE}Create bootable USB drives for any edition${NC}${CYAN}               ║"
    print_color "$CYAN" "║                                                                  ║"
    print_color "$CYAN" "╚══════════════════════════════════════════════════════════════════╝"
    echo
}

print_step() {
    local step="$1"
    local total="$2"
    local desc="$3"
    print_color "$BLUE" "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    print_color "$WHITE" " Step $step of $total: $desc"
    print_color "$BLUE" "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_color "$YELLOW" "This tool requires root privileges to write to USB drives."
        echo
        if command -v pkexec &> /dev/null; then
            print_color "$WHITE" "Restarting with elevated privileges..."
            pkexec "$0" "$@"
            exit $?
        elif command -v sudo &> /dev/null; then
            print_color "$WHITE" "Restarting with sudo..."
            sudo "$0" "$@"
            exit $?
        else
            print_color "$RED" "Error: Please run this script as root or install sudo/pkexec."
            exit 1
        fi
    fi
}

init_environment() {
    if [[ -t 1 ]] && [[ -n "$TERM" ]] && [[ "$TERM" != "dumb" ]]; then
        if tput colors &> /dev/null && [[ $(tput colors) -ge 8 ]]; then
            HAS_COLORS=true
        fi
    fi
    
    if command -v dialog &> /dev/null; then
        HAS_DIALOG=true
    fi
    if command -v whiptail &> /dev/null; then
        HAS_WHIPTAIL=true
    fi
    
    mkdir -p "$TEMP_DIR"
    touch "$LOG_FILE"
    
    log "INFO" "Aegis OS USB Creator v${VERSION} started"
    log "INFO" "Colors: $HAS_COLORS, Dialog: $HAS_DIALOG, Whiptail: $HAS_WHIPTAIL"
}

detect_distro() {
    log "INFO" "Detecting Linux distribution..."
    
    if [[ -f /etc/os-release ]]; then
        source /etc/os-release
        local id_lower=$(echo "$ID" | tr '[:upper:]' '[:lower:]')
        local id_like_lower=$(echo "${ID_LIKE:-}" | tr '[:upper:]' '[:lower:]')
        
        case "$id_lower" in
            ubuntu|linuxmint|pop|elementary|zorin|neon)
                DETECTED_DISTRO="ubuntu"
                DETECTED_PKG_MGR="apt"
                ;;
            debian|raspbian|kali|parrot|mx)
                DETECTED_DISTRO="debian"
                DETECTED_PKG_MGR="apt"
                ;;
            fedora|nobara|ultramarine)
                DETECTED_DISTRO="fedora"
                DETECTED_PKG_MGR="dnf"
                ;;
            rhel|centos|rocky|alma|oracle)
                DETECTED_DISTRO="rhel"
                DETECTED_PKG_MGR="dnf"
                ;;
            arch|manjaro|endeavouros|garuda|arcolinux|artix)
                DETECTED_DISTRO="arch"
                DETECTED_PKG_MGR="pacman"
                ;;
            opensuse*|suse|sles)
                DETECTED_DISTRO="opensuse"
                DETECTED_PKG_MGR="zypper"
                ;;
            void)
                DETECTED_DISTRO="void"
                DETECTED_PKG_MGR="xbps"
                ;;
            alpine)
                DETECTED_DISTRO="alpine"
                DETECTED_PKG_MGR="apk"
                ;;
            gentoo)
                DETECTED_DISTRO="gentoo"
                DETECTED_PKG_MGR="emerge"
                ;;
            *)
                if [[ "$id_like_lower" == *"ubuntu"* ]] || [[ "$id_like_lower" == *"debian"* ]]; then
                    DETECTED_DISTRO="debian"
                    DETECTED_PKG_MGR="apt"
                elif [[ "$id_like_lower" == *"fedora"* ]] || [[ "$id_like_lower" == *"rhel"* ]]; then
                    DETECTED_DISTRO="fedora"
                    DETECTED_PKG_MGR="dnf"
                elif [[ "$id_like_lower" == *"arch"* ]]; then
                    DETECTED_DISTRO="arch"
                    DETECTED_PKG_MGR="pacman"
                elif [[ "$id_like_lower" == *"suse"* ]]; then
                    DETECTED_DISTRO="opensuse"
                    DETECTED_PKG_MGR="zypper"
                else
                    DETECTED_DISTRO="unknown"
                    DETECTED_PKG_MGR="unknown"
                fi
                ;;
        esac
        
        log "INFO" "Detected: $PRETTY_NAME (ID: $ID, ID_LIKE: ${ID_LIKE:-none})"
        log "INFO" "Using: distro=$DETECTED_DISTRO, pkg_mgr=$DETECTED_PKG_MGR"
    else
        if command -v apt &> /dev/null; then
            DETECTED_DISTRO="debian"
            DETECTED_PKG_MGR="apt"
        elif command -v dnf &> /dev/null; then
            DETECTED_DISTRO="fedora"
            DETECTED_PKG_MGR="dnf"
        elif command -v yum &> /dev/null; then
            DETECTED_DISTRO="rhel"
            DETECTED_PKG_MGR="yum"
        elif command -v pacman &> /dev/null; then
            DETECTED_DISTRO="arch"
            DETECTED_PKG_MGR="pacman"
        elif command -v zypper &> /dev/null; then
            DETECTED_DISTRO="opensuse"
            DETECTED_PKG_MGR="zypper"
        else
            DETECTED_DISTRO="unknown"
            DETECTED_PKG_MGR="unknown"
        fi
        log "INFO" "Fallback detection: distro=$DETECTED_DISTRO, pkg_mgr=$DETECTED_PKG_MGR"
    fi
}

check_command() {
    command -v "$1" &> /dev/null
}

install_package() {
    local pkg="$1"
    local pkg_apt="${2:-$pkg}"
    local pkg_dnf="${3:-$pkg}"
    local pkg_pacman="${4:-$pkg}"
    local pkg_zypper="${5:-$pkg}"
    
    log "INFO" "Installing package: $pkg"
    
    case "$DETECTED_PKG_MGR" in
        apt)
            DEBIAN_FRONTEND=noninteractive apt-get install -y "$pkg_apt" 2>> "$LOG_FILE"
            ;;
        dnf)
            dnf install -y "$pkg_dnf" 2>> "$LOG_FILE"
            ;;
        yum)
            yum install -y "$pkg_dnf" 2>> "$LOG_FILE"
            ;;
        pacman)
            pacman -S --noconfirm "$pkg_pacman" 2>> "$LOG_FILE"
            ;;
        zypper)
            zypper install -y "$pkg_zypper" 2>> "$LOG_FILE"
            ;;
        xbps)
            xbps-install -y "$pkg" 2>> "$LOG_FILE"
            ;;
        apk)
            apk add "$pkg" 2>> "$LOG_FILE"
            ;;
        *)
            log "WARN" "Unknown package manager, cannot install $pkg"
            return 1
            ;;
    esac
}

update_package_cache() {
    print_color "$WHITE" "Updating package cache..."
    case "$DETECTED_PKG_MGR" in
        apt)
            apt-get update -qq 2>> "$LOG_FILE"
            ;;
        dnf|yum)
            $DETECTED_PKG_MGR makecache -q 2>> "$LOG_FILE"
            ;;
        pacman)
            pacman -Sy --noconfirm 2>> "$LOG_FILE"
            ;;
        zypper)
            zypper refresh -q 2>> "$LOG_FILE"
            ;;
    esac
}

check_and_install_dependencies() {
    local deps_needed=()
    local deps_installed=()
    
    print_color "$WHITE" "Checking required dependencies..."
    echo
    
    if ! check_command wget && ! check_command curl; then
        deps_needed+=("wget")
    else
        deps_installed+=("wget/curl")
    fi
    
    if ! check_command dd; then
        print_color "$RED" "Error: 'dd' is not available. This is a core system utility."
        exit 1
    fi
    deps_installed+=("dd")
    
    if ! check_command pv; then
        deps_needed+=("pv")
    else
        deps_installed+=("pv")
    fi
    
    if ! check_command lsblk; then
        deps_needed+=("util-linux")
    else
        deps_installed+=("lsblk")
    fi
    
    if ! check_command parted; then
        deps_needed+=("parted")
    else
        deps_installed+=("parted")
    fi
    
    if ! check_command sha256sum; then
        deps_needed+=("coreutils")
    else
        deps_installed+=("sha256sum")
    fi
    
    if ! $HAS_DIALOG && ! $HAS_WHIPTAIL; then
        deps_needed+=("dialog")
    else
        deps_installed+=("dialog/whiptail")
    fi
    
    echo -n "  Installed: "
    print_color "$GREEN" "${deps_installed[*]}"
    
    if [[ ${#deps_needed[@]} -gt 0 ]]; then
        echo -n "  Missing: "
        print_color "$YELLOW" "${deps_needed[*]}"
        echo
        
        print_color "$WHITE" "Installing missing dependencies..."
        
        if [[ "$DETECTED_PKG_MGR" == "unknown" ]]; then
            print_color "$RED" "Error: Cannot detect package manager. Please install manually:"
            print_color "$YELLOW" "  ${deps_needed[*]}"
            exit 1
        fi
        
        update_package_cache
        
        for dep in "${deps_needed[@]}"; do
            echo -n "  Installing $dep... "
            case "$dep" in
                wget)
                    install_package wget wget wget wget wget && print_color "$GREEN" "OK" || print_color "$YELLOW" "SKIP"
                    ;;
                pv)
                    install_package pv pv pv pv pv && print_color "$GREEN" "OK" || print_color "$YELLOW" "SKIP"
                    ;;
                util-linux)
                    install_package util-linux util-linux util-linux util-linux util-linux && print_color "$GREEN" "OK" || print_color "$YELLOW" "SKIP"
                    ;;
                parted)
                    install_package parted parted parted parted parted && print_color "$GREEN" "OK" || print_color "$YELLOW" "SKIP"
                    ;;
                coreutils)
                    install_package coreutils coreutils coreutils coreutils coreutils && print_color "$GREEN" "OK" || print_color "$YELLOW" "SKIP"
                    ;;
                dialog)
                    if install_package dialog dialog dialog dialog dialog 2>/dev/null; then
                        print_color "$GREEN" "OK"
                        HAS_DIALOG=true
                    else
                        if install_package whiptail whiptail newt whiptail whiptail 2>/dev/null; then
                            print_color "$GREEN" "OK (whiptail)"
                            HAS_WHIPTAIL=true
                        else
                            print_color "$YELLOW" "SKIP (will use text mode)"
                        fi
                    fi
                    ;;
            esac
        done
    fi
    
    echo
    print_color "$GREEN" "✓ All dependencies satisfied"
    log "INFO" "Dependencies check completed"
}

run_system_checks() {
    local checks_passed=0
    local checks_warned=0
    local checks_failed=0
    
    print_color "$WHITE" "Running system checks..."
    echo
    
    local ram_kb=$(grep MemTotal /proc/meminfo | awk '{print $2}')
    local ram_gb=$((ram_kb / 1024 / 1024))
    echo -n "  RAM: "
    if [[ $ram_gb -ge 4 ]]; then
        print_color "$GREEN" "✓ ${ram_gb}GB"
        ((checks_passed++))
    elif [[ $ram_gb -ge 2 ]]; then
        print_color "$YELLOW" "⚠ ${ram_gb}GB (4GB+ recommended)"
        ((checks_warned++))
    else
        print_color "$RED" "✗ ${ram_gb}GB (minimum 2GB required)"
        ((checks_failed++))
    fi
    
    local free_space_kb=$(df "$TEMP_DIR" | tail -1 | awk '{print $4}')
    local free_space_gb=$((free_space_kb / 1024 / 1024))
    echo -n "  Free disk space: "
    if [[ $free_space_gb -ge 4 ]]; then
        print_color "$GREEN" "✓ ${free_space_gb}GB"
        ((checks_passed++))
    else
        print_color "$RED" "✗ ${free_space_gb}GB (4GB+ required for download)"
        ((checks_failed++))
    fi
    
    echo -n "  Internet connection: "
    if ping -c 1 -W 3 8.8.8.8 &> /dev/null || ping -c 1 -W 3 1.1.1.1 &> /dev/null; then
        print_color "$GREEN" "✓ Connected"
        ((checks_passed++))
    else
        if curl -s --connect-timeout 5 https://www.google.com > /dev/null 2>&1; then
            print_color "$GREEN" "✓ Connected"
            ((checks_passed++))
        else
            print_color "$RED" "✗ No connection detected"
            ((checks_failed++))
        fi
    fi
    
    echo -n "  Kernel version: "
    local kernel_version=$(uname -r)
    local kernel_major=$(echo "$kernel_version" | cut -d. -f1)
    if [[ $kernel_major -ge 4 ]]; then
        print_color "$GREEN" "✓ $kernel_version"
        ((checks_passed++))
    else
        print_color "$YELLOW" "⚠ $kernel_version (Linux 4.x+ recommended)"
        ((checks_warned++))
    fi
    
    echo -n "  Architecture: "
    local arch=$(uname -m)
    if [[ "$arch" == "x86_64" ]]; then
        print_color "$GREEN" "✓ $arch (64-bit)"
        ((checks_passed++))
    else
        print_color "$YELLOW" "⚠ $arch (x86_64 required for full compatibility)"
        ((checks_warned++))
    fi
    
    echo
    if [[ $checks_failed -gt 0 ]]; then
        print_color "$RED" "✗ System checks failed: $checks_failed failed, $checks_warned warnings"
        return 1
    elif [[ $checks_warned -gt 0 ]]; then
        print_color "$YELLOW" "⚠ System checks passed with warnings: $checks_passed passed, $checks_warned warnings"
    else
        print_color "$GREEN" "✓ All system checks passed"
    fi
    
    log "INFO" "System checks: $checks_passed passed, $checks_warned warnings, $checks_failed failed"
    return 0
}

select_edition_dialog() {
    local options=()
    
    for key in $(echo "${!EDITIONS[@]}" | tr ' ' '\n' | sort -n); do
        IFS='|' read -r id name price desc <<< "${EDITIONS[$key]}"
        options+=("$key" "$name ($price)")
    done
    
    local result
    if $HAS_DIALOG; then
        result=$(dialog --clear --backtitle "Aegis OS USB Creator" \
            --title "Select Edition" \
            --menu "Choose an Aegis OS edition to install:" 20 70 7 \
            "${options[@]}" 2>&1 >/dev/tty)
    elif $HAS_WHIPTAIL; then
        result=$(whiptail --clear --backtitle "Aegis OS USB Creator" \
            --title "Select Edition" \
            --menu "Choose an Aegis OS edition to install:" 20 70 7 \
            "${options[@]}" 2>&1 >/dev/tty)
    fi
    
    if [[ -n "$result" ]]; then
        SELECTED_EDITION="$result"
        return 0
    fi
    return 1
}

select_edition_text() {
    echo
    print_color "$WHITE" "Available Aegis OS Editions:"
    echo
    
    for key in $(echo "${!EDITIONS[@]}" | tr ' ' '\n' | sort -n); do
        IFS='|' read -r id name price desc <<< "${EDITIONS[$key]}"
        print_color "$CYAN" "  [$key] $name"
        print_color "$GREEN" "      Price: $price"
        print_color "$WHITE" "      Features: $desc"
        echo
    done
    
    while true; do
        echo -n "Enter edition number (1-7): "
        read -r choice
        if [[ -n "${EDITIONS[$choice]}" ]]; then
            SELECTED_EDITION="$choice"
            return 0
        else
            print_color "$RED" "Invalid selection. Please enter a number between 1 and 7."
        fi
    done
}

select_edition() {
    if $HAS_DIALOG || $HAS_WHIPTAIL; then
        select_edition_dialog
    else
        select_edition_text
    fi
    
    if [[ -z "$SELECTED_EDITION" ]]; then
        print_color "$RED" "No edition selected. Exiting."
        exit 1
    fi
    
    IFS='|' read -r id name price desc <<< "${EDITIONS[$SELECTED_EDITION]}"
    
    echo
    print_color "$GREEN" "✓ Selected: $name ($price)"
    print_color "$WHITE" "  Features: $desc"
    log "INFO" "Selected edition: $name ($id)"
    
    if [[ "$price" != "FREE" ]]; then
        echo
        print_color "$YELLOW" "This is a paid edition. Enter your license key or press Enter to skip."
        print_color "$WHITE" "(You can enter the license key later during Aegis OS setup)"
        echo -n "License key: "
        read -r LICENSE_KEY
        if [[ -n "$LICENSE_KEY" ]]; then
            log "INFO" "License key provided for $name edition"
        fi
    fi
}

is_system_drive() {
    local device="$1"
    
    local root_device=$(findmnt -n -o SOURCE / 2>/dev/null | sed 's/[0-9]*$//' | sed 's/p[0-9]*$//')
    if [[ "$device" == "$root_device" ]]; then
        return 0
    fi
    
    local boot_device=$(findmnt -n -o SOURCE /boot 2>/dev/null | sed 's/[0-9]*$//' | sed 's/p[0-9]*$//')
    if [[ -n "$boot_device" ]] && [[ "$device" == "$boot_device" ]]; then
        return 0
    fi
    
    local efi_device=$(findmnt -n -o SOURCE /boot/efi 2>/dev/null | sed 's/[0-9]*$//' | sed 's/p[0-9]*$//')
    if [[ -n "$efi_device" ]] && [[ "$device" == "$efi_device" ]]; then
        return 0
    fi
    
    return 1
}

get_usb_drives() {
    local drives=()
    
    while IFS= read -r line; do
        local name=$(echo "$line" | awk '{print $1}')
        local size=$(echo "$line" | awk '{print $2}')
        local type=$(echo "$line" | awk '{print $3}')
        local rm=$(echo "$line" | awk '{print $4}')
        local tran=$(echo "$line" | awk '{print $5}')
        local model=$(echo "$line" | cut -d' ' -f6-)
        
        if [[ "$type" == "disk" ]] && [[ "$rm" == "1" || "$tran" == "usb" ]]; then
            local device="/dev/$name"
            
            if is_system_drive "$device"; then
                log "INFO" "Skipping system drive: $device"
                continue
            fi
            
            local size_bytes=$(lsblk -b -n -o SIZE "$device" 2>/dev/null | head -1)
            if [[ -n "$size_bytes" ]] && [[ $size_bytes -gt 0 ]]; then
                [[ -z "$model" ]] && model="USB Drive"
                drives+=("$name|$size|$model|$size_bytes")
            fi
        fi
    done < <(lsblk -d -n -o NAME,SIZE,TYPE,RM,TRAN,MODEL 2>/dev/null)
    
    printf '%s\n' "${drives[@]}"
}

select_drive_dialog() {
    local drives=()
    local options=()
    local idx=1
    
    while IFS= read -r drive; do
        [[ -z "$drive" ]] && continue
        IFS='|' read -r name size model size_bytes <<< "$drive"
        drives+=("$drive")
        options+=("$idx" "$name ($size) - $model")
        ((idx++))
    done < <(get_usb_drives)
    
    if [[ ${#drives[@]} -eq 0 ]]; then
        if $HAS_DIALOG; then
            dialog --msgbox "No USB drives detected.\n\nPlease insert a USB drive and try again." 8 50
        elif $HAS_WHIPTAIL; then
            whiptail --msgbox "No USB drives detected.\n\nPlease insert a USB drive and try again." 8 50
        fi
        return 1
    fi
    
    local result
    if $HAS_DIALOG; then
        result=$(dialog --clear --backtitle "Aegis OS USB Creator" \
            --title "Select USB Drive" \
            --menu "WARNING: All data on the selected drive will be ERASED!\n\nSelect the USB drive to use:" 18 70 ${#drives[@]} \
            "${options[@]}" 2>&1 >/dev/tty)
    elif $HAS_WHIPTAIL; then
        result=$(whiptail --clear --backtitle "Aegis OS USB Creator" \
            --title "Select USB Drive" \
            --menu "WARNING: All data will be ERASED!\n\nSelect USB drive:" 18 70 ${#drives[@]} \
            "${options[@]}" 2>&1 >/dev/tty)
    fi
    
    if [[ -n "$result" ]]; then
        local selected="${drives[$((result-1))]}"
        IFS='|' read -r name size model size_bytes <<< "$selected"
        SELECTED_DRIVE="$name"
        SELECTED_DRIVE_PATH="/dev/$name"
        return 0
    fi
    return 1
}

select_drive_text() {
    local drives=()
    local idx=1
    
    echo
    print_color "$WHITE" "Detected USB Drives:"
    print_color "$RED" "⚠ WARNING: All data on the selected drive will be permanently ERASED!"
    echo
    
    while IFS= read -r drive; do
        [[ -z "$drive" ]] && continue
        IFS='|' read -r name size model size_bytes <<< "$drive"
        drives+=("$drive")
        print_color "$CYAN" "  [$idx] /dev/$name"
        print_color "$WHITE" "      Size: $size"
        print_color "$WHITE" "      Model: $model"
        echo
        ((idx++))
    done < <(get_usb_drives)
    
    if [[ ${#drives[@]} -eq 0 ]]; then
        print_color "$RED" "No USB drives detected."
        print_color "$YELLOW" "Please insert a USB drive and try again."
        return 1
    fi
    
    while true; do
        echo -n "Enter drive number (1-${#drives[@]}), or 'r' to refresh: "
        read -r choice
        
        if [[ "$choice" == "r" ]] || [[ "$choice" == "R" ]]; then
            return 2  # Signal to refresh
        fi
        
        if [[ "$choice" =~ ^[0-9]+$ ]] && [[ $choice -ge 1 ]] && [[ $choice -le ${#drives[@]} ]]; then
            local selected="${drives[$((choice-1))]}"
            IFS='|' read -r name size model size_bytes <<< "$selected"
            SELECTED_DRIVE="$name"
            SELECTED_DRIVE_PATH="/dev/$name"
            return 0
        else
            print_color "$RED" "Invalid selection."
        fi
    done
}

select_drive() {
    while true; do
        if $HAS_DIALOG || $HAS_WHIPTAIL; then
            select_drive_dialog
            local result=$?
        else
            select_drive_text
            local result=$?
        fi
        
        if [[ $result -eq 2 ]]; then
            continue  # Refresh
        elif [[ $result -eq 0 ]]; then
            break
        else
            print_color "$RED" "Drive selection failed or cancelled."
            exit 1
        fi
    done
    
    echo
    print_color "$GREEN" "✓ Selected: $SELECTED_DRIVE_PATH"
    log "INFO" "Selected drive: $SELECTED_DRIVE_PATH"
}

confirm_operation() {
    local drive_info=$(lsblk -o NAME,SIZE,MODEL "$SELECTED_DRIVE_PATH" 2>/dev/null)
    
    echo
    print_color "$RED" "╔══════════════════════════════════════════════════════════════════╗"
    print_color "$RED" "║                        ⚠ FINAL WARNING ⚠                         ║"
    print_color "$RED" "╚══════════════════════════════════════════════════════════════════╝"
    echo
    print_color "$WHITE" "You are about to ERASE ALL DATA on:"
    echo
    print_color "$CYAN" "$drive_info"
    echo
    
    IFS='|' read -r id name price desc <<< "${EDITIONS[$SELECTED_EDITION]}"
    print_color "$WHITE" "Edition to install: $BOLD$name${NC}"
    echo
    
    print_color "$YELLOW" "This operation CANNOT be undone!"
    echo
    
    if $HAS_DIALOG; then
        dialog --clear --backtitle "Aegis OS USB Creator" \
            --title "Confirm Operation" \
            --yesno "Are you absolutely sure you want to proceed?\n\nDevice: $SELECTED_DRIVE_PATH\nEdition: $name\n\nALL DATA WILL BE ERASED!" 12 60
        return $?
    elif $HAS_WHIPTAIL; then
        whiptail --clear --backtitle "Aegis OS USB Creator" \
            --title "Confirm Operation" \
            --yesno "Are you absolutely sure you want to proceed?\n\nDevice: $SELECTED_DRIVE_PATH\nEdition: $name\n\nALL DATA WILL BE ERASED!" 12 60
        return $?
    else
        echo -n "Type 'YES' (uppercase) to confirm: "
        read -r confirm
        if [[ "$confirm" == "YES" ]]; then
            return 0
        else
            return 1
        fi
    fi
}

download_iso() {
    local iso_path="$TEMP_DIR/aegis-os.iso"
    local download_url="$PRIMARY_MIRROR"
    local download_success=false
    
    print_color "$WHITE" "Downloading Aegis OS base image..."
    print_color "$CYAN" "  Size: ~3.0 GB"
    echo
    
    if [[ -f "$iso_path" ]]; then
        print_color "$YELLOW" "  Found existing download, attempting to resume..."
        log "INFO" "Resuming download from existing file"
    fi
    
    for mirror in "$PRIMARY_MIRROR" "$FALLBACK_MIRROR"; do
        print_color "$WHITE" "  Trying: $(echo $mirror | cut -d'/' -f3)"
        log "INFO" "Attempting download from: $mirror"
        
        if check_command wget; then
            if wget --continue --progress=bar:force:noscroll \
                    --timeout=30 --tries=3 \
                    -O "$iso_path" "$mirror" 2>&1; then
                download_success=true
                break
            fi
        elif check_command curl; then
            if curl -L -C - --progress-bar \
                    --connect-timeout 30 --retry 3 \
                    -o "$iso_path" "$mirror" 2>&1; then
                download_success=true
                break
            fi
        fi
        
        print_color "$YELLOW" "  Mirror failed, trying next..."
        log "WARN" "Mirror failed: $mirror"
    done
    
    if ! $download_success; then
        print_color "$RED" "✗ Download failed from all mirrors"
        log "ERROR" "All mirrors failed"
        return 1
    fi
    
    if [[ ! -f "$iso_path" ]]; then
        print_color "$RED" "✗ Downloaded file not found"
        return 1
    fi
    
    echo
    print_color "$GREEN" "✓ Download completed"
    log "INFO" "Download completed successfully"
    
    echo "$iso_path"
}

verify_checksum() {
    local iso_path="$1"
    
    print_color "$WHITE" "Verifying SHA256 checksum..."
    
    local actual_hash=$(sha256sum "$iso_path" | awk '{print $1}' | tr '[:lower:]' '[:upper:]')
    
    if [[ "$actual_hash" == "$EXPECTED_SHA256" ]]; then
        print_color "$GREEN" "✓ Checksum verified: OK"
        log "INFO" "Checksum verification passed"
        return 0
    else
        print_color "$RED" "✗ Checksum verification FAILED"
        print_color "$RED" "  Expected: $EXPECTED_SHA256"
        print_color "$RED" "  Got:      $actual_hash"
        log "ERROR" "Checksum mismatch: expected $EXPECTED_SHA256, got $actual_hash"
        return 1
    fi
}

unmount_drive() {
    print_color "$WHITE" "Unmounting drive partitions..."
    
    for partition in "${SELECTED_DRIVE_PATH}"*; do
        if mountpoint -q "$partition" 2>/dev/null || mount | grep -q "^$partition "; then
            print_color "$CYAN" "  Unmounting $partition..."
            umount -f "$partition" 2>/dev/null || true
        fi
    done
    
    sync
    sleep 1
    
    print_color "$GREEN" "✓ Drive unmounted"
    log "INFO" "Drive unmounted: $SELECTED_DRIVE_PATH"
}

write_iso() {
    local iso_path="$1"
    local iso_size=$(stat -c%s "$iso_path")
    
    print_color "$WHITE" "Writing image to USB drive..."
    print_color "$CYAN" "  Source: $iso_path"
    print_color "$CYAN" "  Target: $SELECTED_DRIVE_PATH"
    print_color "$YELLOW" "  Do NOT remove the USB drive!"
    echo
    
    log "INFO" "Writing ISO to $SELECTED_DRIVE_PATH"
    
    if check_command pv; then
        pv -s "$iso_size" "$iso_path" | dd of="$SELECTED_DRIVE_PATH" bs=4M conv=fsync status=none 2>> "$LOG_FILE"
    else
        dd if="$iso_path" of="$SELECTED_DRIVE_PATH" bs=4M conv=fsync status=progress 2>&1 | tee -a "$LOG_FILE"
    fi
    
    local dd_result=$?
    
    if [[ $dd_result -ne 0 ]]; then
        print_color "$RED" "✗ Write operation failed"
        log "ERROR" "dd failed with exit code $dd_result"
        return 1
    fi
    
    echo
    print_color "$WHITE" "Syncing data to disk..."
    sync
    
    print_color "$GREEN" "✓ Image written successfully"
    log "INFO" "ISO written successfully to $SELECTED_DRIVE_PATH"
}

write_license_key() {
    if [[ -z "$LICENSE_KEY" ]]; then
        return 0
    fi
    
    print_color "$WHITE" "Saving license key to USB drive..."
    
    sleep 2
    partprobe "$SELECTED_DRIVE_PATH" 2>/dev/null || true
    sleep 2
    
    local mount_point="/tmp/aegis-usb-mount"
    mkdir -p "$mount_point"
    
    local first_partition="${SELECTED_DRIVE_PATH}1"
    if [[ ! -b "$first_partition" ]]; then
        first_partition="${SELECTED_DRIVE_PATH}p1"
    fi
    
    if [[ -b "$first_partition" ]]; then
        if mount "$first_partition" "$mount_point" 2>/dev/null; then
            echo "$LICENSE_KEY" > "$mount_point/aegis-license.key"
            sync
            umount "$mount_point" 2>/dev/null
            print_color "$GREEN" "✓ License key saved"
            log "INFO" "License key written to USB"
        else
            print_color "$YELLOW" "⚠ Could not save license key (will be entered during setup)"
            log "WARN" "Could not mount partition to save license key"
        fi
    else
        print_color "$YELLOW" "⚠ Could not save license key (will be entered during setup)"
    fi
    
    rmdir "$mount_point" 2>/dev/null
}

show_completion() {
    IFS='|' read -r id name price desc <<< "${EDITIONS[$SELECTED_EDITION]}"
    
    echo
    print_color "$GREEN" "╔══════════════════════════════════════════════════════════════════╗"
    print_color "$GREEN" "║                                                                  ║"
    print_color "$GREEN" "║        ✓ Aegis OS USB Drive Created Successfully!               ║"
    print_color "$GREEN" "║                                                                  ║"
    print_color "$GREEN" "╚══════════════════════════════════════════════════════════════════╝"
    echo
    
    print_color "$WHITE" "Edition: ${BOLD}$name${NC}"
    print_color "$WHITE" "USB Drive: $SELECTED_DRIVE_PATH"
    echo
    
    print_color "$CYAN" "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    print_color "$WHITE" " Next Steps:"
    print_color "$CYAN" "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    print_color "$WHITE" " 1. Safely eject the USB drive"
    print_color "$WHITE" " 2. Insert into the target computer"
    print_color "$WHITE" " 3. Restart and boot from USB"
    print_color "$WHITE" " 4. Follow the Aegis OS installer"
    echo
    
    print_color "$YELLOW" " Boot Key Reference:"
    print_color "$WHITE" "   • Dell, Lenovo: F12"
    print_color "$WHITE" "   • HP: F9 or Esc → F9"
    print_color "$WHITE" "   • ASUS, Acer: F2 or Del"
    print_color "$WHITE" "   • MSI: F11"
    print_color "$WHITE" "   • Apple: Hold Option (⌥)"
    echo
    
    print_color "$GREEN" " Thank you for choosing Aegis OS!"
    echo
    
    log "INFO" "USB creation completed successfully"
}

cleanup() {
    log "INFO" "Cleaning up temporary files..."
    
    rm -f "$TEMP_DIR/aegis-os.iso" 2>/dev/null
    rmdir "$TEMP_DIR" 2>/dev/null
}

trap cleanup EXIT

main() {
    check_root "$@"
    init_environment
    
    print_header
    
    print_step 1 6 "Detecting System"
    detect_distro
    print_color "$GREEN" "✓ Detected: $(grep PRETTY_NAME /etc/os-release 2>/dev/null | cut -d'"' -f2 || echo "$DETECTED_DISTRO")"
    print_color "$WHITE" "  Package Manager: $DETECTED_PKG_MGR"
    echo
    sleep 1
    
    print_step 2 6 "Checking Dependencies"
    check_and_install_dependencies
    echo
    sleep 1
    
    print_step 3 6 "System Requirements"
    if ! run_system_checks; then
        print_color "$RED" "System requirements not met. Please resolve the issues above."
        exit 1
    fi
    echo
    
    echo -n "Press Enter to continue..."
    read -r
    
    print_header
    print_step 4 6 "Select Edition"
    select_edition
    echo
    
    print_header
    print_step 5 6 "Select USB Drive"
    select_drive
    echo
    
    if ! confirm_operation; then
        print_color "$YELLOW" "Operation cancelled by user."
        exit 0
    fi
    
    print_header
    print_step 6 6 "Creating Bootable USB"
    echo
    
    local iso_path=$(download_iso)
    if [[ $? -ne 0 ]] || [[ -z "$iso_path" ]]; then
        print_color "$RED" "Download failed. Please check your internet connection."
        exit 1
    fi
    echo
    
    if ! verify_checksum "$iso_path"; then
        print_color "$RED" "Checksum verification failed. The download may be corrupted."
        print_color "$YELLOW" "Delete $iso_path and try again."
        exit 1
    fi
    echo
    
    unmount_drive
    echo
    
    if ! write_iso "$iso_path"; then
        print_color "$RED" "Failed to write image to USB drive."
        exit 1
    fi
    echo
    
    write_license_key
    
    print_header
    show_completion
}

main "$@"
