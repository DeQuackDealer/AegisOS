#!/usr/bin/env python3

import os
from pathlib import Path

# New legal footer to add to all files
LEGAL_FOOTER = '''    <!-- LEGAL DISCLAIMER FOOTER -->
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

def process_file(filepath):
    """Process a single HTML file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    skip_footer = False
    skip_admin_section = False
    
    for i, line in enumerate(lines):
        # Skip the original footer
        if '<footer' in line.lower():
            skip_footer = True
            continue
        if skip_footer and '</footer>' in line.lower():
            skip_footer = False
            continue
        if skip_footer:
            continue
            
        # Skip Admin sections in footer
        if '<h4>Admin</h4>' in line:
            skip_admin_section = True
            continue
        if skip_admin_section and '</div>' in line:
            # Check if this is the closing div for the admin section
            if i + 1 < len(lines) and '<div class="footer-col">' in lines[i + 1]:
                skip_admin_section = False
            elif i + 1 < len(lines) and '</div>' in lines[i + 1]:
                skip_admin_section = False
            continue
        if skip_admin_section:
            continue
            
        # Remove admin links
        if 'href="/admin"' in line or 'href="admin.html"' in line or 'href="admin"' in line:
            # Skip the entire line if it's just an admin link
            if '>Admin<' in line or '>License Management<' in line or 'API Status' in line or 'Health Check' in line:
                continue
        
        # Remove "| Admin" or "Admin |" patterns
        line = line.replace('| <a href="/admin">Admin</a>', '')
        line = line.replace('<a href="/admin">Admin</a> |', '')
        line = line.replace('| Admin', '')
        line = line.replace('Admin |', '')
        
        # Add the line if it's not being skipped
        new_lines.append(line)
        
        # Add new footer before </body>
        if '</body>' in line:
            # Insert footer before </body>
            new_lines.insert(-1, LEGAL_FOOTER + '\n')
    
    # Special handling for specific files
    filename = os.path.basename(filepath)
    
    if filename == 'index.html':
        # Add demo notice after hero section
        demo_notice = '''    <!-- DEMO NOTICE -->
    <div style="background:linear-gradient(135deg,#fbbf24,#f59e0b);color:#1f2937;padding:1rem 2rem;text-align:center;font-weight:600;margin-bottom:2rem">
        <p style="font-size:1.1rem;margin:0">🎯 Demo & Promotional Website 🎯</p>
        <p style="font-size:0.9rem;margin:0.5rem 0 0 0;font-weight:500">All features shown are for demonstration purposes only</p>
    </div>
'''
        # Find hero section end and insert notice
        for i, line in enumerate(new_lines):
            if 'class="hero"' in line:
                # Find the closing of hero section (two </div> tags)
                count = 0
                for j in range(i, min(i + 50, len(new_lines))):
                    if '</div>' in new_lines[j]:
                        count += 1
                        if count == 2:
                            new_lines.insert(j + 1, demo_notice)
                            break
                break
    
    elif filename == 'admin.html':
        # Add warning banner
        warning = '''    <!-- ADMIN WARNING -->
    <div style="background:#ef4444;color:#fff;padding:1rem;text-align:center;font-weight:600;position:fixed;top:0;left:0;right:0;z-index:10000">
        ⚠️ DEMO ADMIN PANEL - FOR DEMONSTRATION PURPOSES ONLY ⚠️
    </div>
'''
        # Insert after <body>
        for i, line in enumerate(new_lines):
            if '<body' in line:
                new_lines.insert(i + 1, warning)
                break
        
        # Add warning to login description
        for i, line in enumerate(new_lines):
            if 'class="login-desc"' in line:
                demo_text = '            <p style="color:#ef4444;font-weight:600;margin-top:1rem">⚠️ Demo Panel - Not a real admin interface</p>\n'
                new_lines.insert(i + 1, demo_text)
                break
    
    # Write the file back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    return True

# Process all HTML files
html_dir = Path('aegis-promotional/html')
processed = 0
errors = 0

print("Processing HTML files...")
print("-" * 60)

for html_file in sorted(html_dir.glob('*.html')):
    if html_file.name.endswith('.bak'):
        continue
    
    try:
        process_file(html_file)
        print(f"✓ Updated: {html_file.name}")
        processed += 1
    except Exception as e:
        print(f"✗ Error with {html_file.name}: {e}")
        errors += 1

print("-" * 60)
print(f"Processed: {processed} files")
if errors:
    print(f"Errors: {errors} files")