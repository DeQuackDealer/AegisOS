#!/usr/bin/env python3
"""
Aegis OS License Signing Tool

Signs license files with RSA-2048 private key for offline verification.
The resulting license.json can be distributed to customers.
"""

import os
import sys
import json
import base64
import argparse
import secrets
import string
from pathlib import Path
from datetime import datetime, date

try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.backends import default_backend
except ImportError:
    print("Error: cryptography library not found")
    print("Install with: pip install cryptography")
    sys.exit(1)

EDITIONS = {
    "basic": {"prefix": "BSIC", "name": "Aegis OS Basic"},
    "workplace": {"prefix": "WORK", "name": "Aegis OS Workplace"},
    "gamer": {"prefix": "GAME", "name": "Aegis OS Gamer"},
    "aidev": {"prefix": "AIDV", "name": "Aegis OS AI Developer"},
    "gamer_ai": {"prefix": "GMAI", "name": "Aegis OS Gamer + AI"},
    "server": {"prefix": "SERV", "name": "Aegis OS Server"},
}


def generate_license_key(edition):
    """Generate a random license key with edition prefix"""
    if edition not in EDITIONS:
        raise ValueError(f"Unknown edition: {edition}")
    
    prefix = EDITIONS[edition]["prefix"]
    
    def random_segment():
        chars = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(chars) for _ in range(4))
    
    return f"{prefix}-{random_segment()}-{random_segment()}-{random_segment()}"


def load_private_key(key_path, password=None):
    """Load private key from PEM file"""
    with open(key_path, 'rb') as f:
        key_data = f.read()
    
    pwd = password.encode() if password else None
    
    private_key = serialization.load_pem_private_key(
        key_data,
        password=pwd,
        backend=default_backend()
    )
    
    return private_key


def create_license_data(edition, license_key, customer_email, expiry_date):
    """Create the license data structure"""
    issued_date = date.today().isoformat()
    
    if expiry_date and expiry_date.lower() == "lifetime":
        expiry_date = None
    
    return {
        "license_key": license_key,
        "edition": edition,
        "customer_email": customer_email or "",
        "issued_date": issued_date,
        "expiry_date": expiry_date
    }


def sign_license(private_key, license_data):
    """
    Sign license data with RSA private key.
    
    The signature is created from a JSON string with:
    - Sorted keys
    - No whitespace separators
    This ensures consistent verification across platforms.
    """
    signature_data = {
        "license_key": license_data["license_key"],
        "edition": license_data["edition"],
        "customer_email": license_data.get("customer_email", ""),
        "issued_date": license_data.get("issued_date", ""),
        "expiry_date": license_data.get("expiry_date")
    }
    
    data_to_sign = json.dumps(signature_data, sort_keys=True, separators=(',', ':'))
    
    signature = private_key.sign(
        data_to_sign.encode('utf-8'),
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    
    signature_b64 = base64.b64encode(signature).decode('ascii')
    
    return signature_b64


def save_license(license_data, signature, output_path):
    """Save the complete license file"""
    complete_license = {
        "license_key": license_data["license_key"],
        "edition": license_data["edition"],
        "customer_email": license_data["customer_email"],
        "issued_date": license_data["issued_date"],
        "expiry_date": license_data["expiry_date"],
        "signature": signature
    }
    
    with open(output_path, 'w') as f:
        json.dump(complete_license, f, indent=2)
    
    return complete_license


def main():
    parser = argparse.ArgumentParser(
        description="Sign Aegis OS license files with RSA-2048"
    )
    parser.add_argument(
        "--edition", "-e",
        required=True,
        choices=list(EDITIONS.keys()),
        help="Edition to license"
    )
    parser.add_argument(
        "--license-key", "-l",
        help="License key (auto-generated if not provided)"
    )
    parser.add_argument(
        "--email", "-m",
        default="",
        help="Customer email address"
    )
    parser.add_argument(
        "--expiry", "-x",
        default=None,
        help="Expiry date (YYYY-MM-DD) or 'lifetime' for no expiry"
    )
    parser.add_argument(
        "--private-key", "-k",
        required=True,
        help="Path to private key PEM file"
    )
    parser.add_argument(
        "--password", "-p",
        help="Password for encrypted private key"
    )
    parser.add_argument(
        "--output", "-o",
        default="license.json",
        help="Output license file path (default: license.json)"
    )
    parser.add_argument(
        "--batch", "-b",
        type=int,
        help="Generate multiple licenses (outputs to numbered files)"
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.private_key):
        print(f"Error: Private key not found: {args.private_key}")
        sys.exit(1)
    
    if args.expiry and args.expiry.lower() != "lifetime":
        try:
            datetime.strptime(args.expiry, "%Y-%m-%d")
        except ValueError:
            print(f"Error: Invalid date format: {args.expiry}")
            print("Use YYYY-MM-DD format or 'lifetime'")
            sys.exit(1)
    
    print(f"\nLoading private key: {args.private_key}")
    try:
        private_key = load_private_key(args.private_key, args.password)
    except Exception as e:
        print(f"Error loading private key: {e}")
        if "password" in str(e).lower():
            print("Hint: Use --password if the key is encrypted")
        sys.exit(1)
    
    batch_count = args.batch or 1
    
    for i in range(batch_count):
        license_key = args.license_key if args.license_key and batch_count == 1 else generate_license_key(args.edition)
        
        license_data = create_license_data(
            edition=args.edition,
            license_key=license_key,
            customer_email=args.email,
            expiry_date=args.expiry
        )
        
        signature = sign_license(private_key, license_data)
        
        if batch_count > 1:
            output_path = Path(args.output)
            output_file = output_path.parent / f"{output_path.stem}_{i+1:03d}{output_path.suffix}"
        else:
            output_file = args.output
        
        complete_license = save_license(license_data, signature, output_file)
        
        print(f"\n{'=' * 60}")
        print(f"LICENSE #{i+1} GENERATED SUCCESSFULLY")
        print("=" * 60)
        print(f"Edition:     {EDITIONS[args.edition]['name']}")
        print(f"License Key: {license_key}")
        print(f"Email:       {args.email or '(none)'}")
        print(f"Issued:      {license_data['issued_date']}")
        print(f"Expires:     {args.expiry or 'Lifetime'}")
        print(f"Output:      {output_file}")
        print("=" * 60)
    
    if batch_count == 1:
        print("\n📋 CUSTOMER INSTRUCTIONS:")
        print(f"""
    1. Copy {args.output} to one of these locations:
       • ~/.aegis/license.json (Linux/Mac)
       • USB drive root as license.json
       
    2. Run the Aegis OS installer
    
    3. The installer will automatically detect and verify the license
""")
    else:
        print(f"\n✓ Generated {batch_count} license files")


if __name__ == "__main__":
    main()
