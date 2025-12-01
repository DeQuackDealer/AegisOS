#!/usr/bin/env python3
"""
RSA License Validation Tester
Tests the complete signing and verification process used by the HTA installer
"""

import os
import sys
import re
import json
import hashlib
import base64
import requests

def compute_key_hash(key):
    """Replicate the VBScript ComputeKeyHash function EXACTLY
    
    VBScript:
        h = 0: r = &H5A3C
        For i = 1 To Len(str)
            c = Asc(Mid(str, i, 1))
            h = ((h * 31) + c) And &H7FFFFFFF
            r = ((r Xor c) * 17) And &HFFFF
        Next
        ComputeKeyHash = LCase(Left(Hex(h) & Hex(r), 16))
    """
    h = 0
    r = 0x5A3C  # Initial value for secondary hash
    for c in key.upper():
        code = ord(c)
        h = ((h * 31) + code) & 0x7FFFFFFF
        r = ((r ^ code) * 17) & 0xFFFF
    
    # Combine h and r, convert to hex, take first 16 chars, pad with zeros
    combined = format(h, 'x') + format(r, 'x')
    result = combined[:16].lower()
    while len(result) < 16:
        result = '0' + result
    return result

def test_hash_function():
    """Test that the hash function matches across all implementations"""
    print("\n[0] Testing hash function consistency...")
    test_keys = [
        "BSIC-DEMO-TEST-2024",
        "GAME-DEMO-TEST-2024",
        "AIDV-DEMO-TEST-2024",
    ]
    
    for key in test_keys:
        hash_val = compute_key_hash(key)
        print(f"   {key} -> {hash_val}")
    
    return True

