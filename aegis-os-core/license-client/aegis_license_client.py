#!/usr/bin/env python3

"""
Aegis OS License Client
------------------------
Client-side license validation script that communicates with the Aegis License Server.
Generates hardware ID, validates license, and delivers JWT tokens to the kernel module.
"""

import hashlib
import uuid
import requests
import time
import os
import sys
import json


LICENSE_SERVER_URL = os.environ.get('AEGIS_LICENSE_SERVER', 'http://localhost:5000')
TOKEN_FILE_PATH = '/etc/aegis/auth.token'
CONFIG_FILE_PATH = '/etc/aegis/license.conf'


def generate_hardware_id(use_test_hwid=False):
    """
    Generate a unique hardware ID for this machine.
    
    Uses the MAC address (uuid.getnode()) to create a deterministic hash.
    For testing purposes, can return a fixed test HWID.
    
    Args:
        use_test_hwid: If True, return test HWID for server testing
    
    Returns:
        str: Hexadecimal hardware ID
    """
    if use_test_hwid:
        return "TEST-HWID-Aegis123"
    
    mac_address = uuid.getnode()
    
    mac_bytes = str(mac_address).encode('utf-8')
    
    hw_hash = hashlib.sha256(mac_bytes).hexdigest()
    
    return hw_hash


