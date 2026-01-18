# Presentation Styles

Two remembered styles for different use cases.

## Useful Apple Keynote (Preferred)

Higher information density while maintaining polish. Use for most decks.

**Characteristics:**
- Black backgrounds (#000)
- Clean sans-serif typography (SF Pro Display, Segoe UI, system fonts)
- Section labels: 14px uppercase, accent color, letter-spacing: 2px
- Headlines: 48-72px, font-weight 600-700, letter-spacing: -1px to -2px
- Cards with titles and descriptions for feature grids
- Code blocks with syntax highlighting (green for code, gray for comments)
- Comparison tables and before/after layouts
- Flow diagrams with colored step boxes
- Velocity/stats grids near the end
- Navigation dots at bottom center
- Slide counter at bottom right

**CSS Essentials:**
```css
body {
    font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', Roboto, sans-serif;
    background: #000;
    color: #fff;
}

.section-label {
    font-size: 14px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: var(--accent-color);
}

.headline {
    font-size: 72px;
    font-weight: 700;
    letter-spacing: -2px;
    line-height: 1.1;
}

.card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 28px;
}

.code-block {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px;
    padding: 20px 28px;
    font-family: 'SF Mono', 'Fira Code', 'Courier New', monospace;
    font-size: 15px;
    line-height: 1.6;
    white-space: pre;  /* CRITICAL: Preserves line breaks and indentation */
    overflow-x: auto;
}
```

## Apple Keynote (Pure)

Maximum visual impact, minimal information density. Use for executive summaries or high-level vision decks.

**Characteristics:**
- Pure black backgrounds
- San Francisco typography (or similar sans-serif)
- One major concept per slide
- Full-bleed imagery where applicable
- Bold, centered headlines
- Avoid bullet points entirely
- Use icons or 3-word phrases instead of lists
- Premium, quiet, powerful aesthetic

**When to use:**
- Executive presentations
- Vision/strategy decks
- When visual impact matters more than information density

## Choosing a Style

| Audience | Recommended Style |
|----------|-------------------|
| Engineers, developers | Useful Apple Keynote |
| Executives, leadership | Apple Keynote (Pure) |
| Mixed audience | Useful Apple Keynote |
| Feature deep-dive | Useful Apple Keynote |
| Vision/roadmap | Apple Keynote (Pure) |

Default to **Useful Apple Keynote** unless specifically asked for the pure style.
