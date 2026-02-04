# Production Bible Skill

```yaml
skill: production-bible
role: production
version: 1.0
description: Generate and maintain a comprehensive visual production bible for a project, consolidating story, character, and visual reference information into a browsable HTML interface.

inputs:
  required:
    - PROJECT_CONFIG.yaml  # Style DNA, characters, visual settings
    - .state.json          # Current pipeline state
    - STORY/CHARACTER_SHEETS/*.md  # Character definitions
  optional:
    - STORY/CREATIVE_BRIEF.md
    - STORY/LOGLINE_LOCK.md
    - STORY/EPISODE_STRUCTURE.md
    - STORY/POWER_STACK.md
    - STORY/WRITERS_ROOM/STORY_LOCK.md
    - STORY/SCRIPTS/*.md
    - EXPORTS/hero_shots/
    - EXPORTS/identity_sheets/
    - EXPORTS/character_refs/
    - EXPORTS/location_refs/

outputs:
  - VISUAL_PRODUCTION/PRODUCTION_BIBLE/index.html     # Dashboard
  - VISUAL_PRODUCTION/PRODUCTION_BIBLE/story.html    # Story overview
  - VISUAL_PRODUCTION/PRODUCTION_BIBLE/visual.html   # Visual references
  - VISUAL_PRODUCTION/PRODUCTION_BIBLE/status.html   # Production status
  - VISUAL_PRODUCTION/PRODUCTION_BIBLE/style.css     # Shared styles
  - VISUAL_PRODUCTION/PRODUCTION_BIBLE/script.js     # Interactions

doneness:
  criteria:
    - All four HTML pages render correctly
    - Navigation between pages works
    - Character cards display with available reference images
    - Progress bars reflect actual gate/phase status
    - Episode grid shows correct status per episode
    - Checklist items reflect actual artifact completion
    - Style DNA displays complete color palette
    - Mobile responsive layout functions
  validation:
    - Open index.html in browser, verify no console errors
    - Test all nav links between pages
    - Verify images load from relative paths
    - Test sidebar toggle on mobile width

dependencies:
  skills: []
  files:
    - At minimum PROJECT_CONFIG.yaml and one character sheet
```

## Purpose

The Production Bible serves as the single source of truth for visual production, consolidating:
- Story foundation (logline, theme, characters, episodes)
- Visual references (style guide, character refs, location refs)
- Production status (gates passed, artifacts generated, queue)
- Quality gates and approval tracking

It is designed to be:
1. **Browsable offline** - Static HTML files with relative paths
2. **Printable** - Clean print styles for physical reference
3. **Updatable** - Regenerated when project state changes
4. **Visual-first** - Images and galleries, not walls of text

## Structure

### index.html (Dashboard)
- Project title and logline
- Stats row (characters, episodes, images, scenes)
- Progress bars for each production phase
- Character cards at-a-glance with images
- Next steps checklist

### story.html (Story Overview)
- Creative brief (logline, genre, tone, comps)
- Character sheets with full psychology
- Episode grid with status
- Relationship map with axis visualization

### visual.html (Visual Production)
- Style guide with color palette swatches
- Style reference images
- Character reference galleries (turnarounds, signatures, expressions)
- Location reference galleries
- Generation prompt documentation (collapsible)

### status.html (Production Status)
- Phase progress with detailed checklists
- Artifact inventory table
- Generation queue with priorities
- Locked references section
- Quality gates checklist
- Generation log

## Execution

### Step 1: Read Project State

Read and parse the following files:
- `PROJECT_CONFIG.yaml` - Extract style DNA, character definitions, model preferences
- `.state.json` - Extract current phase, gates passed, skills completed
- Character sheets from `STORY/CHARACTER_SHEETS/`
- Episode structure from `STORY/EPISODE_STRUCTURE.md` if present

### Step 2: Inventory Visual Assets

