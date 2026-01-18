# Amplifier Module: Stories - Usage Guide

Complete guide to using the autonomous storytelling engine.

## Overview

**amplifier-module-stories** transforms Amplifier development activity into professional content across multiple formats and audiences - automatically.

## Quick Start

### Manual Storytelling (Conversational)

Ask the storyteller agent naturally:

```
"Create a PowerPoint about shadow environments"
"Make an Excel dashboard showing adoption metrics"
"Write a case study about this session"
```

### Automated Storytelling (Recipes)

Run workflows that generate content automatically:

```bash
# Weekly ecosystem digest (every Monday)
amplifier tool invoke recipes operation=execute \
  recipe_path=amplifier-module-stories:recipes/weekly-digest.yaml

# Generate case study from session
amplifier tool invoke recipes operation=execute \
  recipe_path=amplifier-module-stories:recipes/session-to-case-study.yaml \
  context='{"session_file": "~/.amplifier/sessions/2026-01-17/events.jsonl"}'

# Release documentation from git tag
amplifier tool invoke recipes operation=execute \
  recipe_path=amplifier-module-stories:recipes/git-tag-to-changelog.yaml \
  context='{"tag_name": "v2.0.0"}'

# Blog post from feature development
amplifier tool invoke recipes operation=execute \
  recipe_path=amplifier-module-stories:recipes/blog-post-generator.yaml \
  context='{"feature_name": "shadow environments"}'
```

---

## The 10 Specialist Agents

### 1. story-researcher
**Purpose:** Automated data gathering from git, sessions, bundles, ecosystem

**Use when:** You need data about features, development, usage, or ecosystem activity

**Example:**
```
"Use story-researcher to gather data about shadow environments development"
"Research the past month's ecosystem activity"
"Analyze this session file for case study material"
```

**Outputs:** Structured JSON with metrics, timeline, key moments, impact data

---

### 2. content-strategist
**Purpose:** Determines what stories to tell, for which audiences, in which formats

**Use when:** You have data but need to decide how to turn it into content

**Example:**
```
"Use content-strategist to plan content for the surface feature launch"
"What's the best way to tell the story of recipe workflows?"
"Plan a multi-format campaign for the 2.0 release"
```

**Outputs:** Content plan with audience mapping, format selection, narrative arc, agent assignments

---

### 3. technical-writer
**Purpose:** Creates deep technical documentation for developers

**Use when:** Developers need comprehensive understanding of architecture, APIs, or implementation

**Example:**
```
"Use technical-writer to document the session forking architecture"
"Create a technical guide for recipe development"
"Write API documentation for the Surface module"
```

**Outputs:** Word technical docs, PowerPoint deep-dives, Markdown tutorials with code

---

### 4. marketing-writer
**Purpose:** External communication for community and public audiences

**Use when:** You need engaging community content, announcements, or user-facing communication

**Example:**
```
"Use marketing-writer to create a blog post about shadow environments"
"Write a Twitter thread announcing the 2.0 release"
"Create a community announcement for the new recipe feature"
```

**Outputs:** Blog posts, social media threads, email newsletters, community announcements

---

### 5. executive-briefer
**Purpose:** High-level summaries and ROI content for decision-makers

**Use when:** Leadership needs to understand business value, ROI, or strategic implications

**Example:**
```
"Use executive-briefer to create a one-pager on Amplifier's ROI"
"Generate an executive summary of Q1 achievements"
"Create a dashboard showing business impact metrics"
```

**Outputs:** PDF one-pagers, executive summaries (PowerPoint), ROI dashboards (Excel)

---

### 6. release-manager
**Purpose:** Automates all release documentation from git tags

**Use when:** Creating a new release and need changelogs, release notes, migration guides

**Example:**
```
"Use release-manager to generate docs for v2.0.0"
"Create release notes from the latest tag"
"Generate migration guide for breaking changes"
```

**Outputs:** CHANGELOG.md entries, GitHub release notes, migration guides, announcements

---

### 7. case-study-writer
**Purpose:** Turns sessions and feature developments into narrative case studies

**Use when:** You have a breakthrough session or interesting feature story

**Example:**
```
"Use case-study-writer to create a case study from this session"
"Turn the Surface feature development into a case study"
"Write a narrative about building Cortex with Amplifier"
```

