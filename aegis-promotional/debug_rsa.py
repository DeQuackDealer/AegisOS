#!/usr/bin/env python3
"""
RSA Verification Debugger - Simulates exactly what PowerShell 5 does
"""

import os
import sys
import re
import base64
import requests

def main():
    print("=" * 60)
    print("RSA VERIFICATION DEBUGGER")
    print("=" * 60)
    
    # Download installer
    print("\n[1] Downloading installer...")
    resp = requests.get("http://localhost:5000/download-installer-licensed", timeout=30)
    if resp.status_code != 200:
        print(f"   FAIL: {resp.status_code}")
        return
    
    hta = resp.text
    
    # Extract values
    salt_match = re.search(r'Const CACHE_SALT = "([^"]+)"', hta)
    cache_match = re.search(r'Const LICENSE_CACHE = "([^"]+)"', hta)
    date_match = re.search(r'Const CACHE_BUILD_DATE = "([^"]+)"', hta)
    sig_match = re.search(r'Const MASTER_SIG = "([^"]+)"', hta)
    
    if not all([salt_match, cache_match, date_match, sig_match]):
        print("   FAIL: Could not extract all values")
        return
    
    cache_salt_b64 = salt_match.group(1)
    license_cache = cache_match.group(1)
    build_date = date_match.group(1)
    master_sig_b64 = sig_match.group(1)
    
    print(f"   CACHE_SALT length: {len(cache_salt_b64)}")
    print(f"   LICENSE_CACHE length: {len(license_cache)}")
    print(f"   BUILD_DATE: {build_date}")
    print(f"   MASTER_SIG length: {len(master_sig_b64)}")
    
    # Decode the XML public key
    print("\n[2] Decoding public key XML...")
    try:
        xml_key = base64.b64decode(cache_salt_b64).decode('utf-8')
        print(f"   XML: {xml_key[:80]}...")
    except Exception as e:
        print(f"   FAIL: {e}")
        return
    
    # Extract modulus and exponent
    mod_match = re.search(r'<Modulus>([^<]+)</Modulus>', xml_key)
    exp_match = re.search(r'<Exponent>([^<]+)</Exponent>', xml_key)
    
    if not mod_match or not exp_match:
        print("   FAIL: Could not extract modulus/exponent")
        return
    
    modulus_b64 = mod_match.group(1)
    exponent_b64 = exp_match.group(1)
    
    print(f"   Modulus (base64): {modulus_b64[:40]}...")
    print(f"   Exponent (base64): {exponent_b64}")
    
    # Decode and analyze
    modulus_bytes = base64.b64decode(modulus_b64)
    exponent_bytes = base64.b64decode(exponent_b64)
    
    print(f"   Modulus bytes: {len(modulus_bytes)} ({len(modulus_bytes)*8} bits)")
    print(f"   Exponent bytes: {len(exponent_bytes)}")
    print(f"   Exponent hex: {exponent_bytes.hex()}")
    
    # The message that should be verified
    message = f"CACHE:{license_cache}:{build_date}"
    print(f"\n[3] Message to verify:")
    print(f"   Length: {len(message)} chars")
    print(f"   First 80 chars: {message[:80]}...")
    
    # Now verify using Python (which we know works)
    print("\n[4] Verifying with Python cryptography...")
    try:
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import padding
        from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
        from cryptography.hazmat.backends import default_backend
        
        modulus = int.from_bytes(modulus_bytes, byteorder='big')
        exponent = int.from_bytes(exponent_bytes, byteorder='big')
        
        public_numbers = RSAPublicNumbers(exponent, modulus)
        public_key = public_numbers.public_key(default_backend())
        
        sig_bytes = base64.b64decode(master_sig_b64)
        
        public_key.verify(
            sig_bytes,
            message.encode('utf-8'),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        print("   SUCCESS: Python verification passed!")
    except Exception as e:
        print(f"   FAIL: {e}")
        return
    
    # Generate a PowerShell test script
    print("\n[5] Generating PowerShell test script...")
    ps_script = f'''
$ErrorActionPreference = 'Continue'
Write-Host "=== PowerShell RSA Verification Test ==="

# Embedded values (exactly as in HTA)
$pubKeyXmlB64 = '{cache_salt_b64}'
$sigB64 = '{master_sig_b64}'
$message = 'CACHE:{license_cache}:{build_date}'

Write-Host "Message length: $($message.Length)"
Write-Host ""

try {{
    # Decode XML public key
    $pubKeyXml = [System.Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($pubKeyXmlB64))
    Write-Host "Public key XML decoded successfully"
    Write-Host "XML preview: $($pubKeyXml.Substring(0, [Math]::Min(80, $pubKeyXml.Length)))..."
    
    # Decode signature
    $sig = [Convert]::FromBase64String($sigB64)
    Write-Host "Signature decoded: $($sig.Length) bytes"
    
    # Get message bytes
    $msgBytes = [System.Text.Encoding]::UTF8.GetBytes($message)
    Write-Host "Message bytes: $($msgBytes.Length)"
    
    # Create RSA and import key
    $rsa = New-Object System.Security.Cryptography.RSACryptoServiceProvider
    $rsa.FromXmlString($pubKeyXml)
    Write-Host "RSA key imported successfully"
    Write-Host "Key size: $($rsa.KeySize) bits"
    
    # Try verification with VerifyData
    Write-Host ""
    Write-Host "Attempting VerifyData..."
    $result = $rsa.VerifyData($msgBytes, [System.Security.Cryptography.CryptoConfig]::MapNameToOID('SHA256'), $sig)
    Write-Host "VerifyData result: $result"
    
    if (-not $result) {{
        # Try with hash
        Write-Host ""
        Write-Host "Attempting VerifyHash..."
        $sha256 = [System.Security.Cryptography.SHA256]::Create()
        $hashBytes = $sha256.ComputeHash($msgBytes)
        Write-Host "Hash computed: $($hashBytes.Length) bytes"
        $hashHex = [BitConverter]::ToString($hashBytes) -replace '-',''
        Write-Host "Hash (hex): $hashHex"
        
        # VerifyHash expects the OID
        $result2 = $rsa.VerifyHash($hashBytes, [System.Security.Cryptography.CryptoConfig]::MapNameToOID('SHA256'), $sig)
        Write-Host "VerifyHash result: $result2"
    }}
    
    $rsa.Dispose()
}} catch {{
    Write-Host "ERROR: $($_.Exception.Message)"
    Write-Host "Stack: $($_.Exception.StackTrace)"
}}
'''
    
    with open('/tmp/test_rsa.ps1', 'w') as f:
        f.write(ps_script)
    
    print("   Saved to /tmp/test_rsa.ps1")
    print("\n   To test on Windows, copy this script and run it in PowerShell.")
    
    # Also check what the issue might be
    print("\n[6] Analysis:")
    print(f"   - Exponent value: {int.from_bytes(exponent_bytes, 'big')}")
    print(f"   - Expected exponent for RSA: 65537 (0x10001)")
    
    if exponent_bytes == b'\x01\x00\x01':
        print("   - Exponent encoding: CORRECT (big-endian)")
    else:
        print(f"   - Exponent bytes: {exponent_bytes.hex()} - might need adjustment")

if __name__ == "__main__":
    main()
