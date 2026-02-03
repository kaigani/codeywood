# WORKFLOWS

Workflows are reusable execution patterns defined in YAML with Mermaid flow diagrams for visualization. They describe the logic of multi-step processes that can be executed by Claude or automated scripts.

## Philosophy

Workflows are **design patterns, not automation configs**. They document:
- The sequence of steps in a process
- Decision points and branching logic
- Inputs, outputs, and validation criteria
- Error handling strategies

Execution can be:
1. **Manual** - Claude follows the pattern step-by-step
2. **Scripted** - Python scripts in `/scripts/` implement the pattern
3. **Hybrid** - Claude orchestrates, scripts execute specific steps

## Directory Structure

```
WORKFLOWS/
├── patterns/                    # Reusable workflow patterns
│   ├── image-generation.md      # Generate images via FAL
│   ├── character-reference.md   # Full character ref pipeline
│   ├── gate-validation.md       # Quality gate checking
│   └── writers-room.md          # Multi-agent story development
└── README.md                    # This file
```

## Pattern Definition Format

Each pattern is a markdown file with YAML frontmatter and Mermaid diagrams:

```markdown
---
pattern: pattern-name
version: 1.0
description: What this pattern does

inputs:
  required:
    - name: prompt
      type: string
      description: The generation prompt
  optional:
    - name: aspect_ratio
      type: enum
      options: ["1:1", "2:3", "16:9"]
      default: "1:1"

outputs:
  - name: image_path
    type: file
    description: Path to generated image

execution:
  mode: script | manual | hybrid
  script: scripts/generate/fal_generate.py  # if scripted

error_handling:
  retry: 3
  fallback: log_and_continue | fail
---

# Pattern Name

## Purpose
What this pattern accomplishes and when to use it.

## Flow Diagram

\```mermaid
flowchart TD
    A[Start] --> B{Validate Inputs}
    B -->|Valid| C[Execute Step 1]
    B -->|Invalid| X[Return Error]
    C --> D[Execute Step 2]
    D --> E{Check Result}
    E -->|Success| F[Return Output]
    E -->|Failure| G{Retry?}
    G -->|Yes| C
    G -->|No| X
\```

## Steps

### Step 1: Validate Inputs
- Check required fields exist
- Validate types and ranges

### Step 2: Execute Core Logic
- Description of what happens
- Expected duration
- Possible errors

## Usage Examples

\```python
# Example invocation
result = execute_pattern("pattern-name", {
    "prompt": "A cursed pirate captain...",
    "aspect_ratio": "2:3"
})
\```

## Notes
- Important considerations
- Edge cases
```

## Available Patterns

| Pattern | Purpose | Execution Mode |
|---------|---------|----------------|
| [image-generation](./patterns/image-generation.md) | Generate images via FAL.ai | Script |
| [character-reference](./patterns/character-reference.md) | Full character ref pipeline | Hybrid |
| [gate-validation](./patterns/gate-validation.md) | Check quality gates | Manual |
| [writers-room](./patterns/writers-room.md) | Multi-agent story development | Manual |

## Execution

### Manual Execution (Claude)

Claude reads the pattern and executes each step, using tools as needed:
- Read files with `Read` tool
- Generate images by calling scripts via `Bash`
- Validate outputs against criteria

### Scripted Execution

Python scripts in `/scripts/` implement patterns directly:
```bash
python scripts/generate/fal_generate.py --prompt "..." --aspect-ratio 2:3
```

### Hybrid Execution

Claude orchestrates the overall flow, calling scripts for specific steps:
1. Claude validates inputs and prepares prompts
2. Claude calls generation script
3. Claude validates outputs against criteria
4. Claude decides next steps based on results

## Creating New Patterns

1. Identify a repeatable multi-step process
2. Define inputs, outputs, and validation criteria
3. Draw the flow diagram in Mermaid
4. Document each step with expected behavior
5. Specify execution mode and error handling
6. Add to the patterns directory