**Outputs:** Word case studies, PowerPoint narratives, blog post versions

---

### 8. data-analyst
**Purpose:** Transforms raw metrics into visual dashboards and insights

**Use when:** You have data and need professional visualizations or analysis

**Example:**
```
"Use data-analyst to create a dashboard from session data"
"Generate velocity metrics for the past month"
"Create a comparison chart showing before/after performance"
```

**Outputs:** Excel dashboards, PowerPoint metric slides, data visualizations

---

### 9. content-adapter
**Purpose:** Transforms content between formats and audiences

**Use when:** You have content in one format and need it in another, or for different audience

**Example:**
```
"Use content-adapter to convert this PowerPoint to a blog post"
"Adapt this technical doc for an executive audience"
"Create a PDF summary from this Excel dashboard"
```

**Outputs:** Content in new format or adapted for new audience

---

### 10. community-manager
**Purpose:** Celebrates community achievements and fosters engagement

**Use when:** Highlighting community contributions, user wins, or ecosystem growth

**Example:**
```
"Use community-manager to create a spotlight on this community project"
"Generate a community showcase post"
"Write a contributor recognition announcement"
```

**Outputs:** Blog posts, social media content, community announcements

---

## The 4 Automated Recipes

### 1. session-to-case-study.yaml
**Converts:** Session events.jsonl → Word case study

**When to use:** After a successful, complex session that others could learn from

**Inputs:**
- `session_file` - Path to events.jsonl (required)
- `output_name` - Custom filename (optional)

**Process:**
1. Analyzes session for complexity and outcome
2. Evaluates if case-study worthy (>10 tool calls, successful outcome)
3. Generates narrative case study in Word
4. Auto-opens for review

**Runtime:** 2-3 minutes

**Example:**
```bash
amplifier tool invoke recipes operation=execute \
  recipe_path=amplifier-module-stories:recipes/session-to-case-study.yaml \
  context='{"session_file": "~/.amplifier/sessions/2026-01-17/events.jsonl"}'
```

---

### 2. git-tag-to-changelog.yaml
**Converts:** Git tag → Complete release documentation

**When to use:** After creating a new git tag for a release

**Inputs:**
- `tag_name` - Git tag (required, e.g., "v2.0.0")
- `repo_path` - Repository path (optional, defaults to current)

**Process:**
1. Validates tag exists, finds previous tag
2. Extracts and categorizes commits (feat/fix/chore)
3. Identifies breaking changes
4. Generates CHANGELOG.md entry
5. Creates GitHub release notes
6. Generates migration guide (if breaking changes)
7. Creates announcement content (blog, social)
8. Opens PR with all documentation

**Runtime:** 2-3 minutes

**Example:**
```bash
amplifier tool invoke recipes operation=execute \
  recipe_path=amplifier-module-stories:recipes/git-tag-to-changelog.yaml \
  context='{"tag_name": "v2.0.0"}'
```

---

### 3. weekly-digest.yaml
**Converts:** Ecosystem activity → Weekly digest post

**When to use:** Every Monday (or on-demand) for regular ecosystem updates

**Inputs:**
- `date_range` - Optional (defaults to "last 7 days")
- `include_sessions` - Optional boolean (default: false)
- `repos` - Optional list (defaults to all from MODULES.md)

**Process:**
1. Scans all ecosystem repos for git activity
2. Analyzes sessions (if enabled)
3. Discovers community highlights
4. Determines top stories
5. Generates blog post, email, and social media content
6. Auto-opens blog post

**Runtime:** 3-4 minutes

**Example:**
```bash
# Standard weekly digest
amplifier tool invoke recipes operation=execute \
  recipe_path=amplifier-module-stories:recipes/weekly-digest.yaml

# Last 2 weeks
amplifier tool invoke recipes operation=execute \
  recipe_path=amplifier-module-stories:recipes/weekly-digest.yaml \
  context='{"date_range": "last 14 days"}'
```

**Automation:**
```cron
# Every Monday at 9am
0 9 * * 1 cd ~/dev/amplifier-module-stories && amplifier tool invoke recipes operation=execute recipe_path=./recipes/weekly-digest.yaml
```

