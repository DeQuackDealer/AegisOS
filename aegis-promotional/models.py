import os
from datetime import datetime
from typing import Optional, Any
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.security import generate_password_hash, check_password_hash


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    email_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(255))
    stripe_customer_id = db.Column(db.String(255))
    
    licenses = db.relationship('License', backref='user', lazy='dynamic')
    
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'email_verified': self.email_verified,
            'license_count': self.licenses.count()
        }


class License(db.Model):
    __tablename__ = 'licenses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    license_key = db.Column(db.String(50), unique=True, nullable=False, index=True)
    edition = db.Column(db.String(50), nullable=False)
    license_type = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='active')
    stripe_payment_id = db.Column(db.String(255))
    stripe_session_id = db.Column(db.String(255))
    amount_paid = db.Column(db.Integer)
    currency = db.Column(db.String(10), default='usd')
    customer_email = db.Column(db.String(255))
    machine_id = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    activated_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)
    
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
    
    def to_dict(self):
        return {
            'id': self.id,
            'license_key': self.license_key,
            'edition': self.edition,
            'license_type': self.license_type,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'activated': self.activated_at is not None
        }


class StripeEvent(db.Model):
    __tablename__ = 'stripe_events'
    
    id = db.Column(db.Integer, primary_key=True)
    stripe_event_id = db.Column(db.String(255), unique=True, nullable=False, index=True)
    event_type = db.Column(db.String(100), nullable=False)
    processed = db.Column(db.Boolean, default=False)
    payload = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    error_message = db.Column(db.Text)


class EmailLog(db.Model):
    __tablename__ = 'email_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    license_id = db.Column(db.Integer, db.ForeignKey('licenses.id'), nullable=True)
    email_to = db.Column(db.String(255), nullable=False)
    email_type = db.Column(db.String(50), nullable=False)
    subject = db.Column(db.String(500))
    status = db.Column(db.String(20), default='pending')
    sendgrid_message_id = db.Column(db.String(255))
    sent_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    error_message = db.Column(db.Text)
    
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)


class AdminRole:
    """Admin role constants - defines what each role can do"""
    OWNER = 'owner'
    DEVELOPER = 'developer'
    TESTER = 'tester'
    DESIGNER = 'designer'
    YOUTUBER = 'youtuber'
    
    ALL_ROLES = [OWNER, DEVELOPER, TESTER, DESIGNER, YOUTUBER]
    
    # Roles that can access OS builds
    BUILD_ACCESS_ROLES = [OWNER, DEVELOPER, TESTER]
    
    # Roles that can manage other admins
    ADMIN_MANAGEMENT_ROLES = [OWNER]
    
    # Role display names
    DISPLAY_NAMES = {
        OWNER: 'Owner',
        DEVELOPER: 'Developer',
        TESTER: 'Tester',
        DESIGNER: 'Designer',
        YOUTUBER: 'YouTuber'
    }
    
    @classmethod
    def can_access_builds(cls, role: str) -> bool:
        return role in cls.BUILD_ACCESS_ROLES
    
    @classmethod
    def can_manage_admins(cls, role: str) -> bool:
        return role in cls.ADMIN_MANAGEMENT_ROLES
    
    @classmethod
    def get_display_name(cls, role: str) -> str:
        return cls.DISPLAY_NAMES.get(role, role.title())


class AdminUser(db.Model):
    """Admin users for the dashboard - stored in database for persistence"""
    __tablename__ = 'admin_users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255))
    role = db.Column(db.String(20), default='designer')
    can_create_admins = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(50))
    last_login = db.Column(db.DateTime)
    
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def can_access_builds(self) -> bool:
        """Check if this admin can access OS builds"""
        return AdminRole.can_access_builds(self.role)
    
    def can_manage_admins(self) -> bool:
        """Check if this admin can manage other admins"""
        return AdminRole.can_manage_admins(self.role)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'display_name': self.display_name,
            'email': self.email,
            'role': self.role,
            'role_display': AdminRole.get_display_name(self.role),
            'can_access_builds': self.can_access_builds(),
            'can_create_admins': self.can_create_admins,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }


class Giveaway(db.Model):
    """Giveaways with riddles for free licenses"""
    __tablename__ = 'giveaways'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    riddle = db.Column(db.Text, nullable=False)
    answer = db.Column(db.String(200), nullable=False)
    prize_edition = db.Column(db.String(50), nullable=False)
    prize_type = db.Column(db.String(20), default='lifetime')
    max_winners = db.Column(db.Integer, default=1)
    status = db.Column(db.String(20), default='active')
    created_by = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ends_at = db.Column(db.DateTime)
    
    entries = db.relationship('GiveawayEntry', backref='giveaway', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'riddle': self.riddle,
            'prize_edition': self.prize_edition,
            'prize_type': self.prize_type,
            'max_winners': self.max_winners,
            'status': self.status,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'ends_at': self.ends_at.isoformat() if self.ends_at else None,
            'entry_count': self.entries.count(),
            'winner_count': self.entries.filter_by(is_winner=True).count()
        }


class GiveawayEntry(db.Model):
    """Entries for giveaways - can be email-based or account-based"""
    __tablename__ = 'giveaway_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    giveaway_id = db.Column(db.Integer, db.ForeignKey('giveaways.id'), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100))
    answer_submitted = db.Column(db.String(200))
    is_correct = db.Column(db.Boolean, default=False)
    is_winner = db.Column(db.Boolean, default=False)
    license_key = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    notified_at = db.Column(db.DateTime)
    
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
    
    def to_dict(self):
        return {
            'id': self.id,
            'giveaway_id': self.giveaway_id,
            'email': self.email,
            'name': self.name,
            'is_correct': self.is_correct,
            'is_winner': self.is_winner,
            'license_key': self.license_key,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'notified_at': self.notified_at.isoformat() if self.notified_at else None
        }


class FreePeriodRedemption(db.Model):
    """Tracks which IPs have claimed their free edition during a free period"""
    __tablename__ = 'free_period_redemptions'
    
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), nullable=False, index=True)
    edition = db.Column(db.String(50), nullable=False)
    period_id = db.Column(db.String(50), nullable=False, index=True)
    hwid = db.Column(db.String(50), index=True)
    activation_count = db.Column(db.Integer, default=0)
    max_activations = db.Column(db.Integer, default=2)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('ip_address', 'period_id', name='uix_ip_period'),
    )
    
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
    
    def to_dict(self):
        return {
            'id': self.id,
            'ip_address': self.ip_address,
            'edition': self.edition,
            'period_id': self.period_id,
            'hwid': self.hwid,
            'activation_count': self.activation_count,
            'max_activations': self.max_activations,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class FreePeriodConfig(db.Model):
    """Persistent storage for free period settings"""
    __tablename__ = 'free_period_config'
    
    id = db.Column(db.Integer, primary_key=True)
    enabled = db.Column(db.Boolean, default=False)
    period_id = db.Column(db.String(100))
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    editions = db.Column(db.Text, default='[]')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        import json
        return {
            'id': self.id,
            'enabled': self.enabled,
            'period_id': self.period_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'editions': json.loads(self.editions) if self.editions else [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
