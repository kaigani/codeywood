# SKILLS

Skills are role-based capabilities that define expertise, quality standards, and doneness criteria. Each skill belongs to a role and can be invoked by the Producer during plan execution.

## Role Directory

| Role | Responsibility |
|------|----------------|
| [producer](./producer/) | Orchestration, quality validation, milestone tracking |
| [writer](./writer/) | Story development, scripts, dialogue |
| [art-director](./art-director/) | Visual style, character design, location design |
| [editor](./editor/) | Shot assembly, pacing, continuity |
| [sound-designer](./sound-designer/) | Music, sound effects, audio mixing |

## Skill Definition Format

Each skill is defined in a `SKILL.md` file:

```yaml
---
skill: skill-name
role: writer | art-director | editor | sound-designer
version: 1.0

description: |
  One paragraph describing what this skill does and when to use it.

inputs:
  required:
    - name: input_name
      type: file | string | object
      description: What this input is
  optional:
    - name: optional_input
      type: string
      default: "default value"
      description: Optional parameter

outputs:
  - name: output_name
    type: file
    path: STORY/{filename}.md
    description: What this output contains

doneness:
  criteria:
    - Description of criterion 1
    - Description of criterion 2
  validation:
    - type: file_exists
      path: STORY/{filename}.md
    - type: content_check
      path: STORY/{filename}.md
      contains: "## Required Section"

dependencies:
  skills:
    - writer/story-intake  # Must run before this skill
  files:
    - STORY/CREATIVE_BRIEF.md
---

# {Skill Name}

## Purpose
{Detailed description of this skill's purpose and expertise}

## Process
1. Step one
2. Step two
3. Step three

## Quality Standards
- Standard 1
- Standard 2

## Examples
{Example inputs and outputs}
```

## Producer Role

The **Producer** is special - it orchestrates all other skills and validates doneness:

```
producer/
├── SKILL.md              # Orchestration methodology
├── orchestrate.md        # How to sequence skills
├── validate.md           # How to check doneness
└── checklists/           # Role-specific quality checklists
    ├── writer.yaml
    ├── art-director.yaml
    └── editor.yaml
```

### Producer Responsibilities

1. **Plan Execution** - Follow the plan's phase sequence
2. **Skill Invocation** - Call the right skill at the right time
3. **Doneness Validation** - Check each skill's doneness criteria
4. **Gate Checking** - Validate gate criteria before phase transitions
5. **Error Handling** - Handle failures and request corrections

## Doneness Criteria

Every skill must define clear doneness criteria:

| Type | Description | Example |
|------|-------------|---------|
| `file_exists` | Output file was created | `STORY/LOGLINE_LOCK.md exists` |
| `content_check` | File contains required content | `Contains "## Protagonist"` |
| `quality_score` | Meets minimum quality threshold | `Critique score >= 70` |
| `human_approval` | Requires human sign-off | `Style guide approved by user` |

## Migration from Legacy Skills

Legacy skills in `/skills/` are being migrated to this role-based structure:

| Legacy Skill | New Location |
|--------------|--------------|
| story-intake | writer/story-intake |
| logline-architect | writer/logline-development |
| character-architect | writer/character-creation |
| screenplay-writer | writer/screenplay |
| visual-style-guide | art-director/style-guide |
| character-reference-generator | art-director/character-design |