---

### 4. blog-post-generator.yaml
**Converts:** Feature development data → Blog post + social media

**When to use:** Announcing features, sharing technical insights, or community engagement

**Inputs:**
- `feature_name` - Feature to write about (required)
- `pr_number` - Optional PR number for specific PR focus
- `include_technical_appendix` - Optional boolean (default: false)
- `target_audience` - Optional: "technical", "community", or "mixed" (default: "community")

**Process:**
1. Researches feature from git history
2. Plans content structure and audience focus
3. Generates blog post (Markdown)
4. Creates social media variants
5. Optionally creates technical appendix (Word)
6. Auto-opens blog post

**Runtime:** 2.5-5 minutes (longer with technical appendix)

**Example:**
```bash
# Community-focused blog post
amplifier tool invoke recipes operation=execute \
  recipe_path=amplifier-module-stories:recipes/blog-post-generator.yaml \
  context='{"feature_name": "shadow environments"}'

# Technical deep-dive with appendix
amplifier tool invoke recipes operation=execute \
  recipe_path=amplifier-module-stories:recipes/blog-post-generator.yaml \
  context='{"feature_name": "recipe workflows", "include_technical_appendix": true, "target_audience": "technical"}'
```

---

## The 5 Story Archetypes

Templates for consistent narrative structure across all content.

### 1. Problem/Solution/Impact
**File:** `context/archetypes/problem-solution-impact.md`

**When:** Feature launches, improvements, bug fixes  
**Structure:** Pain point → How we solved it → Results  
**Best for:** Most common story type

### 2. Feature Journey
**File:** `context/archetypes/feature-journey.md`

**When:** Complex features with interesting development stories  
**Structure:** Starting point → Explorations → Breakthrough → Reflection  
**Best for:** Stories where the "how we got there" is valuable

### 3. Technical Deep-Dive
**File:** `context/archetypes/technical-deep-dive.md`

**When:** Developers need deep understanding of implementation  
**Structure:** Context → Architecture → Implementation → Performance → Testing  
**Best for:** Complex systems, architectural decisions

### 4. Community Showcase
**File:** `context/archetypes/community-showcase.md`

**When:** Highlighting community projects and contributions  
**Structure:** The builder → Their approach → Results → Takeaways  
**Best for:** Celebrating user achievements

### 5. Velocity & Metrics
**File:** `context/archetypes/velocity-metrics.md`

**When:** Data-driven reports and metrics storytelling  
**Structure:** Context → Numbers → Analysis → Implications  
**Best for:** Quarterly reports, weekly digests (metrics section)

---

## Templates Reference

### PowerPoint (7 slide templates)
Located in `workspace/pptx/templates/`:
- **slide-title.html** - Centered title slides
- **slide-content.html** - Standard content with bullets
- **slide-code.html** - Code examples with green syntax
- **slide-comparison.html** - Before/After layouts
- **slide-metrics.html** - Big gradient numbers grid
- **slide-cards.html** - Feature cards
- **slide-section.html** - Section dividers
- **slide-big-number.html** - Single large metric

**Style:** Black backgrounds, blue accents, white text

### Excel (3 Python templates)
Located in `workspace/xlsx/templates/`:
- **dashboard-template.py** - Complete dashboard with metrics
- **metrics-template.py** - Trend tracking with formulas
- **comparison-template.py** - Before/after tables

**Style:** Blue accents, clean data presentation, formula-driven

### Word (3 JavaScript templates)
Located in `workspace/docx/templates/`:
- **technical-doc-template.js** - Technical docs with TOC
- **proposal-template.js** - Feature proposals
- **case-study-template.js** - Narrative case studies

**Style:** Clean hierarchy, blue titles, professional formatting

### PDF (1 Python template)
Located in `workspace/pdf/templates/`:
- **one-pager-template.py** - Executive summaries

**Style:** Blue headlines, metrics grid, single page

---

## Workflow Patterns

### Pattern 1: Manual Content Creation

For one-off content needs:

```
1. Ask storyteller: "Create a PowerPoint about X"
2. Storyteller uses templates automatically
3. File created, validated, auto-opened
4. Review and approve
5. Copy to docs/ for deployment
```

### Pattern 2: Session-Driven Storytelling

