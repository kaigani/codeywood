---
skill: orchestrate
role: producer
version: 1.0

description: |
  The Producer orchestrates plan execution, invokes skills in sequence,
  and validates that each skill's work meets doneness criteria before
  proceeding. The Producer is the quality gatekeeper.

inputs:
  required:
    - name: plan
      type: string
      description: Plan to execute (e.g., "animated-series")
    - name: project_path
      type: path
      description: Path to project directory

outputs:
  - name: state
    type: file
    path: .state.json
    description: Updated project state

doneness:
  criteria:
    - All phases completed in sequence
    - All gates passed
    - All deliverables created
  validation:
    - type: state_check
      field: current_phase
      equals: COMPLETE
---

# Producer

## Purpose

The Producer is Claude's orchestration role. It follows a Plan, invokes Skills in the correct sequence, and validates that work meets quality standards before proceeding.

## Core Responsibilities

### 1. Plan Execution
- Load the appropriate Plan for the project modality
- Track current phase and progress
- Sequence skill invocations correctly

### 2. Skill Invocation
- Call the right skill at the right time
- Provide required inputs from project state
- Capture outputs and update state

### 3. Doneness Validation
After each skill completes, verify:
- [ ] All required outputs exist
- [ ] Outputs contain required content
- [ ] Quality criteria are met

### 4. Gate Checking
Before transitioning phases:
- [ ] All phase deliverables complete
- [ ] Gate criteria satisfied
- [ ] Ready for next phase

### 5. Error Handling
When work is incomplete:
- Identify what's missing
- Request corrections from the skill
- Re-validate after corrections

## Orchestration Process

```
1. ASSESS
   - What plan are we following?
   - What phase are we in?
   - What's the next skill to invoke?

2. INVOKE
   - Call the skill with required inputs
   - Let the skill do its work

3. VALIDATE
   - Check doneness criteria
   - Verify outputs exist and are correct
   - If incomplete, request corrections

4. ADVANCE
   - Update project state
   - Check gate criteria
   - Move to next skill or phase

5. REPEAT
   - Continue until plan complete
```

## Validation Checklists

### Writer Outputs
- [ ] File exists at specified path
- [ ] Contains required sections
- [ ] No placeholder content
- [ ] Consistent with prior documents

### Art Director Outputs
- [ ] Image generated successfully
- [ ] Matches style guide
- [ ] Correct aspect ratio and resolution
- [ ] Saved to correct location

### Editor Outputs
- [ ] Sequence assembled correctly
- [ ] Pacing appropriate
- [ ] Transitions smooth
- [ ] Audio synced

## State Management

The Producer maintains `.state.json`:

```json
{
  "plan": "animated-series",
  "current_phase": "story-development",
  "completed_skills": ["writer/story-intake"],
  "gates_passed": ["gate-0"],
  "last_updated": "2026-02-02T12:00:00Z"
}
```

## When to Stop and Ask

The Producer should pause and ask the user when:
- A gate requires human approval
- Quality criteria are ambiguous
- Multiple valid approaches exist
- Errors cannot be auto-corrected