def communicate_with_server(endpoint, payload, max_retries=3):
    """
    Communicate with the Aegis License Server with exponential backoff.
    
    Implements resilient HTTP communication with automatic retry logic
    for handling temporary network issues.
    
    Args:
        endpoint: API endpoint (e.g., '/activate', '/check_status')
        payload: JSON payload to send
        max_retries: Maximum number of retry attempts
    
    Returns:
        tuple: (success: bool, response_data: dict or None)
    """
    url = f"{LICENSE_SERVER_URL}{endpoint}"
    
    for attempt in range(max_retries):
        try:
            print(f"[INFO] Attempting to connect to {url} (attempt {attempt + 1}/{max_retries})")
            
            response = requests.post(
                url,
                json=payload,
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                print("[SUCCESS] Server responded successfully")
                return True, response.json()
            else:
                print(f"[ERROR] Server returned status code {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"[ERROR] {error_data.get('error', 'Unknown error')}: {error_data.get('message', '')}")
                except:
                    print(f"[ERROR] Response: {response.text}")
                
                if response.status_code in [400, 403, 404]:
                    return False, response.json() if response.text else None
                
        except requests.exceptions.ConnectionError:
            print(f"[ERROR] Connection failed - server may be down")
        except requests.exceptions.Timeout:
            print(f"[ERROR] Request timed out")
        except Exception as e:
            print(f"[ERROR] Unexpected error: {str(e)}")
        
        if attempt < max_retries - 1:
            wait_time = 2 ** attempt
            print(f"[INFO] Waiting {wait_time} seconds before retry...")
            time.sleep(wait_time)
    
    print(f"[FATAL] Failed to communicate with server after {max_retries} attempts")
    return False, None


def deliver_token_to_lkm(token):
    """
    Deliver the JWT token to the kernel module by writing to the token file.
    
    Creates the /etc/aegis directory if it doesn't exist and writes the token
    with appropriate permissions.
    
    Args:
        token: JWT token string to write
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        token_dir = os.path.dirname(TOKEN_FILE_PATH)
        
        if not os.path.exists(token_dir):
            print(f"[INFO] Creating directory {token_dir}")
            try:
                os.makedirs(token_dir, mode=0o755)
            except (PermissionError, OSError):
                print(f"[WARNING] Cannot create {token_dir} (permission or filesystem)")
                print(f"[INFO] Using local directory instead...")
                
                local_token_path = './aegis_auth.token'
                with open(local_token_path, 'w') as f:
                    f.write(token)
                os.chmod(local_token_path, 0o600)
                print(f"[SUCCESS] Token written to {local_token_path}")
                return True
        
        with open(TOKEN_FILE_PATH, 'w') as f:
            f.write(token)
        
        os.chmod(TOKEN_FILE_PATH, 0o600)
        
        print(f"[SUCCESS] Token delivered to {TOKEN_FILE_PATH}")
        return True
        
    except (PermissionError, OSError):
        print(f"[WARNING] Cannot write to {TOKEN_FILE_PATH}")
        print(f"[INFO] Using local directory instead...")
        
        local_token_path = './aegis_auth.token'
        with open(local_token_path, 'w') as f:
            f.write(token)
        os.chmod(local_token_path, 0o600)
        print(f"[SUCCESS] Token written to {local_token_path} instead")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to write token: {str(e)}")
        
        try:
            local_token_path = './aegis_auth.token'
            with open(local_token_path, 'w') as f:
                f.write(token)
            os.chmod(local_token_path, 0o600)
            print(f"[SUCCESS] Token written to {local_token_path} as fallback")
            return True
        except:
            return False


def activate_license(license_key, hardware_id):
    """
    Activate a license key with the server.
    
    Args:
        license_key: The license key to activate
        hardware_id: The hardware ID of this machine
    
    Returns:
        tuple: (success: bool, token: str or None)
    """
    print("\n[INFO] Activating license...")
    
    payload = {
        'license_key': license_key,
        'hardware_id': hardware_id
    }
    
    success, response = communicate_with_server('/activate', payload)
    
    if success and response:
        print(f"[SUCCESS] License activated for tier: {response.get('tier', 'unknown')}")
        print(f"[INFO] Expiry date: {response.get('expiry_date', 'unknown')}")
        return True, response.get('token')
    
    return False, None


def check_license_status(license_key, hardware_id):
    """
    Check license status and get a new JWT token.
    
    Args:
        license_key: The license key to check
        hardware_id: The hardware ID of this machine
    
    Returns:
        tuple: (success: bool, token: str or None)
    """
    print("\n[INFO] Checking license status...")
    
    payload = {
        'license_key': license_key,
        'hardware_id': hardware_id
    }
    
    success, response = communicate_with_server('/check_status', payload)
    
    if success and response:
        print(f"[SUCCESS] License is valid - Tier: {response.get('tier', 'unknown')}")
        print(f"[INFO] Status: {response.get('status', 'unknown')}")
        print(f"[INFO] Expiry date: {response.get('expiry_date', 'unknown')}")
        return True, response.get('token')
    
    return False, None


def save_config(license_key, hardware_id):
    """Save license configuration for future use."""
    config = {
        'license_key': license_key,
        'hardware_id': hardware_id
    }
    
    try:
        config_dir = os.path.dirname(CONFIG_FILE_PATH)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir, mode=0o755)
        
        with open(CONFIG_FILE_PATH, 'w') as f:
            json.dump(config, f)
        os.chmod(CONFIG_FILE_PATH, 0o600)
        print(f"[INFO] Configuration saved to {CONFIG_FILE_PATH}")
    except (PermissionError, OSError):
        local_config = './aegis_license.conf'
        with open(local_config, 'w') as f:
            json.dump(config, f)
        print(f"[INFO] Configuration saved to {local_config}")


def load_config():
    """Load saved license configuration."""
    try:
        if os.path.exists(CONFIG_FILE_PATH):
            with open(CONFIG_FILE_PATH, 'r') as f:
                return json.load(f)
    except:
        pass
    
    local_config = './aegis_license.conf'
    if os.path.exists(local_config):
        with open(local_config, 'r') as f:
            return json.load(f)
    
    return None


def main():
    """Main entry point for the license client."""
    print("=" * 60)
    print("Aegis OS License Client v1.0.0")
    print("=" * 60)
    
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python3 aegis_license_client.py <license_key> [--test]")
        print("  python3 aegis_license_client.py --check")
        print("\nOptions:")
        print("  <license_key>  : Your Aegis OS license key")
        print("  --test         : Use test hardware ID for development")
        print("  --check        : Check existing license status")
        print("\nExample:")
        print("  python3 aegis_license_client.py AEGIS-BASIC-2024-ACTIVE --test")
        sys.exit(1)
    
    if sys.argv[1] == '--check':
        config = load_config()
        if not config:
            print("[ERROR] No saved license configuration found")
            print("[INFO] Please activate a license first")
            sys.exit(1)
        
        license_key = config['license_key']
        hardware_id = config['hardware_id']
        
        success, token = check_license_status(license_key, hardware_id)
    else:
        license_key = sys.argv[1]
        use_test_hwid = '--test' in sys.argv
        
        hardware_id = generate_hardware_id(use_test_hwid)
        print(f"\n[INFO] Hardware ID: {hardware_id}")
        
        success, token = activate_license(license_key, hardware_id)
        
        if success:
            save_config(license_key, hardware_id)
    
    if success and token:
        if deliver_token_to_lkm(token):
            print("\n[SUCCESS] License validation complete!")
            print("[INFO] Aegis OS features are now enabled")
            sys.exit(0)
    
    print("\n[FAILURE] License validation failed")
    sys.exit(1)


if __name__ == '__main__':
    main()
