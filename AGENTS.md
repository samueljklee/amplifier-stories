# Amplifier Stories Bundle

This is an **Amplifier bundle** for creating presentation decks showcasing Amplifier features and projects.

## Installation

```bash
# Add to your bundles
amplifier bundle add git+https://github.com/ramparte/amplifier-stories@master

# Or run directly
amplifier run --bundle git+https://github.com/ramparte/amplifier-stories@master
```

## Usage

Once the bundle is loaded, use the **storyteller** agent:

```
"Use storyteller to tell a story about [feature]"
"Create a deck about the new shadow environments feature"
"Make a presentation showing off recipe cancellation"
```

The storyteller agent will:
1. Research the feature (GitHub history, PRs, timeline)
2. Create a polished HTML deck in "Useful Apple Keynote" style
3. Save to `showoff/` directory
4. Deploy to SharePoint when you approve

## Local Development

If you clone this repo directly for development:

```bash
# Set up SharePoint deployment
cp .env.local.example .env.local
# Edit .env.local with your SharePoint path

# Deploy decks
./deploy.sh                    # All decks
./deploy.sh my-deck.html       # Specific deck
```

## Bundle Structure

```
amplifier-stories/
├── bundle.md              # Bundle definition
├── agents/
│   └── storyteller.md     # Storyteller agent
├── context/
│   ├── presentation-styles.md
│   └── storyteller-instructions.md
├── showoff/               # Generated decks
├── deploy.sh              # SharePoint deployment
├── .env.local             # Your SharePoint path (gitignored)
└── FUTURE_TOPICS.md       # Ideas for future decks
```

## Available Decks

| Deck | Topic |
|------|-------|
| cortex-amplifier-presentation.html | Cortex project showcase |
| shadow-environments-deck.html | Shadow environment testing |
| cost-optimization-deck.html | Token cost reduction |
| session-forking-deck.html | Conversation branching |
| ecosystem-audit-deck.html | Compliance automation |
| attention-firewall-deck.html | Notification filtering |
| notifications-deck.html | Desktop/mobile alerts |

## Presentation Styles

The bundle supports two remembered styles:

- **Useful Apple Keynote** (default) - Higher density, good for engineers
- **Apple Keynote** - Pure visual impact, good for executives

See `context/presentation-styles.md` for details.
