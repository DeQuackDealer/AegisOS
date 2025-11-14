# Aegis OS Promotional Website

Marketing website showcasing all Aegis OS editions with Windows 10-inspired design.

## Structure

```
aegis-promotional/
├── html/           # HTML pages for each edition
│   ├── index.html      # Main landing page
│   ├── freemium.html   # Freemium edition page
│   ├── basic.html      # Basic edition page
│   ├── gamer.html      # Gamer edition page
│   ├── ai.html         # AI Developer edition page
│   └── server.html     # Server edition page
├── css/
│   └── styles.css      # Windows 10-inspired styling
├── js/
│   └── main.js         # Interactive features
└── assets/             # Images and media
```

## Design Philosophy

The website uses a Windows 10-inspired aesthetic to:
- Provide familiar navigation for Windows users
- Showcase the professional nature of Aegis OS
- Demonstrate the seamless Windows compatibility (via Proton/Wine)

## Key Features

### Windows 10 Taskbar-Style Header
- Fixed top navigation
- Windows-style buttons with hover effects
- Active page highlighting

### Consistent Branding
- All editions (except Server) share the same visual style
- Color-coded tier badges
- Professional, clean design

### Server Edition
- Unique terminal/console aesthetic
- Green-on-black color scheme
- Minimal, performance-focused design

## Pages

### 1. index.html
Main landing page featuring:
- Hero section with call-to-action
- All five editions in card format
- Feature highlights
- System requirements

### 2. freemium.html
Free edition details:
- Features included in free tier
- Limitations clearly stated
- Upgrade prompts to paid tiers

### 3. basic.html
Basic paid edition:
- Security and update features
- License activation information
- Upgrade paths to specialized tiers

### 4. gamer.html
Gaming-optimized edition:
- AI-powered optimization features
- Gaming-specific enhancements
- Hardware recommendations

### 5. ai.html
AI developer edition:
- Pre-installed frameworks
- Docker and container support
- Development tools overview

### 6. server.html
Server edition (unique styling):
- Terminal-inspired design
- Enterprise features
- Server-grade specifications

## Styling Notes

### Color Scheme
- Primary: `#0078d4` (Windows blue)
- Gamer accent: `#00ff88` (bright green)
- AI accent: `#ff00ff` (magenta)
- Server accent: `#ff8800` (orange)

### Typography
- Font: Segoe UI (Windows standard)
- Clean, readable hierarchy
- Professional presentation

### Responsive Design
- Mobile-friendly navigation
- Adaptive card layouts
- Touch-friendly buttons

## Interactive Features

### JavaScript Enhancements
- Smooth scrolling for anchor links
- Active navigation highlighting
- Scroll animations for feature boxes
- Console easter egg

### Animations
- Fade-in on scroll
- Hover effects on cards and buttons
- Smooth transitions

## Usage

### Local Development
```bash
cd aegis-promotional/html
python3 -m http.server 8080
```

Visit `http://localhost:8080/index.html`

### Production Deployment
- Deploy to static hosting (Netlify, Vercel, GitHub Pages)
- Use CDN for assets
- Enable HTTPS
- Optimize images for web

## Customization

### Adding New Editions
1. Create new HTML file in `html/`
2. Add navigation button to all pages
3. Create version card on index.html
4. Define accent color in CSS

### Modifying Styles
- Edit `css/styles.css`
- Use CSS custom properties (`:root`)
- Maintain Windows 10 aesthetic

### Adding Features
- Update feature grids in respective pages
- Add icons (emoji or icon font)
- Maintain consistent layout

## Assets

### Images
Place in `assets/` directory:
- Logo files
- Screenshots
- Feature illustrations
- Icons

### Optimization
- Compress images (WebP format recommended)
- Minify CSS and JS for production
- Use lazy loading for images

## SEO Considerations

- Add meta descriptions to all pages
- Include Open Graph tags
- Add structured data for products
- Create sitemap.xml
- Optimize page titles

## Accessibility

- Semantic HTML structure
- ARIA labels where needed
- Keyboard navigation support
- High contrast for server edition
- Screen reader friendly

---

**Note**: This is a promotional website only. It does not contain actual OS functionality.
