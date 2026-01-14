# Storyteller Instructions

Detailed guidance for creating presentation decks.

## Research Phase

Before creating a deck, gather:

1. **GitHub activity** - Use `gh` CLI to find:
   - Recent commits and PRs related to the feature
   - Timeline (when did development start/end?)
   - Number of repos touched
   - Key contributors

2. **Feature details** - Understand:
   - What problem does it solve?
   - How does it work?
   - What's the user-facing impact?
   - Any metrics or numbers?

3. **Narrative angle** - Decide the story:
   - "Built with Amplifier" (showcase projects like Cortex)
   - "Amplifier Feature" (platform capabilities)
   - "Developer Experience" (tooling improvements)
   - "Enterprise Value" (compliance, cost, scale)

## Creating the Deck

### HTML Template

Start with this structure:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Deck Title</title>
    <style>
        /* Full CSS inline - see presentation-styles.md */
    </style>
</head>
<body>
    <!-- Slides -->
    <div class="slide active">...</div>
    <div class="slide">...</div>
    
    <!-- Navigation -->
    <div class="nav" id="nav"></div>
    <div class="slide-counter" id="counter"></div>
    
    <script>
        /* Navigation JS - arrow keys, click, dots */
    </script>
</body>
</html>
```

### Navigation JavaScript

Always include this for keyboard/click/dot navigation:

```javascript
const slides = document.querySelectorAll('.slide');
let currentSlide = 0;

function showSlide(n) {
    slides[currentSlide].classList.remove('active');
    currentSlide = (n + slides.length) % slides.length;
    slides[currentSlide].classList.add('active');
    updateNav();
}

function updateNav() {
    const nav = document.getElementById('nav');
    const counter = document.getElementById('counter');
    nav.innerHTML = '';
    slides.forEach((_, i) => {
        const dot = document.createElement('div');
        dot.className = 'nav-dot' + (i === currentSlide ? ' active' : '');
        dot.onclick = () => showSlide(i);
        nav.appendChild(dot);
    });
    counter.textContent = `${currentSlide + 1} / ${slides.length}`;
}

document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowRight' || e.key === ' ') showSlide(currentSlide + 1);
    if (e.key === 'ArrowLeft') showSlide(currentSlide - 1);
});

document.addEventListener('click', (e) => {
    if (e.target.closest('.nav')) return;
    if (e.clientX > window.innerWidth / 2) showSlide(currentSlide + 1);
    else showSlide(currentSlide - 1);
});

updateNav();
```

### Slide Types

**Title Slide:**
```html
<div class="slide active center">
    <div class="section-label">Category</div>
    <h1 class="headline">Feature Name</h1>
    <p class="subhead">One-line description</p>
    <div class="small-text">January 2026</div>
</div>
```

**Problem Slide:**
```html
<div class="slide">
    <div class="section-label">The Problem</div>
    <h2 class="headline">Pain point headline</h2>
    <div class="thirds">
        <div class="card">...</div>
        <div class="card">...</div>
        <div class="card">...</div>
    </div>
</div>
```

**Code Example Slide:**
```html
<div class="slide">
    <div class="section-label">Usage</div>
    <h2 class="medium-headline">How to use it</h2>
    <div class="code-block">
<span class="code-comment"># Comment</span>
command --flag value
    </div>
</div>
```

**Velocity Slide:**
```html
<div class="slide center">
    <h2 class="medium-headline">Development velocity</h2>
    <div class="velocity-grid">
        <div class="velocity-stat">
            <div class="velocity-number">3</div>
            <div class="velocity-label">Repositories</div>
        </div>
        <!-- More stats -->
    </div>
</div>
```

## Quality Checklist

Before presenting to user:

- [ ] Navigation works (arrows, click, dots)
- [ ] Slide counter updates correctly
- [ ] No horizontal scrolling on any slide
- [ ] Code blocks don't overflow
- [ ] Consistent color scheme throughout
- [ ] Velocity slide has accurate numbers
- [ ] All links are correct

## Deployment Workflow

1. Create deck, save to `showoff/`
2. Present to user for review
3. Iterate based on feedback
4. When approved: `./deploy.sh filename.html`
5. Commit changes to git
