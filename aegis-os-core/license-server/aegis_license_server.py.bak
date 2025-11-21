#!/usr/bin/env python3

"""
Aegis OS License Server
-----------------------
Flask-based license server that manages license activation and validation.
Issues JWT tokens for authenticated clients based on their tier and license status.
"""

from flask import Flask, request, jsonify
import jwt
import hashlib
from datetime import datetime, timedelta
import os

app = Flask(__name__)

SECRET_KEY = os.environ.get('SESSION_SECRET', 'aegis-default-secret-key-change-in-production')

MOCK_DB = {
    'AEGIS-BASIC-2024-ACTIVE': {
        'tier': 'basic',
        'expiry_date': '2026-12-31',
        'hardware_id': None,
        'status': 'ACTIVE'
    },
    'AEGIS-GAMER-2024-ACTIVE': {
        'tier': 'gamer',
        'expiry_date': '2026-06-30',
        'hardware_id': None,
        'status': 'ACTIVE'
    },
    'AEGIS-AI-2024-ACTIVE': {
        'tier': 'ai',
        'expiry_date': '2026-12-31',
        'hardware_id': None,
        'status': 'ACTIVE'
    },
    'AEGIS-SERVER-2024-ACTIVE': {
        'tier': 'server',
        'expiry_date': '2026-12-31',
        'hardware_id': None,
        'status': 'ACTIVE'
    },
    'AEGIS-BASIC-2024-EXPIRED': {
        'tier': 'basic',
        'expiry_date': '2023-01-01',
        'hardware_id': None,
        'status': 'EXPIRED'
    },
    'AEGIS-TEST-FREE': {
        'tier': 'freemium',
        'expiry_date': '2099-12-31',
        'hardware_id': None,
        'status': 'ACTIVE'
    }
}


def generate_jwt_token(license_key, tier, expiry_minutes=60):
    """
    Generate a signed JWT token for authenticated clients.
    
    Args:
        license_key: The validated license key
        tier: The tier level (freemium, basic, gamer, ai, server)
        expiry_minutes: Token expiration time in minutes (default 60)
    
    Returns:
        JWT token string
    """
    payload = {
        'license_key': license_key,
        'tier': tier,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(minutes=expiry_minutes)
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token


def validate_hardware_id(hardware_id):
    """
    Validate hardware ID format to prevent spoofing.
    
    Args:
        hardware_id: The hardware ID to validate
    
    Returns:
        bool: True if valid, False otherwise
    """
    if not hardware_id or len(hardware_id) < 10:
        return False
    
    if hardware_id.startswith('TEST-'):
        return True
    
    try:
        int(hardware_id, 16)
        return True
    except ValueError:
        return False


@app.route('/activate', methods=['POST'])
def activate():
    """
    Activate a license key by binding it to a hardware ID.
    
    Expected JSON payload:
        {
            "license_key": "AEGIS-XXXX-XXXX-XXXXX",
            "hardware_id": "unique-hardware-hash"
        }
    
    Returns:
        JSON response with activation status
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Invalid request', 'message': 'No JSON payload provided'}), 400
    
    license_key = data.get('license_key')
    hardware_id = data.get('hardware_id')
    
    if not license_key or not hardware_id:
        return jsonify({'error': 'Missing parameters', 'message': 'license_key and hardware_id required'}), 400
    
    if not validate_hardware_id(hardware_id):
        return jsonify({'error': 'Invalid hardware_id', 'message': 'Hardware ID format is invalid'}), 400
    
    if license_key not in MOCK_DB:
        return jsonify({'error': 'Invalid license', 'message': 'License key not found'}), 404
    
    license_data = MOCK_DB[license_key]
    
    if license_data['status'] == 'EXPIRED':
        return jsonify({'error': 'License expired', 'message': 'This license has expired'}), 403
    
    expiry_date = datetime.strptime(license_data['expiry_date'], '%Y-%m-%d')
    if expiry_date < datetime.utcnow():
        MOCK_DB[license_key]['status'] = 'EXPIRED'
        return jsonify({'error': 'License expired', 'message': 'This license has expired'}), 403
    
    if license_data['hardware_id'] is not None and license_data['hardware_id'] != hardware_id:
        return jsonify({
            'error': 'Hardware mismatch',
            'message': 'This license is already bound to another machine'
        }), 403
    
    MOCK_DB[license_key]['hardware_id'] = hardware_id
    
    token = generate_jwt_token(license_key, license_data['tier'])
    
    return jsonify({
        'success': True,
        'message': 'License activated successfully',
        'tier': license_data['tier'],
        'expiry_date': license_data['expiry_date'],
        'token': token
    }), 200


@app.route('/check_status', methods=['POST'])
def check_status():
    """
    Check the status of a license and issue a new JWT token if valid.
    
    Expected JSON payload:
        {
            "license_key": "AEGIS-XXXX-XXXX-XXXXX",
            "hardware_id": "unique-hardware-hash"
        }
    
    Returns:
        JSON response with license status and JWT token if valid
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Invalid request', 'message': 'No JSON payload provided'}), 400
    
    license_key = data.get('license_key')
    hardware_id = data.get('hardware_id')
    
    if not license_key or not hardware_id:
        return jsonify({'error': 'Missing parameters', 'message': 'license_key and hardware_id required'}), 400
    
    if not validate_hardware_id(hardware_id):
        return jsonify({'error': 'Invalid hardware_id', 'message': 'Hardware ID format is invalid'}), 400
    
    if license_key not in MOCK_DB:
        return jsonify({'error': 'Invalid license', 'message': 'License key not found'}), 404
    
    license_data = MOCK_DB[license_key]
    
    expiry_date = datetime.strptime(license_data['expiry_date'], '%Y-%m-%d')
    if expiry_date < datetime.utcnow():
        MOCK_DB[license_key]['status'] = 'EXPIRED'
        return jsonify({'error': 'License expired', 'message': 'This license has expired'}), 403
    
    if license_data['hardware_id'] is not None and license_data['hardware_id'] != hardware_id:
        return jsonify({
            'error': 'Hardware mismatch',
            'message': 'This license is bound to a different machine'
        }), 403
    
    token = generate_jwt_token(license_key, license_data['tier'])
    
    return jsonify({
        'success': True,
        'message': 'License is valid',
        'tier': license_data['tier'],
        'expiry_date': license_data['expiry_date'],
        'status': license_data['status'],
        'token': token
    }), 200


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Aegis License Server',
        'version': '1.0.0'
    }), 200


@app.route('/', methods=['GET'])
def index():
    """Root endpoint with API information"""
    return jsonify({
        'service': 'Aegis OS License Server',
        'version': '1.0.0',
        'endpoints': {
            '/activate': 'POST - Activate a license key',
            '/check_status': 'POST - Check license status and get JWT token',
            '/health': 'GET - Health check'
        }
    }), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
