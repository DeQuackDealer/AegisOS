#!/usr/bin/env python3
"""
Process all HTML files to remove admin links and add legal disclaimers
"""

import os
import re
from pathlib import Path

def process_html_file(filepath):
    """Process a single HTML file"""
    filename = os.path.basename(filepath)
    
    # Skip the files we just created
    if filename in ['terms.html', 'privacy.html', 'disclaimer.html']:
        print(f"  Skipping legal page: {filename}")
        return False
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Remove Admin links and sections
        # Pattern 1: Remove complete Admin section divs
        content = re.sub(r'<div class="footer-col">\s*<h4>Admin</h4>.*?</div>', '', content, flags=re.DOTALL)
        
        # Pattern 2: Remove individual admin links
        content = re.sub(r'<a[^>]*href="[^"]*admin[^"]*"[^>]*>.*?Admin.*?</a>', '', content, flags=re.DOTALL)
        content = re.sub(r'<a[^>]*href="/admin"[^>]*>[^<]*</a>', '', content, flags=re.DOTALL)
        
        # Pattern 3: Clean up License Management, API Status, Health Check links
        content = re.sub(r'<li>\s*<a[^>]*>License Management</a>\s*</li>', '', content, flags=re.DOTALL)
        content = re.sub(r'<li>\s*<a[^>]*>API Status</a>\s*</li>', '', content, flags=re.DOTALL)  
        content = re.sub(r'<li>\s*<a[^>]*>Health Check</a>\s*</li>', '', content, flags=re.DOTALL)
        
        # Pattern 4: Remove | Admin patterns
        content = re.sub(r'\|\s*<a[^>]*>Admin</a>', '', content)
        content = re.sub(r'<a[^>]*>Admin</a>\s*\|', '', content)
        
        # Clean up any double pipes or trailing pipes
        content = re.sub(r'\|\s*\|', '|', content)
        content = re.sub(r'\|\s*</p>', '</p>', content)
        
        # Replace entire footer with legal disclaimer footer
        legal_footer = '''    <!-- LEGAL DISCLAIMER FOOTER -->
    <footer class="footer" style="background:#1f2937;color:#f3f4f6;padding:3rem 2rem 2rem;margin-top:3rem;border-top:1px solid #333">
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
        
        # Replace existing footer
        content = re.sub(r'<footer[^>]*>.*?</footer>', legal_footer, content, flags=re.DOTALL)
        
        # If no footer exists, add before </body>
        if '</footer>' not in content and '<footer' not in content:
            content = re.sub(r'(</body>)', legal_footer + '\n\\1', content)
        
        # Special handling for index.html
        if filename == 'index.html':
            demo_notice = '''    <!-- DEMO NOTICE -->
    <div style="background:linear-gradient(135deg,#fbbf24,#f59e0b);color:#1f2937;padding:1rem 2rem;text-align:center;font-weight:600;margin-bottom:2rem">
        <p style="font-size:1.1rem;margin:0">🎯 Demo & Promotional Website 🎯</p>
        <p style="font-size:0.9rem;margin:0.5rem 0 0 0;font-weight:500">All features shown are for demonstration purposes only</p>
    </div>'''
            
            # Add after hero section
            hero_match = re.search(r'(<div[^>]*class="hero"[^>]*>.*?</div>\s*</div>)', content, re.DOTALL)
            if hero_match:
                hero_end = hero_match.end()
                content = content[:hero_end] + '\n\n' + demo_notice + '\n' + content[hero_end:]
        
        # Special handling for admin.html  
        elif filename == 'admin.html':
            admin_warning = '''    <!-- ADMIN WARNING -->
    <div style="background:#ef4444;color:#fff;padding:1rem;text-align:center;font-weight:600;position:fixed;top:0;left:0;right:0;z-index:10000">
        ⚠️ DEMO ADMIN PANEL - FOR DEMONSTRATION PURPOSES ONLY ⚠️
    </div>'''
            
            # Add after <body> tag
            content = re.sub(r'(<body[^>]*>)', r'\1\n' + admin_warning, content, count=1)
            
            # Add warning to login description if present
            if 'class="login-desc"' in content:
                demo_text = '\n            <p style="color:#ef4444;font-weight:600;margin-top:1rem">⚠️ Demo Panel - Not a real admin interface</p>'
                content = re.sub(r'(class="login-desc">.*?</p>)', r'\1' + demo_text, content, count=1, flags=re.DOTALL)
        
        # Write back if content changed
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
        
    except Exception as e:
        print(f"  Error processing {filename}: {e}")
        return False

def main():
    html_dir = Path('aegis-promotional/html')
    
    # Get all HTML files
    html_files = sorted([f for f in html_dir.glob('*.html') if not f.name.endswith('.bak')])
    
    print(f"Found {len(html_files)} HTML files to process")
    print("-" * 60)
    
    updated = 0
    skipped = 0
    errors = 0
    
    for html_file in html_files:
        result = process_html_file(html_file)
        if result is True:
            print(f"✓ Updated: {html_file.name}")
            updated += 1
        elif result is False and html_file.name not in ['terms.html', 'privacy.html', 'disclaimer.html']:
            print(f"  No changes needed: {html_file.name}")
            skipped += 1
    
    print("-" * 60)
    print(f"Summary:")
    print(f"  Updated: {updated} files")
    print(f"  Skipped: {skipped} files")
    print(f"  Legal pages: 3 files (already complete)")
    
    return updated > 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)