Scan the `EXPORTS/` directory for:
- Hero shots in `hero_shots/{character}/`
- Identity sheets in `identity_sheets/`
- Character refs in `character_refs/{character}/`
- Location refs in `location_refs/`

**CRITICAL**: For each asset type, find the MOST RECENT file by timestamp:
- Pattern: `{slug}_{type}_{model}_{YYYYMMDD_HHMMSS}.png`
- Sort by modification time or parse timestamp from filename
- Use most recent version for all pages

Build a manifest mapping each character/location to their latest asset paths.

**Verify completeness**: Cross-reference manifest against `PROJECT_CONFIG.yaml`:
- Every character in `config.characters` should have identity sheet
- Every location in `config.locations` should have location ref
- Flag any missing assets for status.html queue

### Step 3: Generate HTML Files

Create the four HTML files using the Codeywood production bible template:
- Replace project-specific content (title, logline, characters)
- Update navigation status indicators based on completion
- Populate character cards with available images
- Fill progress bars based on gate status
- Build episode grid from structure file
- Generate checklist items from artifact inventory

**Character data sourcing** (in order of priority):
1. `PROJECT_CONFIG.yaml` - Visual keywords, wardrobe, palette (AUTHORITATIVE)
2. `STORY/CHARACTER_SHEETS/*.md` - Psychology, backstory, relationships
3. Never use stale descriptions from previous bible generation

**Ensure cross-page consistency**:
- Character visual profile in `story.html` must match `visual.html` card-meta
- Both must reflect current `PROJECT_CONFIG.yaml` visual_keywords
- Generate ALL pages in single pass to prevent drift

### Step 4: Copy Static Assets

Copy `style.css` and `script.js` from template or previous project bible.
These provide:
- Pixel art aesthetic matching docs site
- Lightbox gallery functionality
- Collapsible sections
- Mobile sidebar toggle
- Print styles

### Step 5: Validate Output

- Verify all relative image paths resolve
- Check that navigation links work
- Confirm progress percentages match actual state
- Test mobile responsive layout

## Template Components

### Character Card HTML
```html
<div class="character-card">
    <div class="character-card-image">
        <img src="../{path_to_image}" alt="{name}">
    </div>
    <div class="character-card-body">
        <h3>{Name}</h3>
        <div class="character-role">{Role}</div>
        <p class="character-description">{One-paragraph description}</p>
        <div class="character-card-footer">
            <span class="tag tag-character">Tier {n}</span>
            <span class="tag tag-production">{status}</span>
        </div>
    </div>
</div>
```

### Progress Bar HTML
```html
<div class="progress-card">
    <h3>{Phase Name}</h3>
    <div class="progress-bar-container">
        <div class="progress-bar">
            <div class="progress-fill" style="width: {percent}%"></div>
        </div>
        <span class="progress-percent">{percent}%</span>
    </div>
    <div class="progress-details">{description}</div>
</div>
```

### Episode Row HTML
```html
<tr>
    <td>{number}</td>
    <td>{title}</td>
    <td>{focus}</td>
    <td>{arc}</td>
    <td><span class="status-badge {status}">{STATUS_LABEL}</span></td>
</tr>
```

### Checklist Item HTML
```html
<li class="{done|wip|pending}">{description}</li>
```

## Status Mapping

| State | CSS Class | Badge Color |
|-------|-----------|-------------|
| Complete | `done` / `complete` | Green |
| In Progress | `wip` / `progress` | Gold |
| Pending | `pending` | Gray |
| Blocked | `blocked` | Red |

## Progress Calculation

### Story Foundation Progress
Count completed items from:
- Creative Brief (10%)
- Logline Lock (10%)
- Cast List (5%)
- Power Stack (5%)
- Character Sheets (20% total, divided by character count)
- Season Grid (10%)
- Episode Beats (20% total, divided by episode count)
- Scene Lists (10%)
- Screenplays (10%)

