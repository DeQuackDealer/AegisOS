#!/usr/bin/env python3
"""
Apply legal disclaimers and remove admin links from all HTML files
"""

import os
from pathlib import Path
import re

# Comprehensive legal footer
LEGAL_FOOTER = '''    <footer class="footer" style="background:#1f2937;color:#f3f4f6;padding:3rem 2rem 2rem;margin-top:3rem;border-top:1px solid #333">
        <div style="max-width:1200px;margin:0 auto">
            <div style="text-align:center;margin-bottom:2rem">
                <p style="font-size:1.1rem;font-weight:600;color:#fbbf24;margin-bottom:1rem">⚠️ DEMO & PROMOTIONAL WEBSITE ⚠️</p>
                <p style="font-size:0.95rem;margin-bottom:0.5rem">© 2024 Aegis OS Demo. This is a promotional demonstration website.</p>
                <p style="font-size:0.9rem;color:#9ca3af;margin-bottom:0.5rem">All features described are conceptual and for demonstration purposes only.</p>
                <p style="font-size:0.9rem;color:#9ca3af;margin-bottom:0.5rem">Not affiliated with any actual Linux distribution or operating system.</p>
                <p style="font-size:0.85rem;color:#9ca3af;margin-bottom:1.5rem">All trademarks mentioned (Linux, NVIDIA, AMD, Intel, etc.) belong to their respective owners.</p>
            </div>
            <div style="text-align:center;padding-top:1.5rem;border-top:1px solid #4b5563">
                <nav style="margin-bottom:1rem">
                    <a href="/" style="color:#60a5fa;text-decoration:none;margin:0 10px">Home</a>
                    <span style="color:#4b5563">|</span>
                    <a href="/terms" style="color:#60a5fa;text-decoration:none;margin:0 10px">Terms of Service</a>
                    <span style="color:#4b5563">|</span>
                    <a href="/privacy" style="color:#60a5fa;text-decoration:none;margin:0 10px">Privacy Policy</a>
                    <span style="color:#4b5563">|</span>
                    <a href="/disclaimer" style="color:#60a5fa;text-decoration:none;margin:0 10px">Disclaimer</a>
                    <span style="color:#4b5563">|</span>
                    <a href="/contact" style="color:#60a5fa;text-decoration:none;margin:0 10px">Contact</a>
                    <span style="color:#4b5563">|</span>
                    <a href="/faq" style="color:#60a5fa;text-decoration:none;margin:0 10px">FAQ</a>
                </nav>
                <p style="font-size:0.85rem;color:#6b7280">This website is for demonstration purposes only. No actual software is distributed.</p>
            </div>
        </div>
    </footer>'''

def update_html_file(filepath):
    """Update a single HTML file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Remove Admin links from navigation bars (in nav sections)
    content = re.sub(r'<a[^>]*class="nav-link"[^>]*href="[^"]*admin[^"]*"[^>]*>Admin</a>', '', content, flags=re.IGNORECASE)
    content = re.sub(r'<a[^>]*href="[^"]*admin[^"]*"[^>]*class="nav-link"[^>]*>Admin</a>', '', content, flags=re.IGNORECASE)
    
    # Remove Admin links from footers with various patterns
    content = re.sub(r'<a[^>]*href="/admin"[^>]*>Admin</a>', '', content, flags=re.IGNORECASE)
    content = re.sub(r'<a[^>]*href="admin\.html"[^>]*>Admin</a>', '', content, flags=re.IGNORECASE)
    content = re.sub(r'\|\s*<a[^>]*>Admin</a>', '', content, flags=re.IGNORECASE)
    content = re.sub(r'<a[^>]*>Admin</a>\s*\|', '', content, flags=re.IGNORECASE)
    
    # Clean up any double pipes
    content = re.sub(r'\|\s*\|', '|', content)
    content = re.sub(r'\|\s*</p>', '</p>', content)
    
    # Replace footer
    # Find and replace the entire footer section
    footer_start = content.find('<footer')
    if footer_start != -1:
        footer_end = content.find('</footer>', footer_start) + len('</footer>')
        if footer_end > footer_start:
            content = content[:footer_start] + LEGAL_FOOTER + '\n' + content[footer_end:]
    else:
        # No footer found, add before </body>
        body_end = content.find('</body>')
        if body_end != -1:
            content = content[:body_end] + LEGAL_FOOTER + '\n    ' + content[body_end:]
    
    # Special handling for index.html
    if 'index.html' in str(filepath):
        # Add demo notice after hero section
        hero_end = content.find('</div>', content.find('class="hero'))
        if hero_end != -1:
            hero_end = content.find('</div>', hero_end + 1)  # Find second closing div
            if hero_end != -1:
                demo_notice = '''
    <div style="background:linear-gradient(135deg,#fbbf24,#f59e0b);color:#1f2937;padding:1rem 2rem;text-align:center;font-weight:600;margin-bottom:2rem">
        <p style="font-size:1.1rem;margin:0">🎯 Demo & Promotional Website 🎯</p>
        <p style="font-size:0.9rem;margin:0.5rem 0 0 0;font-weight:500">All features shown are for demonstration purposes only</p>
    </div>'''
                content = content[:hero_end + 6] + demo_notice + content[hero_end + 6:]
    
    # Special handling for admin.html
    if 'admin.html' in str(filepath):
        # Add warning banner
        body_start = content.find('<body')
        body_end = content.find('>', body_start) + 1
        if body_start != -1:
            warning = '''
    <div style="background:#ef4444;color:#fff;padding:1rem;text-align:center;font-weight:600;position:fixed;top:0;left:0;right:0;z-index:10000">
        ⚠️ DEMO ADMIN PANEL - FOR DEMONSTRATION PURPOSES ONLY ⚠️
    </div>'''
            content = content[:body_end] + warning + content[body_end:]
        
        # Add warning to login description if present
        if 'login-desc' in content:
            login_desc_end = content.find('</p>', content.find('login-desc'))
            if login_desc_end != -1:
                demo_warning = '\n            <p style="color:#ef4444;font-weight:600;margin-top:1rem">⚠️ Demo Panel - Not a real admin interface</p>'
                content = content[:login_desc_end + 4] + demo_warning + content[login_desc_end + 4:]
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    html_dir = Path('aegis-promotional/html')
    updated_files = []
    
    # Process all HTML files
    for html_file in sorted(html_dir.glob('*.html')):
        if html_file.name.endswith('.bak'):
            continue
        
        try:
            if update_html_file(html_file):
                updated_files.append(html_file.name)
                print(f"✓ Updated: {html_file.name}")
            else:
                print(f"  Checked: {html_file.name}")
        except Exception as e:
            print(f"✗ Error with {html_file.name}: {e}")
    
    return updated_files

if __name__ == "__main__":
    print("Applying legal disclaimers and removing admin links...")
    print("-" * 60)
    updated = main()
    print("-" * 60)
    print(f"Updated {len(updated)} files: {', '.join(updated) if updated else 'None'}")