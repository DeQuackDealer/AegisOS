"""Aegis OS API Client"""

import requests
from typing import Dict, List, Optional

class AegisClient:
    """Main client for Aegis OS API"""
    
    def __init__(self, base_url: str = 'https://api.aegis-os.dev', api_key: str = '', user_id: str = ''):
        self.base_url = base_url
        self.api_key = api_key
        self.user_id = user_id
        self.headers = {
            'Content-Type': 'application/json',
            'X-API-Key': api_key,
            'X-User-ID': user_id
        }
    
    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make HTTP request"""
        url: str = f"{self.base_url}{endpoint}"
        response = requests.request(method, url, json=data, headers=self.headers)
        return response.json()
    
    # ===== LICENSING =====
    
    def validate_license(self, key: str) -> Dict:
        """Validate license key"""
        return self._request('POST', '/api/v1/license/validate', {'key': key})
    
    def get_license_status(self) -> Dict:
        """Get current license status"""
        return self._request('GET', '/api/v1/license/check')
    
    def get_tiers(self) -> Dict:
        """Get all available tiers"""
        return self._request('GET', '/api/v1/tiers')
    
    def get_tier(self, tier_name: str) -> Dict:
        """Get specific tier details"""
        return self._request('GET', f'/api/v1/tier/{tier_name}')
    
    # ===== PAYMENTS =====
    
    def initiate_payment(self, tier: str, email: str) -> Dict:
        """Start payment for tier"""
        return self._request('POST', '/api/v1/payment/initiate', {
            'tier': tier,
            'email': email
        })
    
    def verify_payment(self, transaction_id: str, tier: str) -> Dict:
        """Verify payment and get license"""
        return self._request('POST', '/api/v1/payment/verify', {
            'transaction_id': transaction_id,
            'tier': tier
        })
    
    # ===== USER MANAGEMENT =====
    
    def register(self, email: str, password: str) -> Dict:
        """Register new user"""
        return self._request('POST', '/api/v1/auth/register', {
            'email': email,
            'password': password
        })
    
    def login(self, email: str, password: str) -> Dict:
        """Login user"""
        return self._request('POST', '/api/v1/auth/login', {
            'email': email,
            'password': password
        })
    
    def get_profile(self) -> Dict:
        """Get user profile"""
        return self._request('GET', '/api/v1/user/profile')
    
    def enable_2fa(self) -> Dict:
        """Enable two-factor authentication"""
        return self._request('POST', '/api/v1/user/2fa/enable')
    
    # ===== SECURITY =====
    
    def check_security(self) -> Dict:
        """Check system security status"""
        return self._request('GET', '/api/v1/security/check')
    
    # ===== WEBHOOKS =====
    
    def register_webhook(self, url: str, events: List[str]) -> Dict:
        """Register webhook"""
        return self._request('POST', '/api/v1/webhooks/register', {
            'url': url,
            'events': events
        })
    
    def list_webhooks(self) -> Dict:
        """List all webhooks"""
        return self._request('GET', '/api/v1/webhooks')
    
    def delete_webhook(self, webhook_id: str) -> Dict:
        """Delete webhook"""
        return self._request('DELETE', f'/api/v1/webhooks/{webhook_id}')
    
    # ===== ANALYTICS =====
    
    def get_analytics(self) -> Dict:
        """Get analytics dashboard"""
        return self._request('GET', '/api/v1/analytics/dashboard')
    
    def get_audit_log(self, limit: int = 100) -> Dict:
        """Get audit log"""
        return self._request('GET', f'/api/v1/analytics/audit?limit={limit}')
    
    # ===== BACKUP =====
    
    def schedule_backup(self, schedule: str, retention_days: int = 30) -> Dict:
        """Schedule automated backups"""
        return self._request('POST', '/api/v1/backup/schedule', {
            'schedule': schedule,
            'retention_days': retention_days
        })
    
    def list_backups(self) -> Dict:
        """List available backups"""
        return self._request('GET', '/api/v1/backup/list')
    
    # ===== MARKETPLACE =====
    
    def list_apps(self) -> Dict:
        """List marketplace apps"""
        return self._request('GET', '/api/v1/marketplace/apps')
    
    def install_app(self, app_id: str) -> Dict:
        """Install app from marketplace"""
        return self._request('POST', f'/api/v1/marketplace/app/{app_id}/install')
    
    # ===== SYSTEM =====
    
    def get_system_status(self) -> Dict:
        """Get system status"""
        return self._request('GET', '/api/v1/system/status')
    
    def get_system_health(self) -> Dict:
        """Get system health"""
        return self._request('GET', '/api/v1/system/health')
    
    def get_rate_limit(self) -> Dict:
        """Get rate limit info"""
        return self._request('GET', '/api/v1/rate-limit/status')
