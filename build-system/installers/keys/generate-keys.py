#!/usr/bin/env python3
"""
Aegis OS RSA Key Pair Generator

Generates RSA-2048 key pair for license signing and verification.
The private key is used to sign licenses (keep secure!).
The public key is embedded in installers for verification.
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

try:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.backends import default_backend
except ImportError:
    print("Error: cryptography library not found")
    print("Install with: pip install cryptography")
    sys.exit(1)


def generate_key_pair(key_size=2048):
    """Generate RSA key pair"""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
        backend=default_backend()
    )
    return private_key


def save_private_key(private_key, filename, password=None):
    """Save private key to file"""
    if password:
        encryption = serialization.BestAvailableEncryption(password.encode())
    else:
        encryption = serialization.NoEncryption()
    
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption
    )
    
    with open(filename, 'wb') as f:
        f.write(pem)
    
    os.chmod(filename, 0o600)
    return pem


def save_public_key(private_key, filename):
    """Save public key to file"""
    public_key = private_key.public_key()
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    with open(filename, 'wb') as f:
        f.write(pem)
    
    return pem


def main():
    parser = argparse.ArgumentParser(
        description="Generate RSA-2048 key pair for Aegis OS license signing"
    )
    parser.add_argument(
        "--output-dir", "-o",
        default=".",
        help="Directory to save keys (default: current directory)"
    )
    parser.add_argument(
        "--private-key", "-p",
        default="aegis-private.pem",
        help="Private key filename (default: aegis-private.pem)"
    )
    parser.add_argument(
        "--public-key", "-u",
        default="aegis-public.pem",
        help="Public key filename (default: aegis-public.pem)"
    )
    parser.add_argument(
        "--password",
        help="Password to encrypt private key (optional but recommended)"
    )
    parser.add_argument(
        "--key-size", "-k",
        type=int,
        default=2048,
        choices=[2048, 4096],
        help="RSA key size in bits (default: 2048)"
    )
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Overwrite existing keys without prompting"
    )
    
    args = parser.parse_args()
    
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    private_path = output_dir / args.private_key
    public_path = output_dir / args.public_key
    
    if not args.force:
        if private_path.exists():
            response = input(f"Private key {private_path} exists. Overwrite? (y/N): ")
            if response.lower() != 'y':
                print("Aborted.")
                sys.exit(0)
        if public_path.exists():
            response = input(f"Public key {public_path} exists. Overwrite? (y/N): ")
            if response.lower() != 'y':
                print("Aborted.")
                sys.exit(0)
    
    print(f"\nGenerating RSA-{args.key_size} key pair...")
    print("=" * 60)
    
    private_key = generate_key_pair(args.key_size)
    
    private_pem = save_private_key(private_key, private_path, args.password)
    print(f"✓ Private key saved: {private_path}")
    
    public_pem = save_public_key(private_key, public_path)
    print(f"✓ Public key saved:  {public_path}")
    
    print("\n" + "=" * 60)
    print("PUBLIC KEY (embed this in installers):")
    print("=" * 60)
    print(public_pem.decode())
    
    print("=" * 60)
    print("CRITICAL SECURITY INSTRUCTIONS")
    print("=" * 60)
    print("""
⚠️  PRIVATE KEY SECURITY:
    
    1. NEVER commit the private key to version control
    2. NEVER store on networked computers
    3. NEVER share via email, chat, or cloud storage
    
    Recommended storage:
    • Hardware Security Module (HSM) for production
    • Air-gapped computer for signing operations
    • Encrypted USB drive in secure physical location
    • Multiple encrypted backups in separate locations

📋 NEXT STEPS:

    1. Move the private key to secure storage immediately:
       mv {private_path} /secure/offline/location/
    
    2. Update the public key in installers:
       - Edit: aegis-installer-licensed.py
       - Replace RSA_PUBLIC_KEY_PEM content with the public key above
    
    3. Sign licenses using:
       python sign-license.py --private-key /path/to/aegis-private.pem \\
           --edition basic --license-key "BSIC-XXXX-XXXX-XXXX" \\
           --email "customer@example.com"

🔑 Key Details:
    • Algorithm: RSA-{key_size}
    • Generated: {timestamp}
    • Private key protected: {protected}
""".format(
        private_path=private_path,
        key_size=args.key_size,
        timestamp=datetime.now().isoformat(),
        protected="Yes (password encrypted)" if args.password else "No (plaintext)"
    ))


if __name__ == "__main__":
    main()
