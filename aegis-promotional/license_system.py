"""
Aegis OS License Management System
Generates and validates licenses for different OS editions
"""

import hashlib
import hmac
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

class AegisLicenseSystem:
    """Manages license generation, validation, and feature access"""

    def __init__(self, secret_key: str):
        self.secret_key = secret_key

    def generate_license_key(self, tier: str, license_type: str, email: str, 
                            stripe_session_id: Optional[str] = None) -> Dict:
        """
        Generate a unique license key for a customer

        Args:
            tier: Edition (basic, gamer, ai-dev, server)
            license_type: 'lifetime' or 'annual'
            email: Customer email
            stripe_session_id: Stripe checkout session ID for verification

        Returns:
            Dictionary with license details
        """
        # Generate unique license ID (remove hyphens for key generation)
        license_id = str(uuid.uuid4()).replace('-', '')

        # Create license metadata
        metadata = {
            'license_id': license_id,
            'tier': tier,
            'type': license_type,
            'email': email,
            'issued_at': datetime.utcnow().isoformat(),
            'stripe_session_id': stripe_session_id
        }

        # Add expiration for annual licenses
        if license_type == 'annual':
            expires_at = datetime.utcnow() + timedelta(days=365)
            metadata['expires_at'] = expires_at.isoformat()
        else:
            metadata['expires_at'] = ''  # Lifetime licenses don't expire

        # Generate signature for tamper protection
        signature = self._generate_signature(metadata)

        # Create the license key (format: AEGIS-TIER-XXXXX-XXXXX-XXXXX)
        # Use specific tier codes to avoid issues with hyphens
        tier_codes = {
            'basic': 'BAS',
            'gamer': 'GAM', 
            'workplace': 'WOR',
            'ai-dev': 'AID',
            'server': 'SER',
            'gamer-ai': 'GAI'
        }
        tier_code = tier_codes.get(tier, tier.upper()[:3].replace('-', ''))
        
        key_parts = [
            'AEGIS',
            tier_code,
            license_id[:5].upper(),
            license_id[5:10].upper(),
            signature[:5].upper()
        ]

        license_key = '-'.join(key_parts)

        return {
            'license_key': license_key,
            'license_id': license_id,
            'metadata': metadata,
            'signature': signature
        }

    def validate_license(self, license_key: str, 
                        stored_metadata: Optional[Dict] = None) -> Tuple[bool, Dict]:
        """
        Validate a license key and return feature access

        Args:
            license_key: The license key to validate
            stored_metadata: Optional metadata stored with the license

        Returns:
            Tuple of (is_valid, feature_dict)
        """
        try:
            # Parse license key
            parts = license_key.split('-')
            if len(parts) != 5 or parts[0] != 'AEGIS':
                return False, {'tier': 'freemium', 'reason': 'Invalid license format'}

            # Extract tier from key
            tier_code = parts[1].lower()
            tier_map = {
                'bas': 'basic', 
                'gam': 'gamer', 
                'wor': 'workplace', 
                'aid': 'ai-dev', 
                'ser': 'server',
                'gai': 'gamer-ai'
            }
            tier = tier_map.get(tier_code, 'freemium')

            # If we have stored metadata, validate it
            if stored_metadata:
                # Check expiration for annual licenses
                if stored_metadata.get('type') == 'annual':
                    expires_at = stored_metadata.get('expires_at')
                    if expires_at:
                        expiry = datetime.fromisoformat(expires_at)
                        if datetime.utcnow() > expiry:
                            return False, {
                                'tier': 'freemium', 
                                'reason': 'License expired',
                                'expired_at': expires_at
                            }

                # Verify signature if available
                if 'signature' in stored_metadata:
                    expected_sig = self._generate_signature(stored_metadata)
                    if not hmac.compare_digest(stored_metadata['signature'], expected_sig):
                        return False, {'tier': 'freemium', 'reason': 'Invalid signature'}

            # Return features for the tier
            features = self._get_tier_features(tier)
            features['license_valid'] = True
            features['tier'] = tier
            features['license_type'] = stored_metadata.get('type', 'unknown') if stored_metadata else 'unknown'

            return True, features

        except Exception as e:
            return False, {'tier': 'freemium', 'reason': str(e)}

    def _generate_signature(self, data: Dict) -> str:
        """Generate HMAC signature for license data"""
        # Create deterministic string from data (exclude signature field)
        data_copy = {k: v for k, v in data.items() if k != 'signature'}
        data_str = json.dumps(data_copy, sort_keys=True)

        # Generate HMAC
        signature = hmac.new(
            self.secret_key.encode(),
            data_str.encode(),
            hashlib.sha256
        ).hexdigest()

        return signature

    def _get_tier_features(self, tier: str) -> Dict:
        """Get feature set for a given tier"""
        features = {
            'freemium': {
                'drivers': ['nouveau'],
                'desktop': 'XFCE 4.18',
                'wine': True,
                'proton': False,
                'security': 'basic',
                'gaming': False,
                'ai_tools': False,
                'enterprise': False,
                'max_memory': '4GB',
                'max_cores': 2,
                'support': 'community'
            },
            'basic': {
                'drivers': ['nouveau', 'basic_nvidia'],
                'desktop': 'XFCE 4.18',
                'wine': True,
                'proton': True,
                'security': 'enhanced',
                'gaming': False,
                'ai_tools': False,
                'enterprise': False,
                'max_memory': '16GB',
                'max_cores': 8,
                'support': 'email',
                'features': [
                    'encrypted_storage',
                    'secure_dns',
                    'vpn_client',
                    'password_manager',
                    'anti_ransomware'
                ]
            },
            'gamer': {
                'drivers': ['nvidia', 'amd', 'intel'],
                'desktop': 'XFCE 4.18 Gaming',
                'wine': True,
                'proton': True,
                'security': 'enhanced',
                'gaming': True,
                'ai_tools': False,
                'enterprise': False,
                'max_memory': '32GB',
                'max_cores': 16,
                'support': 'priority',
                'features': [
                    'gaming_mode',
                    'ray_tracing',
                    'dlss3',
                    'fsr3',
                    '8k_upscaling',
                    'rgb_ecosystem',
                    '3ms_latency',
                    'game_optimizer'
                ]
            },
            'workplace': {
                'drivers': ['nouveau', 'nvidia-basic', 'amd-basic'],
                'desktop': 'XFCE 4.18 Business',
                'wine': True,
                'proton': True,
                'security': 'enterprise',
                'gaming': False,
                'ai_tools': False,
                'enterprise': True,
                'max_memory': '32GB',
                'max_cores': 16,
                'support': 'business',
                'features': [
                    'active_directory',
                    'sso_support',
                    'remote_desktop',
                    'team_collaboration',
                    'office_365_compatibility',
                    'meeting_scheduler',
                    'expense_tracker',
                    'business_vpn'
                ]
            },
            'ai-dev': {
                'drivers': ['nvidia-cuda', 'rocm', 'intel-oneapi'],
                'desktop': 'XFCE 4.18 Developer',
                'wine': True,
                'proton': True,
                'security': 'enhanced',
                'gaming': False,
                'ai_tools': True,
                'enterprise': False,
                'max_memory': '64GB',
                'max_cores': 32,
                'support': '24/7',
                'features': [
                    'cuda_12_3',
                    'rocm',
                    'intel_oneapi',
                    'pytorch',
                    'tensorflow',
                    'jupyter_lab',
                    'ml_libraries',
                    'triton_server',
                    'langchain',
                    'vector_dbs'
                ]
            },
            'gamer-ai': {
                'drivers': ['nvidia-latest', 'amd-latest', 'intel', 'cuda', 'rocm'],
                'desktop': 'XFCE 4.18 Ultimate',
                'wine': True,
                'proton': True,
                'security': 'enhanced',
                'gaming': True,
                'ai_tools': True,
                'enterprise': False,
                'max_memory': '128GB',
                'max_cores': 64,
                'support': '24/7_priority',
                'features': [
                    'gaming_mode',
                    'ray_tracing',
                    'dlss3',
                    'fsr3',
                    '8k_upscaling',
                    'rgb_ecosystem',
                    '1ms_latency',
                    'game_optimizer',
                    'cuda_12_3',
                    'pytorch',
                    'tensorflow',
                    'ml_gaming_optimization',
                    'ai_upscaling'
                ]
            },
            'server': {
                'drivers': ['all'],
                'desktop': 'headless',
                'wine': False,
                'proton': False,
                'security': 'enterprise',
                'gaming': False,
                'ai_tools': True,
                'enterprise': True,
                'max_memory': 'unlimited',
                'max_cores': 'unlimited',
                'support': '24/7_sla',
                'features': [
                    'kubernetes',
                    'docker_swarm',
                    'high_availability',
                    'auto_scaling',
                    'disaster_recovery',
                    'zero_trust',
                    'multi_region',
                    '100k_rps'
                ]
            }
        }

        return features.get(tier, features['freemium'])

# License validation API for boot-time checks
def validate_license_on_boot(license_key: str, hardware_id: Optional[str] = None) -> Dict:
    """
    Validate license during OS boot

    Args:
        license_key: The license key entered by user
        hardware_id: Optional hardware fingerprint for binding

    Returns:
        Dictionary with validation result and features to enable
    """
    # This would connect to the Aegis license server
    # For now, using local validation
    license_system = AegisLicenseSystem(secret_key='your-secret-key-here')

    # Try to load cached license metadata
    metadata = None
    try:
        with open('/etc/aegis/license.json', 'r') as f:
            stored_data = json.load(f)
            if stored_data.get('license_key') == license_key:
                metadata = stored_data.get('metadata')
    except:
        pass

    # Validate the license
    is_valid, features = license_system.validate_license(license_key, metadata)

    # Log the validation attempt
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'license_key': license_key[:10] + '...',  # Partial key for privacy
        'hardware_id': hardware_id,
        'valid': is_valid,
        'tier': features.get('tier', 'freemium')
    }

    try:
        with open('/var/log/aegis_license.log', 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    except:
        pass

    return features