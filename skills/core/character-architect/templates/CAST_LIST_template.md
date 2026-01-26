# Cast List: {{SHOW_TITLE}}

**Version**: 1.0
**Created**: {{DATE}}

---

## Main Cast (Tier 1)

### {{PROTAGONIST_NAME}}
**Role**: Protagonist
**Archetype**: {{ARCHETYPE}}
**One-Line**: {{BRIEF_DESCRIPTION}}
**Key Relationship**: {{PRIMARY_RELATIONSHIP}}
**Sheet**: `CHARACTER_SHEETS/{{NAME}}.md`

### {{CHARACTER_2_NAME}}
**Role**: {{ROLE_IN_STORY}}
**Archetype**: {{ARCHETYPE}}
**One-Line**: {{BRIEF_DESCRIPTION}}
**Key Relationship**: {{PRIMARY_RELATIONSHIP}}
**Sheet**: `CHARACTER_SHEETS/{{NAME}}.md`

---

## Series Regulars (Tier 2)

### {{CHARACTER_NAME}}
**Role**: {{ROLE}}
**Archetype**: {{ARCHETYPE}}
**One-Line**: {{BRIEF_DESCRIPTION}}
**Sheet**: `CHARACTER_SHEETS/{{NAME}}.md`

---

## Recurring Characters (Tier 3)

### {{CHARACTER_NAME}}
**Role**: {{ROLE}}
**Episodes**: {{WHICH_EPISODES}}
**One-Line**: {{BRIEF_DESCRIPTION}}
**Sheet**: `CHARACTER_SHEETS/{{NAME}}.md` (if developed)

---

## Character Relationships Quick Reference

```
{{PROTAGONIST}}
    ├── [{{RELATIONSHIP_TYPE}}] → {{CHARACTER}}
    ├── [{{RELATIONSHIP_TYPE}}] → {{CHARACTER}}
    └── [{{RELATIONSHIP_TYPE}}] → {{CHARACTER}}

{{CHARACTER}}
    └── [{{RELATIONSHIP_TYPE}}] → {{CHARACTER}}
```

---

## Voice Differentiation Matrix

| Character | Sentence Length | Metaphor Domain | Directness | Sarcasm |
|-----------|-----------------|-----------------|------------|---------|
| {{NAME}} | {{VALUE}} | {{VALUE}} | {{1-10}} | {{1-10}} |
| {{NAME}} | {{VALUE}} | {{VALUE}} | {{1-10}} | {{1-10}} |
| {{NAME}} | {{VALUE}} | {{VALUE}} | {{1-10}} | {{1-10}} |

---

## Visual Quick Reference

| Character | Build | Hair | Signature Color | Key Visual Element |
|-----------|-------|------|-----------------|-------------------|
| {{NAME}} | {{VALUE}} | {{VALUE}} | {{COLOR}} | {{DISTINCTIVE_FEATURE}} |
| {{NAME}} | {{VALUE}} | {{VALUE}} | {{COLOR}} | {{DISTINCTIVE_FEATURE}} |

---

## Story Function Matrix

| Character | Causes Problems | Solves Problems | Comic Relief | Emotional Core |
|-----------|-----------------|-----------------|--------------|----------------|
| {{NAME}} | {{YES/NO}} | {{YES/NO}} | {{YES/NO}} | {{YES/NO}} |

---

## Files Generated

- `CHARACTER_SHEETS/{{NAME_1}}.md`
- `CHARACTER_SHEETS/{{NAME_2}}.md`
- `CHARACTER_SHEETS/{{NAME_3}}.md`
- `RELATIONSHIP_MAP.json`
- `CAST_LIST.md` (this file)
