"""
Simple web server for Aegis OS promotional website
Serves the promotional HTML files on port 5000
"""

from flask import Flask, send_from_directory, redirect
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

@app.route('/api/build', methods=['POST'])
def trigger_build():
  """Trigger the actual Aegis OS build process"""
  import subprocess
  import threading
  
  def run_build():
    try:
      result = subprocess.run([
        'python3', '../aegis-os-freemium/build-replit.py'
      ], capture_output=True, text=True, cwd=BASE_DIR)
      
      if result.returncode == 0:
        print("✅ Aegis OS build completed successfully!")
      else:
        print(f"❌ Build failed: {result.stderr}")
    except Exception as e:
      print(f"❌ Build error: {e}")
  
  build_thread = threading.Thread(target=run_build)
  build_thread.daemon = True
  build_thread.start()
  
  return {'success': True, 'message': 'Build started'}

@app.route('/api/download/<filename>')
def download_file(filename):
  """Download a built file from the output directory"""
  output_dir = os.path.join(BASE_DIR, '../aegis-os-freemium/output')
  
  allowed_files = [
    'aegis-os-freemium-rootfs.tar.gz',
    'aegis_lkm.c', 
    'Makefile',
    'create-bootable-usb.sh',
    'checksums.sha256',
    'iso-metadata.json'
  ]
  
  if filename not in allowed_files:
    return {'error': 'File not allowed'}, 403
  
  try:
    return send_from_directory(output_dir, filename, as_attachment=True)
  except FileNotFoundError:
    return {'error': 'File not found. Run build first.'}, 404

if __name__ == '__main__':
  print("🚀 Starting Aegis OS Promotional Website Server...")
  print("📄 Serving from:", BASE_DIR)
  print("🌐 Access at: http://0.0.0.0:5000")
  app.run(host='0.0.0.0', port=5000, debug=False)
