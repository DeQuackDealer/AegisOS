#!/usr/bin/env python3
"""
Script to update all HTML pages with legal disclaimers and remove admin links
"""

import os
import re
from pathlib import Path

# Comprehensive legal footer HTML
LEGAL_FOOTER = '''<footer class="footer" style="background:#1f2937;color:#f3f4f6;padding:3rem 2rem 2rem;margin-top:3rem;border-top:1px solid #333">
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
                <a href="/" style="color:#60a5fa;text-decoration:none;margin:0 10px;font-size:0.95rem">Home</a>
                <span style="color:#4b5563">|</span>
                <a href="/terms" style="color:#60a5fa;text-decoration:none;margin:0 10px;font-size:0.95rem">Terms of Service</a>
                <span style="color:#4b5563">|</span>
                <a href="/privacy" style="color:#60a5fa;text-decoration:none;margin:0 10px;font-size:0.95rem">Privacy Policy</a>
                <span style="color:#4b5563">|</span>
                <a href="/disclaimer" style="color:#60a5fa;text-decoration:none;margin:0 10px;font-size:0.95rem">Disclaimer</a>
                <span style="color:#4b5563">|</span>
                <a href="/contact" style="color:#60a5fa;text-decoration:none;margin:0 10px;font-size:0.95rem">Contact</a>
                <span style="color:#4b5563">|</span>
                <a href="/faq" style="color:#60a5fa;text-decoration:none;margin:0 10px;font-size:0.95rem">FAQ</a>
            </nav>
            <p style="font-size:0.85rem;color:#6b7280">This website is for demonstration purposes only. No actual software is distributed.</p>
        </div>
    </div>
</footer>'''

def remove_admin_links_and_update_footer(content):
    """Remove admin links and replace footer"""
    
    # Remove Admin links from navigation and footers
    # Pattern 1: Links with href="/admin" or href="admin.html"
    content = re.sub(r'\s*<a[^>]*href=["\']/?admin(?:\.html)?["\'][^>]*>.*?Admin.*?</a>\s*(?:\|\s*)?', '', content, flags=re.IGNORECASE)
    
    # Pattern 2: Remove Admin links with surrounding separators
    content = re.sub(r'\|\s*<a[^>]*>Admin</a>\s*(?:\||$)', '', content, flags=re.IGNORECASE)
    content = re.sub(r'<a[^>]*>Admin</a>\s*\|', '', content, flags=re.IGNORECASE)
    
    # Clean up double separators that might be left
    content = re.sub(r'\|\s*\|', '|', content)
    
    # Replace existing footer with new legal footer
    # Match various footer patterns
    content = re.sub(r'<footer[^>]*>.*?</footer>', LEGAL_FOOTER, content, flags=re.DOTALL | re.IGNORECASE)
    
    # If no footer exists, add it before </body>
    if '</footer>' not in content.lower():
        content = re.sub(r'(</body>)', LEGAL_FOOTER + r'\n\1', content, flags=re.IGNORECASE)
    
    return content

def add_index_notice(content):
    """Add demo notice to index.html"""
    demo_notice = '''<div style="background:linear-gradient(135deg,#fbbf24,#f59e0b);color:#1f2937;padding:1rem 2rem;text-align:center;font-weight:600;margin-top:-2rem;margin-bottom:2rem">
        <p style="font-size:1.1rem;margin:0">🎯 Demo & Promotional Website 🎯</p>
        <p style="font-size:0.9rem;margin:0.5rem 0 0 0;font-weight:500">All features shown are for demonstration purposes only</p>
    </div>'''
    
    # Add notice after the hero section
    if '<div class="hero-content">' in content:
        # Insert after hero section closes
        content = re.sub(r'(</div>\s*</div>)', r'\1\n' + demo_notice, content, count=1)
    elif '<section' in content:
        # Insert before first section
        content = re.sub(r'(<section)', demo_notice + r'\n\1', content, count=1)
    else:
        # Insert after body opening
        content = re.sub(r'(<body[^>]*>)', r'\1\n' + demo_notice, content, count=1)
    
    return content

def add_admin_warning(content):
    """Add warning to admin.html"""
    warning = '''<div style="background:#ef4444;color:#fff;padding:1rem;text-align:center;font-weight:600;position:fixed;top:0;left:0;right:0;z-index:10000">
        ⚠️ DEMO ADMIN PANEL - FOR DEMONSTRATION PURPOSES ONLY ⚠️
    </div>'''
    
    # Add warning at the top of body
    content = re.sub(r'(<body[^>]*>)', r'\1\n' + warning, content, count=1)
    
    # Also add to login page
    if 'login-desc' in content:
        content = re.sub(
            r'(<p class="login-desc">.*?</p>)',
            r'\1\n<p style="color:#ef4444;font-weight:600;margin-top:1rem">⚠️ Demo Panel - Not a real admin interface</p>',
            content
        )
    
    return content

def process_html_files():
    """Process all HTML files"""
    html_dir = Path('aegis-promotional/html')
    processed_files = []
    
    # Get all HTML files (excluding .bak files)
    html_files = [f for f in html_dir.glob('*.html') if not f.name.endswith('.bak')]
    
    for html_file in html_files:
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Apply updates
            content = remove_admin_links_and_update_footer(content)
            
            # Special handling for specific files
            if html_file.name == 'index.html':
                content = add_index_notice(content)
            elif html_file.name == 'admin.html':
                content = add_admin_warning(content)
            
            # Write back only if content changed
            if content != original_content:
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                processed_files.append(html_file.name)
                print(f"✓ Updated: {html_file.name}")
            else:
                print(f"  No changes needed: {html_file.name}")
                
        except Exception as e:
            print(f"✗ Error processing {html_file.name}: {e}")
    
    return processed_files

if __name__ == "__main__":
    print("Starting legal disclaimer updates...")
    print("-" * 50)
    
    processed = process_html_files()
    
    print("-" * 50)
    print(f"Processed {len(processed)} files with updates")
    if processed:
        print("Files updated:", ', '.join(processed))