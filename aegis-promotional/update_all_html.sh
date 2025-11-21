#!/bin/bash

# Comprehensive Legal Footer
read -r -d '' LEGAL_FOOTER << 'EOF'
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
    </footer>
</body>
</html>
EOF

# Demo notice for index.html
read -r -d '' DEMO_NOTICE << 'EOF'
    <div style="background:linear-gradient(135deg,#fbbf24,#f59e0b);color:#1f2937;padding:1rem 2rem;text-align:center;font-weight:600;margin-bottom:2rem">
        <p style="font-size:1.1rem;margin:0">🎯 Demo & Promotional Website 🎯</p>
        <p style="font-size:0.9rem;margin:0.5rem 0 0 0;font-weight:500">All features shown are for demonstration purposes only</p>
    </div>
EOF

# Admin warning banner
read -r -d '' ADMIN_WARNING << 'EOF'
    <div style="background:#ef4444;color:#fff;padding:1rem;text-align:center;font-weight:600;position:fixed;top:0;left:0;right:0;z-index:10000">
        ⚠️ DEMO ADMIN PANEL - FOR DEMONSTRATION PURPOSES ONLY ⚠️
    </div>
EOF

cd aegis-promotional/html

echo "Processing HTML files..."
echo "========================"

# Process each HTML file
for file in *.html; do
    # Skip backup files
    if [[ "$file" == *.bak ]]; then
        continue
    fi
    
    echo "Processing: $file"
    
    # Create a temporary file
    temp_file="${file}.tmp"
    
    # Read the file and process line by line
    awk -v footer="$LEGAL_FOOTER" '
    BEGIN { in_footer = 0; skip_admin = 0 }
    
    # Remove Admin links and sections
    /<h4>Admin<\/h4>/ { skip_admin = 1; next }
    skip_admin && /<\/div>/ { skip_admin = 0; next }
    skip_admin { next }
    
    # Remove admin links
    /<a[^>]*href="[^"]*admin[^"]*"[^>]*>.*Admin.*<\/a>/ { next }
    /<a[^>]*href="\/admin"[^>]*>.*<\/a>/ { gsub(/<a[^>]*href="\/admin"[^>]*>.*<\/a>/, ""); }
    
    # Replace footer
    /<footer/ { in_footer = 1 }
    in_footer && /<\/footer>/ { 
        print footer
        in_footer = 0
        next 
    }
    in_footer { next }
    
    # Print non-footer lines
    !in_footer { print }
    
    END {
        # If no footer was found, add it before </body>
        if (!in_footer) {
            # This will be handled separately
        }
    }
    ' "$file" > "$temp_file"
    
    # Move the temporary file back
    mv "$temp_file" "$file"
done

# Special handling for index.html
echo "Adding demo notice to index.html..."
# Insert demo notice after hero section
sed -i '/<\/div>.*hero.*<\/div>/a\'"$DEMO_NOTICE" index.html 2>/dev/null || true

# Special handling for admin.html
echo "Adding warning to admin.html..."
# Insert warning after body tag
sed -i '/<body[^>]*>/a\'"$ADMIN_WARNING" admin.html 2>/dev/null || true

echo "========================"
echo "All HTML files processed"