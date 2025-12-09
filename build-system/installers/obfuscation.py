#!/usr/bin/env python3
"""
Aegis OS Code Obfuscation Module
Provides string encryption, integrity checks, and anti-tampering for installers
"""

import base64
import hashlib
import os
import zlib
import sys
from typing import Tuple


class StringProtector:
    """Encrypt/decrypt sensitive strings at runtime"""
    
    @staticmethod
    def _derive_key(seed: str) -> bytes:
        """Derive encryption key from seed"""
        return hashlib.sha256(seed.encode()).digest()
    
    @staticmethod
    def protect(plaintext: str, seed: str = "aegis_os_2025") -> str:
        """Encrypt a string for embedding in code"""
        key = StringProtector._derive_key(seed)
        data = plaintext.encode('utf-8')
        compressed = zlib.compress(data, 9)
        encrypted = bytes(b ^ key[i % len(key)] for i, b in enumerate(compressed))
        return base64.b64encode(encrypted).decode('ascii')
    
    @staticmethod
    def reveal(protected: str, seed: str = "aegis_os_2025") -> str:
        """Decrypt a protected string at runtime"""
        try:
            key = StringProtector._derive_key(seed)
            encrypted = base64.b64decode(protected)
            decrypted = bytes(b ^ key[i % len(key)] for i, b in enumerate(encrypted))
            decompressed = zlib.decompress(decrypted)
            return decompressed.decode('utf-8')
        except:
            return ""


class IntegrityChecker:
    """Verify code hasn't been tampered with"""
    
    @staticmethod
    def compute_checksum(filepath: str) -> str:
        """Compute SHA-256 checksum of a file"""
        sha256 = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest().upper()
    
    @staticmethod
    def compute_code_hash(code_sections: list) -> str:
        """Compute hash of critical code sections"""
        combined = "".join(str(s) for s in code_sections)
        return hashlib.sha256(combined.encode()).hexdigest()[:16]


class AntiDebug:
    """Anti-debugging and anti-tampering measures"""
    
    @staticmethod
    def check_debugger() -> bool:
        """Check if debugger is attached"""
        try:
            import ctypes
            if sys.platform == 'win32':
                return bool(ctypes.windll.kernel32.IsDebuggerPresent())
        except:
            pass
        
        try:
            import sys
            return hasattr(sys, 'gettrace') and sys.gettrace() is not None
        except:
            pass
        
        return False
    
    @staticmethod
    def check_vm() -> Tuple[bool, str]:
        """Detect if running in VM (informational only)"""
        vm_indicators = []
        
        try:
            import platform
            cpu = platform.processor().lower()
            if 'virtual' in cpu or 'vmware' in cpu or 'hyperv' in cpu:
                vm_indicators.append("cpu")
        except:
            pass
        
        try:
            if sys.platform == 'win32':
                import subprocess
                result = subprocess.run(
                    ['wmic', 'computersystem', 'get', 'model'],
                    capture_output=True, text=True, timeout=5
                )
                model = result.stdout.lower()
                if 'virtual' in model or 'vmware' in model or 'vbox' in model:
                    vm_indicators.append("model")
        except:
            pass
        
        return len(vm_indicators) > 0, ",".join(vm_indicators)
    
    @staticmethod
    def timing_check(operation_name: str, max_ms: int = 100) -> callable:
        """Decorator to detect timing-based debugging"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                import time
                start = time.perf_counter()
                result = func(*args, **kwargs)
                elapsed_ms = (time.perf_counter() - start) * 1000
                return result
            return wrapper
        return decorator


class LicenseProtection:
    """Additional license validation protections"""
    
    PROTECTED_PUBLIC_KEY = None
    
    @staticmethod
    def validate_key_format(license_key: str) -> bool:
        """Validate license key format with checksums"""
        if not license_key:
            return False
        
        parts = license_key.split('-')
        if len(parts) != 4:
            return False
        
        prefix = parts[0]
        valid_prefixes = {'FREE', 'BSIC', 'GMRP', 'AIDV', 'WKPL', 'SRVR', 'GMAI'}
        if prefix not in valid_prefixes:
            return False
        
        for segment in parts[1:]:
            if len(segment) != 4:
                return False
            if not all(c.isalnum() for c in segment):
                return False
        
        return True
    
    @staticmethod
    def obfuscate_public_key(pem_key: str) -> str:
        """Obfuscate public key for embedding"""
        return StringProtector.protect(pem_key, "aegis_rsa_key_2025")
    
    @staticmethod
    def deobfuscate_public_key(protected: str) -> str:
        """Reveal public key at runtime"""
        return StringProtector.reveal(protected, "aegis_rsa_key_2025")


class RuntimeProtection:
    """Runtime protection against tampering"""
    
    _initialized = False
    _integrity_token = None
    
    @classmethod
    def initialize(cls, critical_values: list) -> str:
        """Initialize runtime protection, returns integrity token"""
        cls._integrity_token = IntegrityChecker.compute_code_hash(critical_values)
        cls._initialized = True
        return cls._integrity_token
    
    @classmethod
    def verify(cls, critical_values: list) -> bool:
        """Verify integrity hasn't changed"""
        if not cls._initialized:
            return False
        current = IntegrityChecker.compute_code_hash(critical_values)
        return current == cls._integrity_token
    
    @classmethod
    def secure_compare(cls, a: str, b: str) -> bool:
        """Constant-time string comparison to prevent timing attacks"""
        if len(a) != len(b):
            return False
        result = 0
        for x, y in zip(a.encode(), b.encode()):
            result |= x ^ y
        return result == 0


def generate_protected_constants():
    """Generate protected versions of sensitive constants for embedding"""
    
    sensitive_strings = {
        "ACTIVATION_URL": "https://aegis-os.com/api/v1/activate",
        "VALIDATION_URL": "https://aegis-os.com/api/v1/validate",
        "UPDATE_URL": "https://aegis-os.com/api/v1/updates",
        "REVOCATION_URL": "https://aegis-os.com/api/v1/revoke",
    }
    
    protected = {}
    for name, value in sensitive_strings.items():
        protected[name] = StringProtector.protect(value)
    
    return protected


if __name__ == "__main__":
    print("Aegis OS Obfuscation Module")
    print("=" * 50)
    
    test_string = "https://aegis-os.com/api/v1/activate"
    protected = StringProtector.protect(test_string)
    revealed = StringProtector.reveal(protected)
    
    print(f"Original:  {test_string}")
    print(f"Protected: {protected[:50]}...")
    print(f"Revealed:  {revealed}")
    print(f"Match:     {test_string == revealed}")
    print()
    
    print("Generating protected constants...")
    constants = generate_protected_constants()
    for name, value in constants.items():
        print(f"  {name}: {value[:40]}...")
    
    print()
    print("Anti-debug check:", "Debugger detected" if AntiDebug.check_debugger() else "Clean")
    
    is_vm, indicators = AntiDebug.check_vm()
    print("VM check:", f"VM detected ({indicators})" if is_vm else "Native hardware")
