#!/usr/bin/env python3
"""
Aegis OS Activation Client
Handles single-use license activation to prevent ISO piracy

This module provides:
- Hardware fingerprinting for device binding
- Server-side activation verification
- Local activation cache for offline use
- Activation revocation detection
"""

import os
import sys
import json
import hashlib
import platform
import socket
import uuid
import urllib.request
import urllib.error
import ssl
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any

try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.backends import default_backend
    import base64
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False


ACTIVATION_SERVER_URL = "https://activate.aegis-os.com/api/v1"
ACTIVATION_CACHE_DIR = Path.home() / ".aegis" / "activation"
MAX_ACTIVATIONS_PER_LICENSE = 3
ACTIVATION_CACHE_VALIDITY_DAYS = 30


class HardwareFingerprint:
    """Generates a unique hardware fingerprint for device binding"""
    
    @staticmethod
    def get_machine_id() -> str:
        """Get a unique machine identifier"""
        components = []
        
        try:
            if sys.platform == "win32":
                import subprocess
                result = subprocess.run(
                    ['wmic', 'csproduct', 'get', 'uuid'],
                    capture_output=True, text=True, timeout=5
                )
                for line in result.stdout.strip().split('\n'):
                    line = line.strip()
                    if line and line != 'UUID':
                        components.append(f"wmic:{line}")
                        break
            elif sys.platform == "darwin":
                import subprocess
                result = subprocess.run(
                    ['ioreg', '-rd1', '-c', 'IOPlatformExpertDevice'],
                    capture_output=True, text=True, timeout=5
                )
                for line in result.stdout.split('\n'):
                    if 'IOPlatformUUID' in line:
                        uuid_val = line.split('"')[-2]
                        components.append(f"ioreg:{uuid_val}")
                        break
            else:
                machine_id_paths = [
                    '/etc/machine-id',
                    '/var/lib/dbus/machine-id',
                ]
                for path in machine_id_paths:
                    if os.path.exists(path):
                        with open(path, 'r') as f:
                            components.append(f"machineid:{f.read().strip()}")
                        break
        except Exception:
            pass
        
        try:
            components.append(f"hostname:{socket.gethostname()}")
        except Exception:
            pass
        
        try:
            components.append(f"platform:{platform.platform()}")
            components.append(f"processor:{platform.processor()}")
        except Exception:
            pass
        
        try:
            components.append(f"node:{uuid.getnode()}")
        except Exception:
            pass
        
        if not components:
            components.append(f"fallback:{uuid.uuid4().hex}")
        
        fingerprint_data = "|".join(sorted(components))
        fingerprint_hash = hashlib.sha256(fingerprint_data.encode()).hexdigest()
        
        return fingerprint_hash[:32]
    
    @staticmethod
    def get_fingerprint_info() -> Dict[str, str]:
        """Get detailed fingerprint information"""
        return {
            "machine_id": HardwareFingerprint.get_machine_id(),
            "hostname": socket.gethostname(),
            "platform": platform.system(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "timestamp": datetime.utcnow().isoformat()
        }


class ActivationCache:
    """Manages local activation cache for offline verification"""
    
    def __init__(self, cache_dir: Path = ACTIVATION_CACHE_DIR):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_path(self, license_key: str) -> Path:
        """Get cache file path for a license key"""
        key_hash = hashlib.sha256(license_key.encode()).hexdigest()[:16]
        return self.cache_dir / f"activation_{key_hash}.json"
    
    def save_activation(self, license_key: str, activation_data: Dict[str, Any]) -> bool:
        """Save activation data to cache"""
        try:
            cache_path = self._get_cache_path(license_key)
            activation_data["cached_at"] = datetime.utcnow().isoformat()
            activation_data["machine_id"] = HardwareFingerprint.get_machine_id()
            
            with open(cache_path, 'w') as f:
                json.dump(activation_data, f, indent=2)
            
            os.chmod(cache_path, 0o600)
            return True
        except Exception:
            return False
    
    def load_activation(self, license_key: str) -> Optional[Dict[str, Any]]:
        """Load activation data from cache"""
        try:
            cache_path = self._get_cache_path(license_key)
            if not cache_path.exists():
                return None
            
            with open(cache_path, 'r') as f:
                data = json.load(f)
            
            cached_machine_id = data.get("machine_id")
            current_machine_id = HardwareFingerprint.get_machine_id()
            
            if cached_machine_id != current_machine_id:
                return None
            
            cached_at = datetime.fromisoformat(data.get("cached_at", "2000-01-01"))
            max_age = timedelta(days=ACTIVATION_CACHE_VALIDITY_DAYS)
            
            if datetime.utcnow() - cached_at > max_age:
                return None
            
            return data
        except Exception:
            return None
    
    def invalidate(self, license_key: str) -> bool:
        """Remove cached activation"""
        try:
            cache_path = self._get_cache_path(license_key)
            if cache_path.exists():
                cache_path.unlink()
            return True
        except Exception:
            return False


class ActivationClient:
    """
    Handles license activation with the Aegis activation server
    
    Activation flow:
    1. Check local cache for valid activation
    2. If no cache, contact server to activate
    3. Server checks if license is valid and not over-activated
    4. If valid, server records activation and returns token
    5. Client caches activation token locally
    """
    
    def __init__(self, server_url: str = ACTIVATION_SERVER_URL):
        self.server_url = server_url
        self.cache = ActivationCache()
        self.machine_id = HardwareFingerprint.get_machine_id()
    
    def _get_ssl_context(self) -> ssl.SSLContext:
        """Get SSL context for HTTPS requests"""
        try:
            return ssl.create_default_context()
        except Exception:
            return ssl._create_unverified_context()
    
    def _make_request(self, endpoint: str, data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Make a request to the activation server"""
        try:
            url = f"{self.server_url}/{endpoint}"
            json_data = json.dumps(data).encode('utf-8')
            
            request = urllib.request.Request(
                url,
                data=json_data,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'AegisOS-Installer/2.1.0'
                },
                method='POST'
            )
            
            context = self._get_ssl_context()
            
            with urllib.request.urlopen(request, timeout=15, context=context) as response:
                response_data = json.loads(response.read().decode('utf-8'))
                return True, response_data
                
        except urllib.error.HTTPError as e:
            try:
                error_data = json.loads(e.read().decode('utf-8'))
                return False, error_data
            except:
                return False, {"error": f"HTTP {e.code}: {e.reason}"}
        except urllib.error.URLError as e:
            return False, {"error": f"Connection failed: {e.reason}"}
        except socket.timeout:
            return False, {"error": "Connection timed out"}
        except Exception as e:
            return False, {"error": str(e)}
    
    def activate(self, license_key: str, edition: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Activate a license for this machine
        
        Returns:
            (success, message, activation_data)
        """
        cached = self.cache.load_activation(license_key)
        if cached:
            if cached.get("edition") == edition:
                return True, "License already activated on this device", cached
        
        fingerprint_info = HardwareFingerprint.get_fingerprint_info()
        
        activation_request = {
            "license_key": license_key,
            "edition": edition,
            "machine_id": self.machine_id,
            "fingerprint": fingerprint_info,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        success, response = self._make_request("activate", activation_request)
        
        if success:
            activation_data = {
                "license_key": license_key,
                "edition": edition,
                "activation_id": response.get("activation_id"),
                "activated_at": response.get("activated_at"),
                "activations_used": response.get("activations_used", 1),
                "max_activations": response.get("max_activations", MAX_ACTIVATIONS_PER_LICENSE),
                "server_verified": True
            }
            
            self.cache.save_activation(license_key, activation_data)
            
            activations_left = activation_data["max_activations"] - activation_data["activations_used"]
            message = f"License activated successfully ({activations_left} activations remaining)"
            
            return True, message, activation_data
        else:
            error = response.get("error", "Unknown error")
            
            if "already activated" in error.lower():
                return False, "This license has reached its maximum number of activations", None
            elif "revoked" in error.lower():
                self.cache.invalidate(license_key)
                return False, "This license has been revoked", None
            elif "expired" in error.lower():
                return False, "This license has expired", None
            elif "invalid" in error.lower():
                return False, "Invalid license key", None
            else:
                return False, f"Activation failed: {error}", None
    
    def verify(self, license_key: str, edition: str) -> Tuple[bool, str]:
        """
        Verify a license is still valid
        
        Returns:
            (valid, message)
        """
        cached = self.cache.load_activation(license_key)
        if cached and cached.get("edition") == edition:
            return True, "License verified (cached)"
        
        success, response = self._make_request("verify", {
            "license_key": license_key,
            "machine_id": self.machine_id
        })
        
        if success:
            return True, "License verified"
        else:
            error = response.get("error", "Verification failed")
            return False, error
    
    def check_offline(self, license_key: str, edition: str) -> Tuple[bool, str]:
        """
        Check activation status using only local cache (offline mode)
        
        Returns:
            (valid, message)
        """
        cached = self.cache.load_activation(license_key)
        
        if not cached:
            return False, "No activation found for this device (online activation required)"
        
        if cached.get("edition") != edition:
            return False, f"License is for {cached.get('edition')}, not {edition}"
        
        return True, "License verified offline"
    
    def deactivate(self, license_key: str) -> Tuple[bool, str]:
        """
        Deactivate license from this machine (frees up an activation slot)
        
        Returns:
            (success, message)
        """
        success, response = self._make_request("deactivate", {
            "license_key": license_key,
            "machine_id": self.machine_id
        })
        
        self.cache.invalidate(license_key)
        
        if success:
            return True, "License deactivated from this device"
        else:
            return True, "License removed from this device"


def check_single_activation(license_key: str, edition: str, offline_allowed: bool = True) -> Tuple[bool, str]:
    """
    Convenience function to check if a license can be used
    
    Args:
        license_key: The license key to check
        edition: Expected edition
        offline_allowed: Whether to allow offline verification
    
    Returns:
        (can_proceed, message)
    """
    client = ActivationClient()
    
    success, message, _ = client.activate(license_key, edition)
    
    if success:
        return True, message
    
    if offline_allowed and "Connection" in message or "timed out" in message.lower():
        offline_success, offline_message = client.check_offline(license_key, edition)
        if offline_success:
            return True, f"{offline_message} (server unreachable)"
    
    return False, message


if __name__ == "__main__":
    print("Aegis OS Activation Client")
    print("=" * 40)
    print()
    print(f"Machine ID: {HardwareFingerprint.get_machine_id()}")
    print()
    
    info = HardwareFingerprint.get_fingerprint_info()
    print("Device Information:")
    for key, value in info.items():
        print(f"  {key}: {value}")
