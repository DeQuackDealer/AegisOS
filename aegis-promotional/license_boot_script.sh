#!/bin/bash
#
# Aegis OS License Validation Boot Script
# This script runs during system boot to validate the license and configure features
#

set -e

AEGIS_CONFIG_DIR="/etc/aegis"
LICENSE_FILE="$AEGIS_CONFIG_DIR/license.json"
FEATURES_FILE="$AEGIS_CONFIG_DIR/features.json"
LICENSE_CACHE="$AEGIS_CONFIG_DIR/.license_cache"
FALLBACK_MODE="freemium"

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}==================================${NC}"
echo -e "${BLUE}     Aegis OS License Manager     ${NC}"
echo -e "${BLUE}==================================${NC}"

# Function to get hardware fingerprint
get_hardware_id() {
    # Combine multiple hardware identifiers for a unique fingerprint
    hw_id=$(cat /sys/class/dmi/id/product_uuid 2>/dev/null || echo "unknown")
    mac_addr=$(ip link show | awk '/ether/ {print $2}' | head -1 || echo "unknown")
    cpu_id=$(cat /proc/cpuinfo | grep "model name" | head -1 | md5sum | cut -d' ' -f1)
    
    echo "${hw_id}-${mac_addr}-${cpu_id}" | md5sum | cut -d' ' -f1
}

# Function to prompt for license key
prompt_for_license() {
    echo -e "\n${YELLOW}Please enter your Aegis OS license key:${NC}"
    echo -e "${YELLOW}Format: AEGIS-XXX-XXXXX-XXXXX-XXXXX${NC}"
    echo -e "${YELLOW}(Press Enter to continue with Freemium edition)${NC}\n"
    
    read -t 30 -p "License Key: " license_key || true
    
    if [ -z "$license_key" ]; then
        echo -e "\n${YELLOW}No license entered. Starting in Freemium mode...${NC}"
        return 1
    fi
    
    echo "$license_key"
    return 0
}

# Function to validate license online
validate_license_online() {
    local license_key=$1
    local hw_id=$2
    
    # Try to validate with the Aegis license server
    response=$(curl -s -X POST https://aegis-os.com/api/validate-license \
        -H "Content-Type: application/json" \
        -d "{\"license_key\": \"$license_key\", \"hardware_id\": \"$hw_id\"}" \
        --connect-timeout 5 \
        2>/dev/null || echo "{\"valid\": false, \"tier\": \"freemium\"}")
    
    echo "$response"
}

# Function to apply tier features
apply_tier_features() {
    local tier=$1
    
    echo -e "\n${GREEN}Configuring Aegis OS - $tier Edition${NC}"
    
    case "$tier" in
        "basic")
            echo "✓ Enhanced Security Suite"
            echo "✓ Encrypted Storage"
            echo "✓ VPN Client"
            echo "✓ Anti-Ransomware Protection"
            systemctl enable aegis-security.service 2>/dev/null || true
            systemctl enable aegis-vpn.service 2>/dev/null || true
            ;;
            
        "gamer")
            echo "✓ NVIDIA/AMD Drivers"
            echo "✓ Gaming Mode Optimization"
            echo "✓ Ray Tracing & DLSS 3"
            echo "✓ <5ms Input Latency"
            echo "✓ RGB Ecosystem Support"
            modprobe nvidia 2>/dev/null || true
            systemctl enable aegis-gaming.service 2>/dev/null || true
            echo "performance" > /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor 2>/dev/null || true
            ;;
            
        "ai-dev")
            echo "✓ CUDA 12.3 & cuDNN"
            echo "✓ PyTorch & TensorFlow"
            echo "✓ Jupyter Lab"
            echo "✓ ML Libraries (100+)"
            echo "✓ Docker & Kubernetes"
            modprobe nvidia-uvm 2>/dev/null || true
            systemctl enable docker.service 2>/dev/null || true
            systemctl enable jupyter.service 2>/dev/null || true
            ;;
            
        "server")
            echo "✓ Enterprise Security"
            echo "✓ Kubernetes Orchestration"
            echo "✓ High Availability"
            echo "✓ Auto-scaling"
            echo "✓ 100K+ RPS Support"
            systemctl enable kubernetes.service 2>/dev/null || true
            systemctl enable aegis-ha.service 2>/dev/null || true
            sysctl -w net.core.somaxconn=65535 2>/dev/null || true
            ;;
            
        *)
            echo "✓ Basic Desktop Environment"
            echo "✓ Open-source Drivers"
            echo "✓ Community Features"
            echo -e "${YELLOW}Upgrade to unlock premium features!${NC}"
            ;;
    esac
    
    # Save features configuration
    echo "{\"tier\": \"$tier\", \"timestamp\": \"$(date -Iseconds)\"}" > "$FEATURES_FILE"
}

# Main execution
main() {
    # Create config directory if it doesn't exist
    mkdir -p "$AEGIS_CONFIG_DIR"
    
    # Get hardware ID
    HW_ID=$(get_hardware_id)
    echo -e "${BLUE}Hardware ID: ${HW_ID:0:16}...${NC}"
    
    # Check for cached license
    if [ -f "$LICENSE_CACHE" ]; then
        cached_license=$(cat "$LICENSE_CACHE" 2>/dev/null)
        if [ ! -z "$cached_license" ]; then
            echo -e "${GREEN}Found cached license${NC}"
            LICENSE_KEY="$cached_license"
        fi
    else
        # No cached license, prompt user
        if prompt_for_license; then
            LICENSE_KEY=$(prompt_for_license)
        else
            LICENSE_KEY=""
        fi
    fi
    
    # Validate license if provided
    if [ ! -z "$LICENSE_KEY" ]; then
        echo -e "\n${BLUE}Validating license...${NC}"
        
        # Try online validation first
        validation_result=$(validate_license_online "$LICENSE_KEY" "$HW_ID")
        
        # Parse validation result
        is_valid=$(echo "$validation_result" | python3 -c "import sys, json; print(json.load(sys.stdin).get('valid', False))" 2>/dev/null || echo "false")
        tier=$(echo "$validation_result" | python3 -c "import sys, json; print(json.load(sys.stdin).get('tier', 'freemium'))" 2>/dev/null || echo "freemium")
        
        if [ "$is_valid" = "True" ] || [ "$is_valid" = "true" ]; then
            echo -e "${GREEN}✓ License validated successfully!${NC}"
            echo "$LICENSE_KEY" > "$LICENSE_CACHE"
            echo "$validation_result" > "$LICENSE_FILE"
        else
            echo -e "${RED}✗ Invalid or expired license${NC}"
            tier="freemium"
            rm -f "$LICENSE_CACHE" 2>/dev/null
        fi
    else
        tier="freemium"
    fi
    
    # Apply features for the validated tier
    apply_tier_features "$tier"
    
    # Set system branding
    echo "Aegis OS - $tier Edition" > /etc/aegis-release
    
    echo -e "\n${GREEN}Aegis OS initialization complete!${NC}"
    echo -e "${BLUE}==================================${NC}\n"
    
    # Continue with normal boot
    exit 0
}

# Run main function
main