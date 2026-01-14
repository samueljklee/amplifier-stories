---
bundle:
  name: amplifier-stories
  version: 1.0.0
  description: Create polished HTML presentations showcasing Amplifier features and projects

includes:
  - bundle: git+https://github.com/microsoft/amplifier-foundation@main

agents:
  storyteller:
    path: amplifier-stories:agents/storyteller.md
---

# Amplifier Stories

A bundle for creating polished HTML presentation decks that showcase Amplifier features and projects.

## What This Bundle Does

The **storyteller** agent creates "Useful Apple Keynote" style presentations:
- Black backgrounds, clean typography
- One concept per slide with big impact numbers
- Code examples, comparison tables, flow diagrams
- Velocity slides showing development speed
- Automatic deployment to SharePoint (if configured)

## Usage

```
"Use storyteller to tell a story about [feature]"
"Create a deck about the new shadow environments feature"
"Make a presentation showing off recipe cancellation"
```

## Local Configuration

For SharePoint deployment, copy `.env.local.example` to `.env.local` and set your path:

```bash
cp .env.local.example .env.local
# Edit .env.local with your SharePoint folder path
```

Then deploy with:
```bash
./deploy.sh                    # All decks
./deploy.sh my-deck.html       # Specific deck
```

---

@amplifier-stories:context/storyteller-instructions.md

---

@foundation:context/shared/common-system-base.md
