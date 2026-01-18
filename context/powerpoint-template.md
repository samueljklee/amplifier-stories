# PowerPoint Template Specification

This template defines the visual style for all PowerPoint presentations created by the storyteller agent.

**Style:** "Useful Apple Keynote" - matches the HTML presentation style exactly.

**Reference:** Replicates the black background, blue gradient, clean typography style from existing HTML presentations.

---

## Color Palette

### Primary Colors
```
Background:     #000000 (Black)
Text Primary:   #FFFFFF (White)
Text Secondary: rgba(255,255,255,0.7) (White 70%)
Accent Blue:    #0A84FF (Amplifier Blue)
Accent Purple:  #5E5CE6 (Amplifier Purple)
```

### Code & Syntax Colors
```
Code Text:      #98D4A0 (Green)
Code Comment:   rgba(255,255,255,0.4) (White 40%)
Code Keyword:   #FF7AC6 (Pink)
Code String:    #98D4A0 (Green)
```

### Functional Colors
```
Success Green:  #30D158
Warning Orange: #FF9F0A
Error Red:      #FF453A
Info Teal:      #64D2FF
```

### Gradient (for big numbers/titles)
```
Blue Gradient:  linear-gradient(135deg, #0A84FF, #5E5CE6)
Green Gradient: linear-gradient(135deg, #30D158, #00D4FF)
```

### Surface Colors (for cards/boxes)
```
Card Background:  rgba(255,255,255,0.05)
Card Border:      rgba(255,255,255,0.1)
Code Background:  rgba(255,255,255,0.05)
Code Border:      rgba(255,255,255,0.1)
```

