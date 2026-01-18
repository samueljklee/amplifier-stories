# Weekly Digest - Test Example

Test the automated weekly ecosystem digest generation recipe.

## Test Scenario

Generate a weekly digest covering the past 7 days of Amplifier ecosystem activity.

## Prerequisites

- Access to Amplifier ecosystem repos (github.com/microsoft/amplifier-*)
- GitHub CLI authenticated (`gh auth status`)
- Optional: Session data files (if testing with `include_sessions: true`)

## Expected Inputs

```json
{
  "date_range": "last 7 days"
}
```

Optional:
```json
{
  "date_range": "last 7 days",
  "include_sessions": true,
  "repos": ["microsoft/amplifier-core", "microsoft/amplifier-foundation"]
}
```

## Expected Outputs

### 1. Blog Post
**Location:** `workspace/blog/weekly-digest-2026-01-18.md`

**Structure:**
```markdown
---
title: "This Week in Amplifier - January 18, 2026"
date: 2026-01-18
tags: [weekly, digest, ecosystem]
---

# This Week in Amplifier 🚀

## Highlights

Top 3-5 stories from the week

## New Features

Features shipped with brief descriptions

## Community

Community contributions and discussions

## Stats

Ecosystem metrics for the week

## What's Next

Preview of upcoming work
```

### 2. Email Version
**Location:** `workspace/blog/weekly-digest-2026-01-18-email.md`

**Condensed version:** 400-600 words

### 3. Social Media Snippets
**Location:** `workspace/blog/weekly-digest-2026-01-18-social.md`

**Includes:**
- Twitter/X thread (6-8 tweets)
- LinkedIn post
- Discord/Teams announcement

### 4. Auto-Opened
Blog post opens in default markdown editor for review.

## Validation Criteria

✅ **Git activity captured**
- All ecosystem repos scanned
- Commits extracted and categorized
- PRs identified with titles
- New tags/releases found
- Contributors listed

✅ **Content quality**
- Top stories highlighted
- Stats are accurate
- Community highlights included
- Tone is engaging
- Call to action present

✅ **Multiple formats**
- Blog post complete
- Email version condensed appropriately
- Social media ready to post
- All saved to correct locations

✅ **Automation ready**
- Can be scheduled via cron
- Runs without manual intervention
- Handles weeks with little activity gracefully

## Manual Test Steps

```bash
# 1. Run the recipe
amplifier tool invoke recipes operation=execute \
  recipe_path=amplifier-module-stories:recipes/weekly-digest.yaml

# 2. Check outputs
ls -lh workspace/blog/

# 3. Review blog post (should auto-open)
# Check that it opened automatically
cat workspace/blog/weekly-digest-*.md

# 4. Review social media snippets
cat workspace/blog/weekly-digest-*-social.md

# 5. Verify stats accuracy
# Compare reported commit counts with actual:
gh search commits --repo microsoft/amplifier-core \
  --committer-date ">$(date -v-7d +%Y-%m-%d)" \
  --json sha | jq length
```

## Expected Runtime

- Git activity scan: 30-60 seconds (depends on repo count)
- Session analysis: 20-40 seconds (if enabled)
- Community highlights: 20-30 seconds
- Content strategy: 10-20 seconds
- Digest writing: 60-90 seconds
- **Total:** 2.5-4 minutes

## Success Indicators

- ✅ Digest covers all major ecosystem activity
- ✅ Top 3-5 stories featured prominently
- ✅ Stats match reality (verify sample counts)
- ✅ Ready to publish with minimal editing
- ✅ Social media content ready to post
- ✅ Email version appropriate length

## Automation Test

Can this be run automatically every Monday?

**Cron example:**
```cron
# Every Monday at 9am
0 9 * * 1 cd /path/to/amplifier-module-stories && amplifier tool invoke recipes operation=execute recipe_path=./recipes/weekly-digest.yaml
```

**GitHub Actions example:**
```yaml
name: Weekly Digest
on:
  schedule:
    - cron: '0 9 * * 1'  # Every Monday at 9am UTC
  workflow_dispatch:     # Manual trigger
jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Generate digest
        run: amplifier tool invoke recipes operation=execute recipe_path=./recipes/weekly-digest.yaml
```

## Edge Cases to Test

1. **Very quiet week** (< 5 commits)
   - Expected: Still generates digest, notes it was a quiet week

2. **Very active week** (100+ commits)
   - Expected: Summarizes appropriately, doesn't list all commits

3. **No PRs merged**
   - Expected: Focuses on commits and community activity

4. **First week of ecosystem** (no previous digest)
   - Expected: Works without comparison to previous week

## Integration Test

After digest is created:

```bash
# Can metrics be visualized?
amplifier run "create an Excel dashboard from the weekly digest stats"

# Can digest be presented?
amplifier run "create a PowerPoint from this week's digest"
```
