"""
Aegis OS Python SDK
Official SDK for Aegis OS API integration
"""

from .client import AegisClient
from .models import License, User, Webhook, Backup

__version__ = '2.0.0'
__all__ = ['AegisClient', 'License', 'User', 'Webhook', 'Backup']
