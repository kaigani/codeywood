# Contributing to AI Video Story Generation

Thank you for your interest in contributing to this project! This document provides guidelines for contributing to the skill library and development process.

## Project Philosophy

1. **Skills are instruction sets** - Claude reads and follows them, not autonomous agents
2. **Incremental development** - Build and test one skill at a time
3. **Quality gates** - Each phase must pass validation before proceeding
4. **Community-driven** - Share what works, iterate openly

## How to Contribute

### 1. Testing Existing Skills

The most valuable contribution is testing skills and reporting results:

1. Use a skill with your own project
2. Document what worked and what didn't
3. Suggest improvements with specific examples
4. Share successful outputs (anonymized if needed)

### 2. Improving Skills

When improving a skill:

1. **Understand the current version** - Read the SKILL.md thoroughly
2. **Identify specific issues** - Be precise about what's not working
3. **Propose targeted fixes** - Small, focused improvements are easier to validate
4. **Include examples** - Show before/after when possible
5. **Test your changes** - Run the skill with the modifications

### 3. Adding New Skills

New skills should:

1. **Fill a clear gap** - What's missing from current workflow?
2. **Follow existing patterns** - Use established templates and structure
3. **Have clear inputs/outputs** - What does it need? What does it produce?
4. **Include examples** - Demonstrate expected behavior
5. **Document dependencies** - What must exist before this skill runs?

### 4. Improving Documentation

Documentation improvements are always welcome:

- Clarify confusing sections
- Add examples
- Fix errors
- Improve formatting

## Skill Structure

Every skill should follow this structure:

```
skills/{category}/{skill-name}/
├── SKILL.md           # Main skill instructions
├── templates/         # Output templates
│   └── *.md or *.json
├── prompts/           # AI prompt templates (if applicable)
│   └── *.txt
├── examples/          # Example inputs/outputs
│   └── */
└── config/            # Configuration files (if applicable)
    └── *.json
```

### SKILL.md Format

```markdown
# Skill Name

## Purpose
[One paragraph explaining what this skill does]

## Trigger
[When should this skill be invoked?]

## Inputs Required
[List of required inputs with file paths]

## Outputs Produced
[List of outputs with file paths]

## Process
[Step-by-step instructions]

## Quality Gate (if applicable)
[Pass/fail criteria]

## Notes
[Additional guidance]
```

## Code of Conduct

- Be respectful and constructive
- Focus on the work, not the person
- Share knowledge openly
- Credit contributions appropriately

## Pull Request Process

1. **Fork the repository**
2. **Create a feature branch** (`feature/improve-character-architect`)
3. **Make your changes**
4. **Test thoroughly**
5. **Submit PR with clear description**
6. **Respond to feedback**

### PR Description Template

```markdown
## What does this PR do?
[Brief description]

## Why is this change needed?
[Problem being solved]

## How was this tested?
[Testing methodology]

## Example output
[If applicable, show results]

## Checklist
- [ ] Follows existing skill structure
- [ ] Includes relevant templates
- [ ] Examples provided
- [ ] Documentation updated
```

## Reporting Issues

When reporting issues:

1. **Describe the problem clearly**
2. **Include relevant context** (which skill, what inputs)
3. **Show expected vs. actual behavior**
4. **Suggest potential solutions** (if you have ideas)

## Development Priorities

Current focus areas (in order):

1. **Phase 1 Skills (v0.1)** - Story foundation
2. **Phase 2 Skills (v0.2)** - Visual development
3. **Testing & Validation** - Prove skills work
4. **Documentation** - Clear instructions
5. **Examples** - Real-world demonstrations

## Questions?

- Open an issue for discussion
- Reference existing skills for patterns
- Start small and iterate

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for helping build the future of AI-assisted storytelling!
