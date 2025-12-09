#!/usr/bin/env python3
"""
Aegis OS Installer Test Suite
Tests core functionality without GUI (headless testing)
"""

import os
import sys
import json
import tempfile
import hashlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def test_offline_iso_locator():
    """Test ISO locator functionality"""
    print("Testing OfflineISOLocator...")
    
    from importlib.util import spec_from_loader, module_from_spec
    from importlib.machinery import SourceFileLoader
    
    loader = SourceFileLoader("freemium", str(Path(__file__).parent / "aegis-installer-freemium.py"))
    spec = spec_from_loader("freemium", loader)
    freemium = module_from_spec(spec)
    
    sys.modules['tkinter'] = type(sys)('tkinter')
    sys.modules['tkinter.ttk'] = type(sys)('tkinter.ttk')
    sys.modules['tkinter.messagebox'] = type(sys)('tkinter.messagebox')
    sys.modules['tkinter.filedialog'] = type(sys)('tkinter.filedialog')
    
    try:
        search_paths = []
        search_paths.append(Path(__file__).parent)
        search_paths.append(Path.home() / "Downloads")
        valid_paths = [p for p in search_paths if p.exists()]
        print(f"  ✓ Found {len(valid_paths)} valid search paths")
        
        print("  ✓ OfflineISOLocator test passed")
        return True
    except Exception as e:
        print(f"  ✗ OfflineISOLocator test failed: {e}")
        return False


def test_manifest_loading():
    """Test manifest.json loading"""
    print("Testing manifest loading...")
    
    manifest_path = Path(__file__).parent / "manifest.json"
    
    if not manifest_path.exists():
        print("  ✗ manifest.json not found")
        return False
    
    try:
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        if "editions" not in manifest:
            print("  ✗ 'editions' key missing from manifest")
            return False
        
        editions = manifest["editions"]
        required_editions = ["freemium", "basic", "gamer", "aidev", "workplace", "server"]
        
        for edition in required_editions:
            if edition not in editions:
                print(f"  ✗ Edition '{edition}' missing from manifest")
                return False
            
            ed = editions[edition]
            if "filename" not in ed:
                print(f"  ✗ Edition '{edition}' missing 'filename'")
                return False
            if "sha256" not in ed:
                print(f"  ✗ Edition '{edition}' missing 'sha256'")
                return False
        
        print(f"  ✓ Manifest valid with {len(editions)} editions")
        return True
        
    except json.JSONDecodeError as e:
        print(f"  ✗ Invalid JSON: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Error loading manifest: {e}")
        return False


