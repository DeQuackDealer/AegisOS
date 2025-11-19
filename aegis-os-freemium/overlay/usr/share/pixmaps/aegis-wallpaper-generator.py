
#!/usr/bin/env python3
"""
Aegis OS Wallpaper Generator
Creates a professional wallpaper for Aegis OS
"""

from PIL import Image, ImageDraw, ImageFont
import math

def create_aegis_wallpaper():
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
    img.save('/usr/share/pixmaps/aegis-wallpaper.jpg', 'JPEG', quality=95)
    print("✅ Aegis OS wallpaper generated: /usr/share/pixmaps/aegis-wallpaper.jpg")

if __name__ == "__main__":
    create_aegis_wallpaper()
