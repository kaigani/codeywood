# Skill: Production Bible Generator

## Purpose

Generate a comprehensive static website that documents the current state of production. This "Production Bible" serves as a shareable snapshot for collaborators, stakeholders, and review - showing all story artifacts, character designs, location references, and visual assets in an organized, browsable format.

## Trigger

Invoke this skill when:
- You want to share current progress with collaborators
- Before a review meeting or milestone check
- To create a backup/archive of production state
- At any point to assess what's complete vs. pending

## Inputs Required

The skill scans the project directory and collects:

### Story Foundation (Phase 1)
- `CREATIVE_BRIEF.md` - Project overview and vision
- `POWER_STACK.md` - Story structure framework
- `LOGLINE_LOCK.md` - Locked logline
- `CAST_LIST.md` - Character roster
- `CHARACTER_SHEETS/*.md` - Individual character profiles
- `RELATIONSHIP_MAP.json` - Character relationships
- `SEASON_GRID.md` - Episode overview
- `EP*_BEATS.md` - Episode beat sheets
- `EP*_SCENELIST.md` - Scene breakdowns

### Visual Production (Phase 2)
- `VISUAL_PRODUCTION/STYLE_GUIDE/results/*.png` - Style references
- `VISUAL_PRODUCTION/CHARACTER_REFS/*/results/*.png` - Character art
- `VISUAL_PRODUCTION/LOCATION_REFS/*/results/*.png` - Location art
- `VISUAL_PRODUCTION/STORYBOARDS/*/results/*.png` - Storyboard grids
- `VISUAL_PRODUCTION/ACTION_SEQUENCES/*/results/*.png` - Action sequences

### Production Tracking
- `VISUAL_PRODUCTION/GENERATION_QUEUE.md` - Pending generations
- `VISUAL_PRODUCTION/WORKFLOW.md` - Production workflow

## Outputs Produced

```
PROJECT_ROOT/
└── PRODUCTION_BIBLE/
    ├── index.html              # Main entry point
    ├── style.css               # Styling
    ├── script.js               # Gallery interactions
    ├── story/
    │   ├── index.html          # Story overview
    │   ├── characters.html     # Character profiles
    │   ├── episodes.html       # Episode breakdowns
    │   └── relationships.html  # Relationship map
    ├── visual/
    │   ├── index.html          # Visual overview
    │   ├── style-guide.html    # Style references
    │   ├── characters.html     # Character gallery
    │   └── locations.html      # Location gallery
    ├── assets/
    │   └── images/             # Copied/linked images
    └── status.html             # Production status dashboard
```

## Process

### Step 1: Scan Project Structure

Inventory all existing artifacts:

```
For each expected file/folder:
  - Check if exists
  - Note version/date if available
  - Mark status: COMPLETE / IN_PROGRESS / PENDING
```

### Step 2: Extract Content

For each markdown file found:
- Parse frontmatter/metadata
- Extract key sections
- Convert to HTML

For each image folder:
- List all images with metadata
- Generate thumbnail references
- Note naming convention compliance

### Step 3: Generate Site Structure

Create the output folder structure:

```bash
mkdir -p PRODUCTION_BIBLE/{story,visual,assets/images}
```

### Step 4: Generate Index Page

The main `index.html` should include:
- Project title and logline
- Production status overview (progress bars)
- Quick links to all sections
- Last updated timestamp
- Key stats (characters, episodes, images generated)

### Step 5: Generate Story Section

**story/index.html** - Overview with:
- Creative brief summary
- Logline
- Theme and tone
- Links to detailed pages

**story/characters.html** - For each character:
- Name and role
- One-line description
- Visual profile summary
- Key relationships
- Link to full character sheet

**story/episodes.html** - For each episode:
- Episode number and title
- Logline
- Beat summary
- Scene count
- Status indicator

**story/relationships.html** - Visual relationship map:
- Character nodes
- Relationship lines with labels
- Starting vs. current axis values

### Step 6: Generate Visual Section

**visual/index.html** - Overview with:
- Style guide status
- Character count with images
- Location count with images
- Production queue status

**visual/style-guide.html** - Gallery with:
- Master style reference
- Style keywords
- Color palette
- Do's and don'ts

**visual/characters.html** - For each character:
- Turnaround sheet
- Expression variants
- Action poses
- Signature images
- Gallery lightbox

**visual/locations.html** - For each location:
- Establishing shots
- Interior views
- Time/weather variants
- Gallery lightbox

### Step 7: Generate Status Dashboard

