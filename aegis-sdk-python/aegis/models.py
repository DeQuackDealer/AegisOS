"""Data models for Aegis OS SDK"""

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class License:
    tier: str
    price: int
    features: List[str]
    expires: str
    valid: bool

@dataclass
class User:
    user_id: str
    email: str
    role: str
    created: str
    two_fa_enabled: bool

@dataclass
class Webhook:
    webhook_id: str
    url: str
    events: List[str]
    created: str
    active: bool
    failures: int

@dataclass
class Backup:
    backup_id: str
    schedule: str
    retention_days: int
    last_backup: Optional[str]
    next_backup: str
    created: str
