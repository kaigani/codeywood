# Codeywood Documentation Site

This is the GitHub Pages documentation site for the Codeywood project.

## Local Development

To preview the site locally, you can use any static file server:

```bash
# Using Python
cd docs
python -m http.server 8000

# Using Node.js (npx)
npx serve docs

# Using PHP
php -S localhost:8000 -t docs
```

Then open http://localhost:8000 in your browser.

## GitHub Pages Setup

1. Go to your repository Settings
2. Navigate to Pages (under "Code and automation")
3. Under "Build and deployment":
   - Source: Deploy from a branch
   - Branch: `main` (or your default branch)
   - Folder: `/docs`
4. Save and wait for deployment

The site will be available at: `https://kaigani.github.io/codeywood/`

## Files

- `index.html` - Main documentation page
- `style.css` - Pixel art themed styles with Google Fonts
- `script.js` - Parallax scrolling and interactive effects
- `header.jpg` - Hero image (Codeywood pixel art sign)

## Customization

### Adding Images

Place additional images in this folder and reference them in the HTML. Suggested images to create:

- `workflow-diagram.png` - Visual workflow illustration
- `skill-icons/` - Individual icons for each skill category
- `screenshots/` - Example outputs from the system

### Modifying Content

Edit `index.html` to update:
- Navigation links
- Section content
- Roadmap progress
- Getting started steps

### Styling

The CSS uses CSS custom properties (variables) at the top of `style.css`. Key variables:

```css
--accent-gold: #f4d03f;      /* Primary accent color */
--accent-blue: #4ecdc4;      /* Secondary accent */
--bg-dark: #0a0a1a;          /* Main background */
--font-pixel: 'Press Start 2P';  /* Pixel font */
```

## License

This documentation site is part of the Codeywood project and is open source under the MIT License.