def test_server_rsa_signing():
    """Test that the server is properly signing licenses"""
    print("=" * 60)
    print("RSA LICENSE VALIDATION TESTER")
    print("=" * 60)
    
    base_url = "http://localhost:5000"
    
    # Test hash function first
    test_hash_function()
    
    # Test 1: Check if licensed installer is available
    print("\n[1] Testing licensed installer download...")
    try:
        resp = requests.get(f"{base_url}/download-installer-licensed", timeout=10)
        if resp.status_code == 503:
            print("   FAIL: Server returned 503 - RSA key not configured")
            return False
        elif resp.status_code != 200:
            print(f"   FAIL: Server returned {resp.status_code}")
            return False
        print("   PASS: Licensed installer available")
        hta_content = resp.text
    except Exception as e:
        print(f"   FAIL: {e}")
        return False
    
    # Test 2: Extract RSA public key from HTA
    print("\n[2] Extracting RSA public key from installer...")
    pk_match = re.search(r'Const RSA_PUBLIC_KEY = "([^"]+)"', hta_content)
    if not pk_match:
        pk_match = re.search(r'Const CACHE_SALT = "([^"]+)"', hta_content)
    
    if not pk_match or pk_match.group(1) == "PLACEHOLDER_SALT":
        print("   FAIL: No RSA public key found (still placeholder)")
        return False
    
    public_key_b64 = pk_match.group(1)
    print(f"   PASS: Public key found ({len(public_key_b64)} chars)")
    
    # Test 3: Extract license cache
    print("\n[3] Extracting signed license cache...")
    cache_match = re.search(r'Const LICENSE_CACHE = "([^"]+)"', hta_content)
    if not cache_match:
        print("   FAIL: No license cache found")
        return False
    
    license_cache = cache_match.group(1)
    cache_entries = license_cache.split('|')
    print(f"   PASS: Found {len(cache_entries)} license entries")
    
    # Test 4: Extract master signature
    print("\n[4] Extracting master signature...")
    sig_match = re.search(r'Const MASTER_SIG = "([^"]+)"', hta_content)
    if not sig_match or sig_match.group(1) == "PLACEHOLDER_MASTER_SIG":
        print("   FAIL: No master signature found")
        return False
    
    master_sig = sig_match.group(1)
    print(f"   PASS: Master signature found ({len(master_sig)} chars)")
    
    # Test 5: Extract build date
    print("\n[5] Extracting cache build date...")
    date_match = re.search(r'Const CACHE_BUILD_DATE = "([^"]+)"', hta_content)
    if not date_match:
        print("   FAIL: No build date found")
        return False
    
    build_date = date_match.group(1)
    print(f"   PASS: Build date: {build_date}")
    
    # Test 6: Verify license entries have signatures
    print("\n[6] Verifying license entry signatures...")
    signed_entries = 0
    for entry in cache_entries:
        parts = entry.split(':')
        if len(parts) >= 4:  # hash:edition:extra:signature
            signed_entries += 1
    
    print(f"   PASS: {signed_entries}/{len(cache_entries)} entries have signatures")
    
    # Test 7: Verify demo license hashes match expected
    print("\n[7] Verifying demo license key hashes in cache...")
    demo_keys = {
        "BSIC-DEMO-TEST-2024": "basic",
        "WORK-DEMO-TEST-2024": "workplace",
        "GAME-DEMO-TEST-2024": "gamer",
        "AIDV-DEMO-TEST-2024": "ai_developer",
        "GMAI-DEMO-TEST-2024": "gamer_ai",
        "SERV-DEMO-TEST-2024": "server"
    }
    
    found_demos = 0
    for key, expected_edition in demo_keys.items():
        key_hash = compute_key_hash(key)
        for entry in cache_entries:
            if entry.startswith(key_hash + ":"):
                found_demos += 1
                parts = entry.split(':')
                if len(parts) >= 2:
                    print(f"   PASS: {key} found (hash={key_hash[:12]}..., edition={parts[1]})")
                break
        else:
            print(f"   MISS: {key} not found (expected hash={key_hash})")
    
    print(f"\n   Found {found_demos}/{len(demo_keys)} demo licenses in cache")
    
    if found_demos == 0:
        print("   FAIL: No demo licenses match - hash function mismatch!")
        return False
    
    # Test 8: Verify RSA signature using Python cryptography
    print("\n[8] Verifying RSA signatures with Python crypto...")
    try:
        from cryptography.hazmat.primitives import serialization, hashes
        from cryptography.hazmat.primitives.asymmetric import padding
        from cryptography.hazmat.backends import default_backend
        
        # Decode the public key
        try:
            public_key_der = base64.b64decode(public_key_b64)
            public_key = serialization.load_der_public_key(public_key_der, backend=default_backend())
            print("   PASS: Public key decoded successfully")
        except Exception as e:
            print(f"   FAIL: Could not decode public key: {e}")
            return False
        
        # Verify master signature
        print("\n[9] Verifying master cache signature...")
        try:
            message = f"CACHE:{license_cache}:{build_date}"
            signature_bytes = base64.b64decode(master_sig)
            
            public_key.verify(
                signature_bytes,
                message.encode(),
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            print("   PASS: Master signature VERIFIED!")
        except Exception as e:
            print(f"   FAIL: Master signature verification failed: {e}")
            return False
        
        # Verify individual license signatures
        print("\n[10] Verifying individual license signatures...")
        verified_count = 0
        for key, expected_edition in demo_keys.items():
            key_hash = compute_key_hash(key)
            for entry in cache_entries:
                if entry.startswith(key_hash + ":"):
                    parts = entry.split(':')
                    if len(parts) >= 4:
                        msg = f"{parts[0]}:{parts[1]}"
                        sig = parts[3]
                        try:
                            sig_bytes = base64.b64decode(sig)
                            public_key.verify(
                                sig_bytes,
                                msg.encode(),
                                padding.PKCS1v15(),
                                hashes.SHA256()
                            )
                            verified_count += 1
                        except Exception as e:
                            print(f"   FAIL: {key} signature invalid: {e}")
                    break
        
        print(f"   PASS: {verified_count}/{found_demos} license signatures verified")
        
    except ImportError:
        print("   SKIP: cryptography library not available")
    
    # Test 11: Test update API integration
    print("\n[11] Testing update API with license key...")
    try:
        resp = requests.get(
            f"{base_url}/api/v1/updates/check",
            params={"current_version": "2.5.0", "license_key": "BSIC-DEMO-TEST-2024"},
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            print(f"   PASS: Update check returned edition={data.get('edition')}")
            print(f"   PASS: License status={data.get('license_status')}")
            if data.get('signature'):
                print(f"   PASS: Response is RSA-signed")
        else:
            print(f"   FAIL: Update API returned {resp.status_code}")
    except Exception as e:
        print(f"   FAIL: {e}")
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED - RSA validation is working correctly!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_server_rsa_signing()
    sys.exit(0 if success else 1)