### Visual References Progress
- Style Master (20%)
- Character Turnarounds (30% total, divided by character count)
- Character Signatures (20% total, divided by character count)
- Location Refs (30% total, divided by location count)

### Shot Production Progress
- Storyboard Grids (50% total)
- Action Sequences (20%)
- Individual Shots (30%)

## Update Triggers

Regenerate the production bible when:
1. A gate status changes in `.state.json`
2. New visual assets are generated in `EXPORTS/`
3. Character sheets are updated
4. Episode structure changes
5. User explicitly requests update

## Quality Criteria

A production bible is complete when:
- [ ] All available data is represented
- [ ] All available images are displayed
- [ ] Progress percentages are accurate
- [ ] Navigation functions correctly
- [ ] Print view is usable
- [ ] No broken image links
- [ ] Mobile layout is functional

## Example Invocation

```
Given a project at projects/my-show/:
1. Read PROJECT_CONFIG.yaml, .state.json, character sheets
2. Scan EXPORTS/ for generated images
3. Generate VISUAL_PRODUCTION/PRODUCTION_BIBLE/index.html
4. Generate story.html, visual.html, status.html
5. Copy style.css and script.js
6. Validate all pages load correctly
```

## Common Issues & Prevention

### Issue: Character descriptions out of sync between pages
**Problem**: `story.html` and `visual.html` can have different descriptions for the same character.
**Prevention**:
- Always pull character visual keywords from `PROJECT_CONFIG.yaml` as the single source of truth
- When updating one page, verify the other page has matching descriptions
- Character sheet `.md` files may be stale - config is authoritative for visual keywords

### Issue: Placeholder images instead of actual assets
**Problem**: Character sections show "PENDING" placeholders when identity sheets exist.
**Prevention**:
- Scan `EXPORTS/identity_sheets/` for ALL characters before generating
- Use glob pattern `{character_slug}*identity*.png` to find latest image
- Never generate pages until inventory step confirms available assets
- If asset missing, note in status.html queue - don't use placeholder in story.html

### Issue: Image paths with hardcoded timestamps break on regeneration
**Problem**: Images are saved with timestamps (e.g., `_20260203_131447.png`), so paths break when regenerated.
**Prevention**:
- Always scan for most recent file matching pattern: `{slug}_*_{model}_*.png`
- Sort by modification time, use most recent
- Store relative paths at generation time, not hardcoded filenames

### Issue: Navigation status indicators don't match actual state
**Problem**: Nav shows "pending" for Location Refs when locations are complete.
**Prevention**:
- Calculate nav status dynamically from asset inventory
- `complete` = all expected assets present
- `progress` = some assets present
- `pending` = no assets present
- Update ALL pages' nav sections together (they share sidebar markup)

### Issue: Cross-page updates missed
**Problem**: Updating `visual.html` character refs but forgetting `story.html` character sheets.
**Prevention**:
- When regenerating, ALWAYS regenerate all four HTML files together
- Character data appears in: index.html (cards), story.html (sheets), visual.html (refs)
- Treat the bible as atomic - partial updates cause inconsistency

### Checklist Before Completing Bible Generation
- [ ] All tier 1 characters have identity sheets displayed (no placeholders)
- [ ] Character visual descriptions match PROJECT_CONFIG.yaml in ALL pages
- [ ] All nav status indicators reflect actual asset state
- [ ] Image paths resolve (test by opening in browser)
- [ ] story.html and visual.html character sections are consistent
- [ ] Generation date is current in all page headers

## Notes

- Image paths should be relative to the PRODUCTION_BIBLE directory
- Use `../` to navigate up to VISUAL_PRODUCTION, then to EXPORTS
- The bible is a snapshot - it reflects state at generation time
- Regeneration overwrites all HTML files but preserves custom CSS modifications
- The production bible should NOT be manually edited for content - edit source files instead
- **PROJECT_CONFIG.yaml is the source of truth for character visual keywords** - not character sheet markdown files
