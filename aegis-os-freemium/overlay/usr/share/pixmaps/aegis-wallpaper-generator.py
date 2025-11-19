#!/usr/bin/env python3
"""
Aegis OS Wallpaper Generator
Creates a professional wallpaper for Aegis OS
Works with PIL or falls back to SVG generation
"""

import os
import math
import sys

# Try to import PIL
try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️  PIL not available, using SVG fallback")

def create_aegis_wallpaper_pil():
    """Create wallpaper using PIL"""
    # Create 1920x1080 wallpaper
    width, height = 1920, 1080
    img = Image.new('RGB', (width, height), color='#0d1117')
    draw = ImageDraw.Draw(img)
    
    # Create gradient background
    for y in range(height):
        r = int(13 + (y / height) * 30)
        g = int(17 + (y / height) * 40) 
        b = int(23 + (y / height) * 60)
        color = (r, g, b)
        draw.line([(0, y), (width, y)], fill=color)
    
    # Draw circuit pattern
    for i in range(0, width, 100):
        for j in range(0, height, 100):
            if (i + j) % 200 == 0:
                # Draw circuit nodes
                draw.ellipse([i-2, j-2, i+2, j+2], fill='#00ff88', width=1)
                
                # Draw connecting lines
                if i + 100 < width:
                    draw.line([i, j, i+50, j], fill='#00ff88', width=1)
                if j + 100 < height:
                    draw.line([i, j, i, j+50], fill='#00ff88', width=1)
    
    # Draw Aegis shield logo in center
    center_x, center_y = width // 2, height // 2
    
    # Shield outline
    shield_points = [
        (center_x, center_y - 100),
        (center_x - 60, center_y - 60),
        (center_x - 60, center_y + 40),
        (center_x, center_y + 100),
        (center_x + 60, center_y + 40),
        (center_x + 60, center_y - 60)
    ]
    
    # Draw shield with gradient effect
    draw.polygon(shield_points, fill='#0078d4', outline='#ffffff', width=3)
    
    # Draw inner shield
    inner_shield = [(x * 0.7 + center_x * 0.3, y * 0.7 + center_y * 0.3) for x, y in shield_points]
    draw.polygon(inner_shield, fill='#106ebe', outline='#ffffff', width=2)
    
    # Draw 'A' in center
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 60)
    except:
        font = ImageFont.load_default()
    
    draw.text((center_x, center_y - 10), 'A', font=font, fill='#ffffff', anchor='mm')
    
    # Draw "AEGIS OS" text below shield
    try:
        title_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 48)
        subtitle_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 24)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
    
    draw.text((center_x, center_y + 150), 'AEGIS OS', font=title_font, fill='#ffffff', anchor='mm')
    draw.text((center_x, center_y + 200), 'Freemium Edition', font=subtitle_font, fill='#00ff88', anchor='mm')
    draw.text((center_x, center_y + 230), 'The Gold Standard for Gaming', font=subtitle_font, fill='#888888', anchor='mm')
    
    # Save wallpaper
    output_dir = '/usr/share/backgrounds'
    os.makedirs(output_dir, exist_ok=True)
    
    img.save(f'{output_dir}/aegis-wallpaper.png', 'PNG')
    # Also save as JPG for better compatibility
    img.save('/usr/share/pixmaps/aegis-wallpaper.jpg', 'JPEG', quality=95)
    
    print("✅ Aegis OS wallpaper generated with PIL")
    print(f"   - PNG: {output_dir}/aegis-wallpaper.png")
    print("   - JPG: /usr/share/pixmaps/aegis-wallpaper.jpg")

