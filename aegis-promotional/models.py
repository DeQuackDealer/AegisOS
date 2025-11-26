import os
from datetime import datetime
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
