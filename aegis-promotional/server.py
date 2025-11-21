"""
Aegis OS Promotional Website Server
Serves the promotional HTML files on port 5000
Handles ISO downloads and builds
"""

from flask import Flask, send_from_directory, redirect, jsonify
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
def index():
  """Redirect to the main page"""
  return redirect('/html/index.html')

@app.route('/html/<path:filename>')
def serve_html(filename):
  """Serve HTML files"""
  return send_from_directory(os.path.join(BASE_DIR, 'html'), filename)

@app.route('/css/<path:filename>')
def serve_css(filename):
  """Serve CSS files"""
  return send_from_directory(os.path.join(BASE_DIR, 'css'), filename)

@app.route('/js/<path:filename>')
def serve_js(filename):
  """Serve JavaScript files"""
  return send_from_directory(os.path.join(BASE_DIR, 'js'), filename)

@app.route('/assets/<path:filename>')
def serve_assets(filename):
  """Serve asset files"""
  return send_from_directory(os.path.join(BASE_DIR, 'assets'), filename)

@app.route('/favicon.ico')
def favicon():
  """Serve favicon"""
  try:
    return send_from_directory(os.path.join(BASE_DIR, 'assets'), 'logo.svg')
  except:
    return '', 204

@app.route('/download/iso')
def download_iso():
  """Download the Aegis OS ISO file"""
  iso_file = os.path.join(BASE_DIR, 'downloads', 'aegis-os-freemium.iso')
  
  if os.path.exists(iso_file):
    return send_from_directory(
      os.path.join(BASE_DIR, 'downloads'),
      'aegis-os-freemium.iso',
      as_attachment=True,
      download_name='aegis-os-freemium.iso'
    )
  else:
    return jsonify({'error': 'ISO file not available yet. Use build scripts to create it.'}), 404

@app.route('/download/build-scripts')
def download_build_scripts():
  """Download the Buildroot build scripts"""
  script_file = os.path.join(BASE_DIR, 'downloads', 'iso-builder', 'build.sh')
  
  if os.path.exists(script_file):
    return send_from_directory(
      os.path.join(BASE_DIR, 'downloads', 'iso-builder'),
      'build.sh',
      as_attachment=True,
      download_name='build.sh'
    )
  else:
    return jsonify({'error': 'Build scripts not found'}), 404

@app.route('/api/status')
def api_status():
  """Get system status"""
  iso_exists = os.path.exists(os.path.join(BASE_DIR, 'downloads', 'aegis-os-freemium.iso'))
  return jsonify({
    'website': 'online',
    'iso_available': iso_exists,
    'build_scripts': 'available'
  })

if __name__ == '__main__':
  print("🚀 Starting Aegis OS Promotional Website Server...")
  print("📄 Serving from:", BASE_DIR)
  print("🌐 Access at: http://0.0.0.0:5000")
  app.run(host='0.0.0.0', port=5000, debug=False)