For capturing breakthrough work:

```
1. Complete a valuable Amplifier session
2. Run session-to-case-study recipe with events.jsonl
3. Case study auto-generated and opened
4. Review for accuracy
5. Publish or share
```

### Pattern 3: Release Automation

For every release:

```
1. Create git tag: git tag v2.0.0
2. Run git-tag-to-changelog recipe
3. Complete release docs generated
4. PR opened with CHANGELOG, release notes, announcements
5. Review PR and merge
6. Publish release on GitHub
```

### Pattern 4: Regular Communication

For ecosystem updates:

```
1. Schedule weekly-digest recipe (cron or GitHub Actions)
2. Every Monday, digest auto-generates
3. Blog post, email, and social media content ready
4. Review and publish
5. Zero manual work
```

### Pattern 5: Feature Launch Campaign

For major features:

```
1. story-researcher gathers feature data
2. content-strategist plans multi-format campaign
3. Parallel creation:
   - technical-writer creates deep docs
   - marketing-writer creates blog post
   - executive-briefer creates one-pager
4. content-adapter creates additional format variations
5. Coordinated launch across channels
```

---

## Agent Coordination Patterns

### Sequential (Recipe-Driven)
Agents work in sequence, passing results:
```
story-researcher → content-strategist → technical-writer → auto-open
```

Used in all 4 automated recipes.

### Parallel (Manual Delegation)
Create multiple outputs simultaneously:
```
"Create a blog post AND a PowerPoint AND an executive PDF about shadow environments"
```

Storyteller delegates to multiple agents in parallel.

### Adaptive (Content Transformation)
Start with one format, adapt to others:
```
1. "Create a PowerPoint about X" (technical-writer)
2. "Adapt that PowerPoint for executives" (content-adapter → executive-briefer)
3. "Turn it into a blog post" (content-adapter → marketing-writer)
```

---

## File Organization

```
amplifier-module-stories/
├── agents/                   # 10 specialist agents + storyteller
├── recipes/                  # 4 automated workflows
├── context/
│   ├── archetypes/          # 5 story narrative templates
│   ├── powerpoint-template.md
│   ├── presentation-styles.md
│   └── storyteller-instructions.md
├── workspace/               # Working directories
│   ├── pptx/               # PowerPoint creation
│   │   ├── templates/      # 8 HTML slide templates
│   │   ├── html-slides/    # Working HTML (gitignored)
│   │   ├── assets/         # Images (gitignored)
│   │   └── output/         # Final .pptx files
│   ├── xlsx/               # Excel creation
│   │   ├── templates/      # 3 Python templates
│   │   └── output/         # Final .xlsx files
│   ├── docx/               # Word creation
│   │   ├── templates/      # 3 JavaScript templates
│   │   └── output/         # Final .docx files
│   ├── pdf/                # PDF creation
│   │   ├── templates/      # 1 Python template
│   │   └── output/         # Final .pdf files
│   └── blog/               # Blog post creation
│       ├── posts/          # Blog posts
│       └── social/         # Social media content
├── docs/                    # Final deliverables
│   ├── *.html              # HTML presentations (14 existing)
│   └── blog/posts/         # Published blog posts
├── tools/                   # Development utilities
│   ├── analyze_sessions.py
│   ├── create_dashboard.py
│   └── README.md
├── tests/examples/          # Test examples for recipes
├── USAGE_GUIDE.md          # This file
├── IMPLEMENTATION_LOG.md   # Transformation progress log
└── README.md               # Overview and setup
```

---

## Testing Your Setup

### Verify Agents Are Loaded

```
"list available agents"
```

Should show all 11 agents (10 specialists + storyteller).

### Test Manual Content Creation

```
"Create a PowerPoint slide using the title template"
```

Should create a single slide, auto-open in PowerPoint.

### Test Recipe Execution

```bash
# Test with a real session
amplifier tool invoke recipes operation=execute \
  recipe_path=amplifier-module-stories:recipes/session-to-case-study.yaml \
  context='{"session_file": "~/.amplifier/sessions/LATEST/events.jsonl"}'
```

Should generate case study and auto-open.

### Verify Templates Are Available