def create_aegis_wallpaper_svg():
    """Create wallpaper using SVG (fallback when PIL is not available)"""
    width, height = 1920, 1080
    center_x, center_y = width // 2, height // 2
    
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
    <!-- Gradient background -->
    <defs>
        <linearGradient id="bgGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:#0d1117;stop-opacity:1" />
            <stop offset="50%" style="stop-color:#1a2332;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#2d3f5f;stop-opacity:1" />
        </linearGradient>
        
        <!-- Shield gradient -->
        <linearGradient id="shieldGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:#0078d4;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#106ebe;stop-opacity:1" />
        </linearGradient>
        
        <!-- Glow effect -->
        <filter id="glow">
            <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
            <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
            </feMerge>
        </filter>
    </defs>
    
    <!-- Background -->
    <rect width="{width}" height="{height}" fill="url(#bgGradient)"/>
    
    <!-- Circuit pattern -->
    <g opacity="0.3">'''
    
    # Add circuit pattern
    for i in range(0, width, 100):
        for j in range(0, height, 100):
            if (i + j) % 200 == 0:
                svg_content += f'''
        <circle cx="{i}" cy="{j}" r="3" fill="#00ff88" filter="url(#glow)"/>'''
                if i + 100 < width:
                    svg_content += f'''
        <line x1="{i}" y1="{j}" x2="{i+50}" y2="{j}" stroke="#00ff88" stroke-width="1" opacity="0.5"/>'''
                if j + 100 < height:
                    svg_content += f'''
        <line x1="{i}" y1="{j}" x2="{i}" y2="{j+50}" stroke="#00ff88" stroke-width="1" opacity="0.5"/>'''
    
    svg_content += f'''
    </g>
    
    <!-- Aegis Shield -->
    <g transform="translate({center_x}, {center_y})">
        <!-- Outer shield -->
        <path d="M 0,-100 L -60,-60 L -60,40 L 0,100 L 60,40 L 60,-60 Z"
              fill="url(#shieldGradient)" stroke="white" stroke-width="3" filter="url(#glow)"/>
        
        <!-- Inner shield -->
        <path d="M 0,-70 L -42,-42 L -42,28 L 0,70 L 42,28 L 42,-42 Z"
              fill="#106ebe" stroke="white" stroke-width="2" opacity="0.8"/>
        
        <!-- Letter A -->
        <text x="0" y="10" font-family="Arial, sans-serif" font-size="60" font-weight="bold" 
              fill="white" text-anchor="middle" filter="url(#glow)">A</text>
    </g>
    
    <!-- Title text -->
    <text x="{center_x}" y="{center_y + 150}" font-family="Arial, sans-serif" font-size="48" 
          font-weight="bold" fill="white" text-anchor="middle">AEGIS OS</text>
    
    <!-- Subtitle -->
    <text x="{center_x}" y="{center_y + 200}" font-family="Arial, sans-serif" font-size="24" 
          fill="#00ff88" text-anchor="middle">Freemium Edition</text>
    
    <!-- Tagline -->
    <text x="{center_x}" y="{center_y + 230}" font-family="Arial, sans-serif" font-size="20" 
          fill="#888888" text-anchor="middle">The Gold Standard for Gaming</text>
    
    <!-- Corner decoration -->
    <g opacity="0.5">
        <rect x="0" y="0" width="200" height="2" fill="#00ff88"/>
        <rect x="0" y="0" width="2" height="200" fill="#00ff88"/>
        <rect x="{width-200}" y="{height-2}" width="200" height="2" fill="#00ff88"/>
        <rect x="{width-2}" y="{height-200}" width="2" height="200" fill="#00ff88"/>
    </g>
</svg>'''
    
    # Save SVG file
    svg_path = '/usr/share/pixmaps/aegis-wallpaper.svg'
    with open(svg_path, 'w') as f:
        f.write(svg_content)
    
    print("✅ Aegis OS wallpaper generated as SVG")
    print(f"   - SVG: {svg_path}")
    
    # Try to convert SVG to PNG using ImageMagick or rsvg-convert if available
    output_dir = '/usr/share/backgrounds'
    os.makedirs(output_dir, exist_ok=True)
    png_path = f'{output_dir}/aegis-wallpaper.png'
    
    # Try rsvg-convert first
    try:
        import subprocess
        result = subprocess.run([
            'rsvg-convert', '-w', str(width), '-h', str(height),
            '-o', png_path, svg_path
        ], capture_output=True)
        if result.returncode == 0:
            print(f"   - PNG: {png_path} (converted from SVG)")
            return
    except:
        pass
    
    # Try ImageMagick convert
    try:
        import subprocess
        result = subprocess.run([
            'convert', '-background', 'none', '-density', '96',
            svg_path, png_path
        ], capture_output=True)
        if result.returncode == 0:
            print(f"   - PNG: {png_path} (converted from SVG)")
            return
    except:
        pass
    
    print("   ℹ️  SVG to PNG conversion tools not available")
    print("   ℹ️  Using SVG directly as wallpaper")

def main():
    """Main function to generate wallpaper"""
    print("🎨 Aegis OS Wallpaper Generator")
    print("=" * 40)
    
    if PIL_AVAILABLE:
        try:
            create_aegis_wallpaper_pil()
        except Exception as e:
            print(f"❌ PIL generation failed: {e}")
            print("   Falling back to SVG generation...")
            create_aegis_wallpaper_svg()
    else:
        create_aegis_wallpaper_svg()
    
    print("=" * 40)
    print("✅ Wallpaper generation complete!")

if __name__ == "__main__":
    main()