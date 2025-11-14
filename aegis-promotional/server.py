#!/usr/bin/env python3
"""
Simple web server for Aegis OS promotional website
Serves the promotional HTML files on port 5000
"""

from flask import Flask, send_from_directory, redirect
import os

app = Flask(__name__)

# Get the directory where this script is located
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

if __name__ == '__main__':
    print("🚀 Starting Aegis OS Promotional Website Server...")
    print("📄 Serving from:", BASE_DIR)
    print("🌐 Access at: http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