```bash
# Check PowerPoint templates
ls workspace/pptx/templates/*.html

# Check Excel templates  
ls workspace/xlsx/templates/*.py

# Check Word templates
ls workspace/docx/templates/*.js

# Check PDF templates
ls workspace/pdf/templates/*.py
```

All templates should be present.

---

## Common Use Cases

### 1. Feature Launch
```
1. Run blog-post-generator for community post
2. Run git-tag-to-changelog if releasing
3. Create PowerPoint presentation (storyteller)
4. Create executive PDF (executive-briefer)
5. Coordinate launch timing
```

### 2. Weekly Communication
```
1. Every Monday: Run weekly-digest recipe
2. Review generated blog post and social content
3. Publish blog post to docs/blog/posts/
4. Post social media content
5. Share in community channels
```

### 3. Session Documentation
```
1. Complete a valuable session
2. Run session-to-case-study recipe
3. Review case study
4. Optionally adapt to blog post or presentation
5. Share or archive
```

### 4. Release Documentation
```
1. Create git tag: git tag v2.1.0
2. Run git-tag-to-changelog recipe
3. Review PR with generated docs
4. Merge PR
5. Publish GitHub release
6. Share announcements
```

### 5. Metrics Reporting
```
1. Gather data (sessions, git history)
2. Use data-analyst to create dashboard
3. Use executive-briefer for one-pager
4. Use technical-writer for detailed analysis
5. Present to stakeholders
```

---

## Troubleshooting

### Recipes Not Found
```bash
# Verify recipe exists
ls recipes/*.yaml

# Use full path
amplifier tool invoke recipes operation=execute \
  recipe_path=/Users/michaeljabbour/dev/amplifier-module-stories/recipes/weekly-digest.yaml
```

### Agents Not Loaded
```bash
# Restart Amplifier session
exit

# Verify bundle is active
grep "bundle:" ~/.amplifier/settings.yaml
```

### Templates Not Working
```bash
# Verify templates exist
ls workspace/*/templates/

# Check gitignore isn't hiding them
git check-ignore workspace/pptx/templates/*.html
```

### Auto-Open Not Working
```bash
# Verify 'open' command works
open workspace/pptx/output/test.pptx

# On Linux, may need 'xdg-open' instead
```

---

## Best Practices

### When to Use Manual vs Automated

**Use Manual (storyteller):**
- One-off content needs
- Custom presentations
- Exploratory content creation
- When you want direct control

**Use Automated (recipes):**
- Regular updates (weekly digests)
- Standard processes (release docs)
- High-volume needs (session case studies)
- When consistency matters

### Content Quality Standards

All content must:
- Use appropriate templates
- Follow Amplifier Keynote aesthetic (black/blue style)
- Include quantified metrics
- Provide code examples (tested)
- Have clear calls to action
- Be auto-opened for immediate review

### Template Modification

Templates can be customized but maintain:
- Black backgrounds (#000)
- Amplifier blue accents (#0A84FF)
- Professional typography
- `white-space: pre` in code blocks
- Consistent spacing

---

## Advanced Usage

### Custom Recipe Development

See `recipes/README.md` for recipe documentation.

Use `recipes:recipe-author` agent to create new recipes:
```
"Use recipe-author to create a recipe for monthly metrics reports"
```

### Template Customization

Templates are in `workspace/*/templates/` - modify as needed.

After modification, test thoroughly before committing.

### Integration with CI/CD

Recipes can be triggered by:
- Git hooks (post-commit, post-tag)
- GitHub Actions (on push, on schedule)
- Cron jobs (scheduled execution)

Example GitHub Action:
```yaml
name: Weekly Digest
on:
  schedule:
    - cron: '0 9 * * 1'
jobs:
  digest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Generate digest
        run: |
          amplifier tool invoke recipes operation=execute \
            recipe_path=./recipes/weekly-digest.yaml
```

---

## Getting Help

- **General questions:** See README.md
- **Recipe issues:** See recipes/README.md
- **Template usage:** See workspace/*/templates/README.md
- **Agent capabilities:** Read agent markdown files in agents/
- **Archetypes:** See context/archetypes/*.md
- **Test examples:** See tests/examples/*.md

---

**Last updated:** 2026-01-18  
**Version:** 2.0.0