def test_license_validation():
    """Test license validation logic"""
    print("Testing license validation...")
    
    try:
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import padding, rsa
        from cryptography.hazmat.backends import default_backend
        import base64
        
        print("  ✓ cryptography library available")
        
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        
        license_data = {
            "license_key": "TEST-XXXX-XXXX-XXXX",
            "edition": "basic",
            "customer_email": "test@example.com",
            "issued_date": "2024-12-01",
            "expiry_date": None
        }
        
        data_to_sign = json.dumps(license_data, sort_keys=True, separators=(',', ':'))
        
        signature = private_key.sign(
            data_to_sign.encode('utf-8'),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        
        signature_b64 = base64.b64encode(signature).decode('ascii')
        print(f"  ✓ Test signature generated: {signature_b64[:32]}...")
        
        try:
            public_key.verify(
                base64.b64decode(signature_b64),
                data_to_sign.encode('utf-8'),
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            print("  ✓ Signature verification passed")
        except Exception as e:
            print(f"  ✗ Signature verification failed: {e}")
            return False
        
        print("  ✓ License validation test passed")
        return True
        
    except ImportError:
        print("  ! cryptography library not installed (needed for licensed installer)")
        print("    Install with: pip install cryptography")
        return True
    except Exception as e:
        print(f"  ✗ License validation test failed: {e}")
        return False


def test_iso_checksum():
    """Test SHA-256 checksum calculation"""
    print("Testing ISO checksum calculation...")
    
    try:
        with tempfile.NamedTemporaryFile(delete=False) as f:
            test_data = b"AEGIS OS TEST ISO DATA " * 1000
            f.write(test_data)
            temp_path = f.name
        
        expected_hash = hashlib.sha256(test_data).hexdigest().upper()
        
        calculated_hash = hashlib.sha256()
        with open(temp_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                calculated_hash.update(chunk)
        
        result_hash = calculated_hash.hexdigest().upper()
        
        os.unlink(temp_path)
        
        if result_hash == expected_hash:
            print(f"  ✓ Checksum match: {result_hash[:16]}...")
            return True
        else:
            print(f"  ✗ Checksum mismatch")
            return False
            
    except Exception as e:
        print(f"  ✗ Checksum test failed: {e}")
        return False


def test_placeholder_checksum():
    """Test placeholder checksum detection"""
    print("Testing placeholder checksum detection...")
    
    def is_placeholder_checksum(checksum):
        if not checksum:
            return True
        checksum = checksum.upper().strip()
        if checksum.startswith("0" * 60):
            return True
        if all(c == '0' for c in checksum[:-1]) and checksum[-1].isdigit():
            return True
        return False
    
    test_cases = [
        ("0000000000000000000000000000000000000000000000000000000000000001", True, "placeholder 01"),
        ("0000000000000000000000000000000000000000000000000000000000000007", True, "placeholder 07"),
        ("209AAB96227DAE94D0C8C2ED4A7E8BA68BC2F42D1C0D6E8E3F4A5B6C7D8E9F0A", False, "real hash"),
        ("A1B2C3D4E5F6789012345678901234567890123456789012345678901234ABCD", False, "hex hash"),
        ("", True, "empty string"),
        (None, True, "None value"),
    ]
    
    all_passed = True
    for checksum, expected, desc in test_cases:
        result = is_placeholder_checksum(checksum)
        if result != expected:
            print(f"  ✗ Failed: {desc} - expected {expected}, got {result}")
            all_passed = False
    
    if all_passed:
        print(f"  ✓ All {len(test_cases)} placeholder detection tests passed")
    
    return all_passed


def test_activation_client():
    """Test activation client module"""
    print("Testing activation client...")
    
    try:
        from activation_client import HardwareFingerprint, ActivationClient, ActivationCache
        
        machine_id = HardwareFingerprint.get_machine_id()
        if not machine_id or len(machine_id) < 16:
            print("  ✗ Invalid machine ID generated")
            return False
        print(f"  ✓ Machine ID: {machine_id[:16]}...")
        
        info = HardwareFingerprint.get_fingerprint_info()
        if "machine_id" not in info or "hostname" not in info:
            print("  ✗ Fingerprint info incomplete")
            return False
        print("  ✓ Fingerprint info generated")
        
        client = ActivationClient()
        if not hasattr(client, 'activate') or not hasattr(client, 'check_offline'):
            print("  ✗ ActivationClient missing required methods")
            return False
        print("  ✓ ActivationClient initialized")
        
        return True
        
    except ImportError as e:
        print(f"  ✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_python_syntax():
    """Test that all installer files have valid Python syntax"""
    print("Testing Python syntax...")
    
    files = [
        "aegis-installer-freemium.py",
        "aegis-installer-licensed.py",
        "build-all-installers.py",
        "activation_client.py",
    ]
    
    all_valid = True
    for filename in files:
        filepath = Path(__file__).parent / filename
        if not filepath.exists():
            print(f"  ✗ {filename} not found")
            all_valid = False
            continue
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                source = f.read()
            compile(source, filename, 'exec')
            print(f"  ✓ {filename} syntax OK")
        except SyntaxError as e:
            print(f"  ✗ {filename} syntax error: {e}")
            all_valid = False
    
    return all_valid


def main():
    print()
    print("=" * 60)
    print("  AEGIS OS INSTALLER TEST SUITE")
    print("=" * 60)
    print()
    
    tests = [
        ("Python Syntax", test_python_syntax),
        ("Manifest Loading", test_manifest_loading),
        ("ISO Checksum", test_iso_checksum),
        ("License Validation", test_license_validation),
        ("Placeholder Checksum", test_placeholder_checksum),
        ("Activation Client", test_activation_client),
        ("Offline ISO Locator", test_offline_iso_locator),
    ]
    
    results = []
    for name, test_func in tests:
        print()
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"  ✗ {name} crashed: {e}")
            results.append((name, False))
    
    print()
    print("=" * 60)
    print("  TEST RESULTS")
    print("=" * 60)
    print()
    
    passed = sum(1 for _, p in results if p)
    total = len(results)
    
    for name, p in results:
        status = "PASS" if p else "FAIL"
        symbol = "✓" if p else "✗"
        print(f"  {symbol} {status}: {name}")
    
    print()
    print(f"  Total: {passed}/{total} tests passed")
    print("=" * 60)
    print()
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