**status.html** - Production tracking:
- Phase completion percentages
- Checklist of all artifacts
- Generation queue status
- Timeline/milestones

### Step 8: Copy Assets

Copy or symlink all images to `assets/images/` with consistent naming:
```
assets/images/
├── style/
├── characters/
│   ├── nameless/
│   ├── minnie/
│   └── deacon/
└── locations/
```

### Step 9: Final Assembly

- Inject navigation into all pages
- Add consistent header/footer
- Generate table of contents
- Add print stylesheet
- Test all links

## Site Design Guidelines

### Visual Style
- Clean, professional documentation aesthetic
- Dark theme option (matches production aesthetic)
- Responsive for tablet/desktop viewing
- Image galleries with lightbox
- Collapsible sections for long content

### Navigation
- Persistent sidebar or top nav
- Breadcrumbs on all pages
- "Back to top" buttons
- Section jump links

### Status Indicators
- Green: Complete/Locked
- Yellow: In Progress
- Gray: Pending
- Red: Blocked/Issue

### Image Galleries
- Grid layout with thumbnails
- Click to expand (lightbox)
- Image metadata on hover
- Download original option

## Template Variables

The generator uses these variables:

```
{{PROJECT_NAME}} - From CREATIVE_BRIEF.md
{{LOGLINE}} - From LOGLINE_LOCK.md
{{GENERATED_DATE}} - Current timestamp
{{PHASE_1_PROGRESS}} - Percentage complete
{{PHASE_2_PROGRESS}} - Percentage complete
{{CHARACTER_COUNT}} - Number of characters
{{EPISODE_COUNT}} - Number of episodes
{{IMAGE_COUNT}} - Total images generated
```

## Example Output

### Index Page Header
```html
<header class="bible-header">
  <h1>{{PROJECT_NAME}}</h1>
  <p class="logline">{{LOGLINE}}</p>
  <div class="meta">
    <span>Generated: {{GENERATED_DATE}}</span>
    <span>{{CHARACTER_COUNT}} Characters</span>
    <span>{{EPISODE_COUNT}} Episodes</span>
    <span>{{IMAGE_COUNT}} Images</span>
  </div>
</header>
```

### Progress Dashboard
```html
<section class="progress-dashboard">
  <div class="progress-item">
    <label>Story Foundation</label>
    <div class="progress-bar">
      <div class="progress-fill" style="width: {{PHASE_1_PROGRESS}}%"></div>
    </div>
    <span>{{PHASE_1_PROGRESS}}%</span>
  </div>
  <div class="progress-item">
    <label>Visual Production</label>
    <div class="progress-bar">
      <div class="progress-fill" style="width: {{PHASE_2_PROGRESS}}%"></div>
    </div>
    <span>{{PHASE_2_PROGRESS}}%</span>
  </div>
</section>
```

### Character Gallery Card
```html
<div class="character-card">
  <div class="character-image">
    <img src="assets/images/characters/{{CHARACTER_ID}}/turnaround.png"
         alt="{{CHARACTER_NAME}} turnaround">
  </div>
  <div class="character-info">
    <h3>{{CHARACTER_NAME}}</h3>
    <p class="role">{{CHARACTER_ROLE}}</p>
    <p class="description">{{CHARACTER_ONE_LINER}}</p>
    <a href="story/characters.html#{{CHARACTER_ID}}">View Profile →</a>
  </div>
  <div class="character-gallery">
    {{#each CHARACTER_IMAGES}}
    <img src="{{this.path}}" alt="{{this.label}}" class="gallery-thumb">
    {{/each}}
  </div>
</div>
```

## Quality Checklist

Before sharing the production bible:

- [ ] All links work (no 404s)
- [ ] All images load correctly
- [ ] Navigation is consistent across pages
- [ ] Status indicators are accurate
- [ ] No placeholder text remains
- [ ] Responsive on tablet/desktop
- [ ] Print view is usable
- [ ] Generated date is current

## Notes

### Regeneration
- The bible can be regenerated at any time
- Previous versions are overwritten (archive manually if needed)
- Generation is fast - run frequently during active production

### Sharing
- The output folder is self-contained
- Can be zipped and emailed
- Can be hosted on GitHub Pages
- Can be viewed locally (file:// protocol works)

### Privacy
- Review for sensitive content before sharing
- Consider excluding WIP images if needed
- API keys/credentials should never appear

## Dependencies

- Markdown parser (for content extraction)
- File system access (for scanning)
- HTML templates (provided in /templates)
