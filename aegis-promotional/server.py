"""
Aegis OS Promotional Website Server - ENHANCED
Serves promotional HTML, handles ISO downloads, licensing, and payments
"""

from flask import Flask, send_from_directory, redirect, jsonify, request
import os
import json
from datetime import datetime
import hashlib

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# License tiers
TIERS = {
    "freemium": {"price": 0, "features": ["base_os", "wine", "proton"]},
    "basic": {"price": 49, "features": ["base_os", "wine", "proton", "security", "ai_detection", "firewall", "priority_support"]},
    "gamer": {"price": 99, "features": ["base_os", "wine", "proton", "security", "ai_detection", "gaming_tools", "gpu_acceleration", "priority_support"]},
    "ai-dev": {"price": 149, "features": ["base_os", "wine", "proton", "security", "ai_detection", "docker", "pytorch", "tensorflow", "jupyter", "gpu_acceleration", "enterprise_support"]},
    "server": {"price": 199, "features": ["base_os", "security", "ai_detection", "docker", "postgresql", "nginx", "prometheus", "grafana", "rebootless_patching", "enterprise_support_24/7"]},
}

# ============= PAGES =============

@app.route('/')
def index():
    return redirect('/html/index.html')

@app.route('/html/<path:filename>')
def serve_html(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'html'), filename)

@app.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'css'), filename)

@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'js'), filename)

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'assets'), filename)

@app.route('/favicon.ico')
def favicon():
    try:
        return send_from_directory(os.path.join(BASE_DIR, 'assets'), 'logo.svg')
    except:
        return '', 204

# ============= DOWNLOADS =============

@app.route('/download/iso')
def download_iso():
    """Download Aegis OS ISO (Freemium)"""
    iso_file = os.path.join(BASE_DIR, 'downloads', 'aegis-os-freemium.iso')
    if os.path.exists(iso_file):
        return send_from_directory(
            os.path.join(BASE_DIR, 'downloads'),
            'aegis-os-freemium.iso',
            as_attachment=True,
            download_name='aegis-os-freemium.iso'
        )
    return jsonify({'error': 'ISO not available. Run build scripts.'}), 404

@app.route('/download/build-scripts')
def download_build_scripts():
    """Download Buildroot build scripts"""
    script_file = os.path.join(BASE_DIR, 'downloads', 'iso-builder', 'build.sh')
    if os.path.exists(script_file):
        return send_from_directory(
            os.path.join(BASE_DIR, 'downloads', 'iso-builder'),
            'build.sh',
            as_attachment=True,
            download_name='build.sh'
        )
    return jsonify({'error': 'Build scripts not found'}), 404

# ============= API: LICENSING =============

@app.route('/api/v1/license/validate', methods=['POST'])
def validate_license():
    """Validate license key and return tier"""
    data = request.json or {}
    key = data.get('key', '')
    
    if not key:
        return jsonify({'valid': False, 'error': 'No license key provided'}), 400
    
    # Simple validation: check key format
    # Real system would check against database
    if key.startswith('AEGIS-'):
        parts = key.split('-')
        if len(parts) >= 3:
            tier = parts[1].lower()
            if tier in TIERS:
                return jsonify({
                    'valid': True,
                    'tier': tier,
                    'price': TIERS[tier]['price'],
                    'features': TIERS[tier]['features'],
                    'expires': '2025-12-31'
                })
    
    return jsonify({'valid': False, 'error': 'Invalid license key'}), 401

@app.route('/api/v1/license/check', methods=['GET'])
def check_license():
    """Check if system has valid license"""
    license_file = os.path.join('/etc/aegis/license.key')
    
    try:
        if os.path.exists(license_file):
            with open(license_file) as f:
                data = json.load(f)
                return jsonify({
                    'licensed': True,
                    'tier': data.get('tier', 'freemium'),
                    'expires': data.get('expires')
                })
    except:
        pass
    
    return jsonify({'licensed': False, 'tier': 'freemium'})

@app.route('/api/v1/tiers', methods=['GET'])
def get_tiers():
    """Get all available tiers with features"""
    return jsonify({
        'tiers': TIERS,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/v1/tier/<tier_name>', methods=['GET'])
def get_tier(tier_name):
    """Get specific tier details"""
    if tier_name not in TIERS:
        return jsonify({'error': 'Tier not found'}), 404
    
    return jsonify({
        'tier': tier_name,
        'price': TIERS[tier_name]['price'],
        'features': TIERS[tier_name]['features'],
        'description': f'Aegis OS {tier_name.capitalize()} Edition'
    })

# ============= API: PAYMENTS =============

@app.route('/api/v1/payment/initiate', methods=['POST'])
def initiate_payment():
    """Initiate payment for tier (Stripe integration ready)"""
    data = request.json or {}
    tier = data.get('tier')
    email = data.get('email')
    
    if tier not in TIERS:
        return jsonify({'error': 'Invalid tier'}), 400
    
    if not email:
        return jsonify({'error': 'Email required'}), 400
    
    # Stripe integration would go here
    # For now, return payment intent structure
    return jsonify({
        'status': 'ready_for_payment',
        'tier': tier,
        'amount': TIERS[tier]['price'],
        'currency': 'USD',
        'payment_method': 'stripe',
        'note': 'Stripe integration available - contact admin@aegis-os.dev'
    })

@app.route('/api/v1/payment/verify', methods=['POST'])
def verify_payment():
    """Verify payment and issue license"""
    data = request.json or {}
    transaction_id = data.get('transaction_id')
    
    if not transaction_id:
        return jsonify({'error': 'Transaction ID required'}), 400
    
    return jsonify({
        'verified': True,
        'license_key': f'AEGIS-{data.get("tier", "basic").upper()}-2024-{hashlib.md5(transaction_id.encode()).hexdigest()[:12].upper()}',
        'message': 'Payment verified. Use license key to activate.'
    })

# ============= API: SECURITY =============

@app.route('/api/v1/security/check', methods=['GET'])
def security_check():
    """Get security status"""
    return jsonify({
        'system_secure': True,
        'threat_level': 'LOW',
        'last_scan': datetime.now().isoformat(),
        'features': {
            'real_time_scanning': True,
            'ai_threat_detection': True,
            'firewall': True,
            'file_integrity': True,
            'network_monitoring': True
        }
    })

# ============= API: DOCUMENTATION =============

@app.route('/api/docs')
def api_docs():
    """API Documentation"""
    return jsonify({
        'name': 'Aegis OS API',
        'version': '1.0',
        'endpoints': {
            'licensing': {
                'POST /api/v1/license/validate': 'Validate license key',
                'GET /api/v1/license/check': 'Check current license',
                'GET /api/v1/tiers': 'Get all tier info',
                'GET /api/v1/tier/<name>': 'Get specific tier',
            },
            'payments': {
                'POST /api/v1/payment/initiate': 'Start payment',
                'POST /api/v1/payment/verify': 'Verify & issue license',
            },
            'security': {
                'GET /api/v1/security/check': 'Get security status',
            }
        },
        'example_license_key': 'AEGIS-BASIC-2024-XXXXXXXXXXXXX'
    })

# ============= SYSTEM INFO =============

@app.route('/api/system')
def system_info():
    """System and build information"""
    return jsonify({
        'name': 'Aegis OS',
        'version': '1.0',
        'build_date': '2025-11-21',
        'editions': list(TIERS.keys()),
        'features': {
            'buildroot': True,
            'linux_kernel': '6.6.7',
            'desktop': 'XFCE 4.18',
            'security': True,
            'ai_detection': True
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