### Usage Guidelines
- **Slide backgrounds:** Always #000000 (black)
- **Main headings:** White (#FFFFFF), bold
- **Section labels:** Accent Blue (#0A84FF), uppercase, letter-spacing
- **Body text:** White or White 70% for secondary
- **Code blocks:** Dark subtle background with green text
- **Accents:** Use blue gradient for big impact numbers

---

## Typography

### Font Families
```css
Primary:   Arial, 'SF Pro Display', -apple-system, sans-serif
Code:      'Courier New', 'SF Mono', 'Fira Code', monospace
```

**Web-safe fonts for html2pptx:**
- Primary: Arial (clean sans-serif)
- Code: Courier New (monospace)

### Type Scale

**Title Slides:**
```
Main Headline:   72pt, Bold (700), White (#FFFFFF)
Subtitle:        32pt, Regular (400), White 70%
Section Label:   14pt, Bold (600), ALL CAPS, Accent Blue (#0A84FF)
Date/Meta:       16pt, Regular, White 70%
```

**Content Slides:**
```
Slide Heading:   48pt, Bold (600), White (#FFFFFF)
Section Label:   14pt, Bold (600), ALL CAPS, Accent Blue (#0A84FF)
Body Text:       20pt, Regular (400), White (#FFFFFF)
Secondary Text:  16pt, Regular, White 70%
Bullets Level 1: 24pt, Regular, White (#FFFFFF)
Bullets Level 2: 20pt, Regular, White 70%
```

**Code & Technical:**
```
Code Text:       18pt, Regular, Green (#98D4A0)
Code Comments:   18pt, Regular, White 40%
Code Keywords:   18pt, Regular, Pink (#FF7AC6)
```

**Big Numbers (Impact Slides):**
```
Large Numbers:   180pt, Bold (700), Blue Gradient
Number Labels:   24pt, Regular, White 70%
```

### Line Heights
```
Headlines:   1.1 (very tight)
Headings:    1.2 (tight)
Body text:   1.5 (comfortable)
Bullets:     1.6 (generous)
Code blocks: 1.6 (very readable)
```

### Letter Spacing
```
Headlines:      -2px (tight, modern)
Headings:       -1px (slightly tight)
Section Labels: +2px (expanded, uppercase)
Body text:      normal
```

---

## Layout Patterns

### Dimensions
```
Aspect Ratio: 16:9
Width:        720pt (10 inches)
Height:       405pt (5.625 inches)
```

### Margins & Spacing
```
Top margin:        60pt
Bottom margin:     60pt
Left margin:       80pt
Right margin:      80pt

Section spacing:   40pt (between major sections)
Element spacing:   24pt (between elements)
Bullet spacing:    16pt (between bullet items)
Card gap:          40pt (between cards in grid)
```

### Grid Layouts
```
Two-column:   1fr 1fr with 80pt gap
Three-column: repeat(3, 1fr) with 40pt gap
Cards:        Use CSS Grid with gap: 40px
```

---

## Slide Templates

### 1. Title Slide
```
Layout:
┌─────────────────────────────────────────────────┐
│                    BLACK (#000)                 │
│          [SECTION LABEL - 14pt, Blue]          │
│                                                 │
│        [MAIN TITLE - 72pt, Bold, White]        │
│        (with blue gradient if big number)      │
│                                                 │
│      [Subtitle - 32pt, White 70%]              │
│                                                 │
│        [Date - 16pt, White 70%, Bottom]        │
│                                                 │
└─────────────────────────────────────────────────┘
```

**Style:**
- Centered alignment
- Large headline with gradient optional
- Generous whitespace
- Blue section label

### 2. Content Slide (Standard)
```
Layout:
┌─────────────────────────────────────────────────┐
│ BLACK (#000)                                    │
│ [Section Label - 14pt, Blue, UPPERCASE]        │
│                                                 │
│ [Slide Heading - 48pt, Bold, White]            │
│                                                 │
│ • [Bullet - 24pt, White]                       │
│ • [Bullet - 24pt, White]                       │
│ • [Bullet - 24pt, White]                       │
│                                                 │
└─────────────────────────────────────────────────┘
```

**Style:**
- Left-aligned content
- Section label in blue
- Large bullets for readability
- Maximum 5-6 bullets per slide

### 3. Two-Column Comparison
```
Layout:
┌─────────────────────────────────────────────────┐
│ BLACK (#000)                                    │
│ [Heading - 48pt, Bold, White]                  │
│                                                 │
│ ┌──────────────┐  ┌──────────────┐            │
│ │   Before     │  │    After      │            │
│ │ (subtle bg)  │  │ (subtle bg)   │            │
│ │ • Point      │  │ • Point       │            │
│ │ • Point      │  │ • Point       │            │
│ └──────────────┘  └──────────────┘            │
│                                                 │
└─────────────────────────────────────────────────┘
```

**Style:**
- Equal width columns with 80pt gap
- Subtle card backgrounds: rgba(255,255,255,0.05)
- Card borders: rgba(255,255,255,0.1)
- Border-radius: 16px

### 4. Code Example Slide
```
Layout:
┌─────────────────────────────────────────────────┐
│ BLACK (#000)                                    │
│ [Section Label - 14pt, Blue]                   │
│ [Heading - 48pt, Bold, White]                  │
│                                                 │
│ ┌─────────────────────────────────────────────┐│
│ │ # Code - 18pt, Green (#98D4A0)             ││
│ │ command --flag value                        ││
│ │ output result                               ││
│ └─────────────────────────────────────────────┘│
│                                                 │
└─────────────────────────────────────────────────┘
```

**Style:**
- Code background: rgba(255,255,255,0.05)
- Code border: rgba(255,255,255,0.1)
- Border-radius: 12px
- Padding: 24pt 32pt
- **CRITICAL:** white-space: pre (preserves formatting)
- Code text: Green (#98D4A0)
- Comments: White 40%

### 5. Cards/Features Grid
```
Layout:
┌─────────────────────────────────────────────────┐
│ BLACK (#000)                                    │
│ [Heading - 48pt, Bold, White]                  │
│                                                 │
│ ┌──────┐  ┌──────┐  ┌──────┐                  │
│ │Card  │  │Card  │  │Card  │                  │
│ │Title │  │Title │  │Title │                  │
│ │Text  │  │Text  │  │Text  │                  │
│ └──────┘  └──────┘  └──────┘                  │
│                                                 │
└─────────────────────────────────────────────────┘
```

**Style:**
- Card background: rgba(255,255,255,0.05)
- Card border: 1px solid rgba(255,255,255,0.1)
- Border-radius: 16px
- Padding: 32pt
- Card title: 20pt, Bold, Blue (#0A84FF)
- Card text: 16pt, White 70%

### 6. Big Number/Impact Slide
```
Layout:
┌─────────────────────────────────────────────────┐
│ BLACK (#000)                                    │
│ [Heading - 48pt, Bold, White, Center]          │
│                                                 │
│            [180pt, BLUE GRADIENT]              │
│               3,000                             │
│                                                 │
│         [Label - 24pt, White 70%]              │
│                                                 │
└─────────────────────────────────────────────────┘
```

**Style:**
- Centered alignment
- Huge gradient number (180pt)
- Gradient: linear-gradient(135deg, #0A84FF, #5E5CE6)
- Label below in white 70%

---

## Visual Elements

### Cards & Containers
```css
.card {
    background: rgba(255,255,255,0.05);  /* Subtle white overlay */
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 32px;
}

.card-title {
    font-size: 20pt;
    font-weight: 600;
    color: #0A84FF;  /* Blue */
    margin-bottom: 12pt;
}

.card-text {
    font-size: 16pt;
    color: rgba(255,255,255,0.7);  /* White 70% */
    line-height: 1.5;
}
```

### Code Blocks
```css
.code-block {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px;
    padding: 24px 32px;
    font-family: 'Courier New', monospace;
    font-size: 18px;
    line-height: 1.6;
    white-space: pre;  /* CRITICAL: Preserves formatting */
    color: #98D4A0;  /* Green for code */
    overflow-x: auto;
}

.code-comment {
    color: rgba(255,255,255,0.4);
}

.code-keyword {
    color: #FF7AC6;  /* Pink */
}
```

### Icons & Bullets
```
Bullets:          Standard round bullets (•)
Bullet color:     White (#FFFFFF)
Icons:            Simple, flat, 2-color max
Icon size:        24-32pt for inline, 48-64pt for standalone
```

### Dividers
```
Horizontal line:  1px solid rgba(255,255,255,0.1)
Used for:         Separating sections, bottom of list items
```

---

## Content Guidelines

### Text Density
- **Maximum 6 bullets per slide**
- **Maximum 10-12 words per bullet**
- **Prefer 3-4 bullets** for better impact
- Use sub-bullets sparingly (max 2 levels)

### Visual Hierarchy
1. **Most important:** Large, bold, dark color
2. **Supporting:** Medium size, regular weight
3. **Details:** Smaller, lighter color

### Spacing Philosophy
- **Generous whitespace** - slides should breathe
- **Consistent rhythm** - equal spacing between elements
- **Visual balance** - distribute content evenly

### Slide Flow
1. Title slide
2. Problem/Context (1-2 slides)
3. Solution overview (1 slide)
4. Deep dive details (3-5 slides)
5. Impact/Results (1-2 slides)
6. Call to action (1 slide)

**Total:** Aim for 10-15 slides for a 10-minute presentation

---

## Common Patterns

### Before/After Comparison
```css
.before-after {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 40pt;
}

.before { 
  background: #FFF4CE; /* Light yellow */
  border-left: 4pt solid #D83B01; /* Orange */
}

.after { 
  background: #DFF6DD; /* Light green */
  border-left: 4pt solid #107C10; /* Green */
}
```

### Feature Highlight
```css
.feature-highlight {
  background: #F3F2F1; /* Light gray */
  border-left: 4pt solid #0078D4; /* Blue accent */
  padding: 20pt;
}
```

### Code Block
```css
.code-block {
  background: #F3F2F1;
  font-family: 'Courier New', monospace;
  font-size: 16pt;
  line-height: 1.4;
  padding: 20pt;
  border-radius: 4pt;
}
```

### Metric Display
```css
.metric {
  text-align: center;
}

.metric-number {
  font-size: 72pt;
  font-weight: bold;
  color: #0078D4; /* Accent blue */
  line-height: 1;
}

.metric-label {
  font-size: 18pt;
  color: #595959; /* Text secondary */
  margin-top: 12pt;
}
```

---

## HTML Implementation Example

```html
<!DOCTYPE html>
<html>
<head>
<style>
body {
  width: 720pt;
  height: 405pt;
  margin: 0;
  padding: 60pt 80pt;
  font-family: Arial, -apple-system, sans-serif;
  background: #000000;  /* Black background */
  color: #FFFFFF;       /* White text */
}

/* Section labels (uppercase, blue) */
.section-label {
  font-size: 14pt;
  font-weight: 600;
  text-transform: uppercase;
  color: #0A84FF;
  letter-spacing: 2pt;
  margin-bottom: 16pt;
}

/* Main headline (title slides) */
h1 {
  font-size: 72pt;
  font-weight: 700;
  color: #FFFFFF;
  line-height: 1.1;
  letter-spacing: -2px;
  margin: 0 0 24pt 0;
}

/* Slide headings (content slides) */
h2 {
  font-size: 48pt;
  font-weight: 600;
  color: #FFFFFF;
  line-height: 1.2;
  letter-spacing: -1px;
  margin: 0 0 20pt 0;
}

/* Medium headlines */
h3 {
  font-size: 32pt;
  font-weight: 400;
  color: rgba(255,255,255,0.7);  /* White 70% */
  line-height: 1.4;
  margin: 0 0 20pt 0;
}

/* Body text */
p {
  font-size: 20pt;
  line-height: 1.5;
  color: #FFFFFF;
  margin: 0 0 24pt 0;
}

/* Lists */
ul {
  font-size: 24pt;
  line-height: 1.6;
  color: #FFFFFF;
  margin: 0;
  padding-left: 40pt;
  list-style: disc;
}

li {
  margin-bottom: 16pt;
}

/* Cards */
.card {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 16px;
  padding: 32pt;
}

.card-title {
  font-size: 20pt;
  font-weight: 600;
  color: #0A84FF;
  margin-bottom: 12pt;
}

.card-text {
  font-size: 16pt;
  color: rgba(255,255,255,0.7);
  line-height: 1.5;
}

/* Code blocks */
.code-block {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 12px;
  padding: 24pt 32pt;
  font-family: 'Courier New', monospace;
  font-size: 18pt;
  line-height: 1.6;
  white-space: pre;  /* CRITICAL: Preserves formatting */
  color: #98D4A0;    /* Green for code */
  overflow-x: auto;
}

.code-comment {
  color: rgba(255,255,255,0.4);
}

.code-keyword {
  color: #FF7AC6;  /* Pink */
}

/* Big gradient numbers */
.big-number {
  font-size: 180pt;
  font-weight: 700;
  letter-spacing: -8px;
  background: linear-gradient(135deg, #0A84FF, #5E5CE6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  line-height: 1;
  text-align: center;
}

/* Grid layouts */
.split {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 80pt;
}

.thirds {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 40pt;
}
</style>
</head>
<body>
  <!-- Slide content here -->
</body>
</html>
```

---

## Quality Checklist

Before finalizing any PowerPoint:

- [ ] Colors match the palette (no random colors)
- [ ] Fonts are consistent (Arial for body, Courier New for code)
- [ ] Margins are 60pt/80pt top-bottom/left-right
- [ ] Maximum 6 bullets per slide
- [ ] Generous whitespace on every slide
- [ ] Visual hierarchy is clear (size + weight + color)
- [ ] Code blocks have light gray background
- [ ] Text is left-aligned (except title slides)
- [ ] No text smaller than 14pt
- [ ] Consistent spacing between elements
