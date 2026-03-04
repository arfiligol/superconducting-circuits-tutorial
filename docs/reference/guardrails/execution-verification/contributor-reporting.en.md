---
aliases:
  - "Contributor Agent Reporting Format"
  - "Contributor Reporting"
tags:
  - audience/team
  - sot/true
status: stable
owner: docs-team
audience: team
scope: "Standard contributor handoff format that humans can read and integrators can parse quickly"
version: v1.0.0
last_updated: 2026-03-04
updated_by: docs-team
---

# Contributor Agent Reporting Format

Defines a standard contributor report structure that is both human-readable and easy for an Integrator Agent to consume.

!!! important "Goal"
    Reports must satisfy both:
    1) Human stakeholders can quickly understand outcomes and risks  
    2) Integrator Agent can directly extract commits/files/tests/risks

## Required Template

```markdown
## Contributor Report v1

### 0) Task Info
- Agent: <name>
- Task ID / Topic: <id-or-title>
- Branch / Worktree: <branch-or-path>
- Scope (Allowed Files): <summary>
- Status: <done|blocked|needs-integrator>

### 1) Summary
- Goal: <what was requested>
- Outcome: <what is now true>

### 2) Preflight and Boundary Compliance
- Initial `git status --porcelain`: <clean|dirty + note>
- Cross-scope requirement encountered: <no|yes + reason>
- Cross-scope handling: <n/a|handoff-to-integrator>

### 3) Changes
- Commit(s):
  - `<hash>` `<message>`
  - `<hash>` `<message>`
- Changed Files:
  - `<path>`: <why changed>
  - `<path>`: <why changed>

### 4) Documentation Updates (if any)
- `<path>`: <contract/spec change>

### 5) Test Results
- Commands:
  - `<command>`
  - `<command>`
- Results:
  - `<pass/fail + key output>`

### 6) Playwright / E2E (if required)
- Scenarios:
  - <scenario-1>
  - <scenario-2>
- Evidence:
  - `<screenshot-abs-path>`
  - `<log-or-report-abs-path>`
- Result: <pass/fail>

### 7) Known Risks / Limitations
- <risk-1>
- <risk-2>

### 8) Integrator Decisions Needed (if any)
- <decision-needed-1>
- <decision-needed-2>

### 9) Rollback Info
- Recommended rollback commit: `<hash>` (if needed)
```

## Required Fields

- Mandatory: `Commit(s)`, `Changed Files`, `Test Results`, `Known Risks`
- If Playwright is required: `Scenarios` + `Evidence` + `Result` are mandatory
- `Changed Files` must include reason per file, not paths only

## Readability Rules

- Lead with conclusions, then evidence
- Do not dump long raw logs; provide command + result summary + evidence paths
- Explicitly distinguish:
  - **Completed**
  - **Verified**
  - **Needs Integrator Decision**

---

## Agent Rule { #agent-rule }

```markdown
## Contributor Reporting Format
- Contributors MUST use `Contributor Report v1` structure for handoff.
- Mandatory sections:
    - Task info
    - Commit hashes
    - Changed files with reason
    - Test commands and results
    - Known risks
- If Playwright is required:
    - MUST include scenarios, evidence paths, and pass/fail result.
- Reporting quality rules:
    - Lead with conclusion, then evidence.
    - Summarize logs; do not dump long raw logs.
    - Explicitly separate completed work vs verified work vs items needing integrator decision.
```
