---
aliases:
  - "Multiple Agent Collaboration"
  - "Multi-Agent Workflow"
tags:
  - audience/team
  - sot/true
status: stable
owner: docs-team
audience: team
scope: "Isolation, integration, and conflict-avoidance rules for local multi-agent collaboration"
version: v1.1.0
last_updated: 2026-03-05
updated_by: docs-team
---

# Multiple Agent Collaboration

Rules for safe parallel work when multiple local agents contribute to the same delivery stream.

!!! important "Single Integrator Rule (Mandatory)"
    One delivery stream (same topic/PR) must have exactly **one Integrator Agent** at a time.
    All other agents are contributors and must not perform cross-agent integration on their own.

## Roles

- **Integrator Agent**
  - The only role allowed to perform integration actions (cherry-pick, conflict resolution, final merge prep)
  - Owns final validation and regression summary
- **Contributor Agent**
  - Edits only assigned scope
  - Delivers atomic commits and handoff notes for integration

## Required Collaboration Flow

1. **Preflight**
   - Report `git status --porcelain` before editing.
   - If unrelated dirty changes exist, stop and report options instead of overwriting.

2. **Workspace Isolation**
   - MUST use one `git worktree` + one branch per agent/task.
   - Do not have multiple agents editing the same dirty worktree.

3. **File Ownership**
   - Every task must define `Allowed Files`.
   - If a needed change crosses boundaries, hand off to Integrator for re-assignment.

4. **Handoff**
   - Contributors must provide:
     - commit hashes
     - changed-file list
     - test results
     - known risks
   - Integrator performs final integration.

## Prohibited Actions

- Overwriting or reverting another agent's unintegrated work
- Destructive git cleanup in shared contexts (for example `git reset --hard`)
- Opportunistic edits outside assigned file scope

---

## Agent Rule { #agent-rule }

```markdown
## Multiple Agent Collaboration
- **Single Integrator (Mandatory)**:
    - One delivery line/PR MUST have exactly one Integrator Agent at a time.
    - Only Integrator may perform final integration (cherry-pick/conflict resolution/merge prep).
- **Contributor Boundaries**:
    - Contributors MUST edit only assigned files (`Allowed Files`).
    - If required changes exceed scope, stop and hand off to Integrator.
- **Preflight**:
    - Before editing, run `git status --porcelain`.
    - If unrelated dirty changes exist, do not proceed blindly; report and wait.
- **Isolation**:
    - MUST use one `git worktree` + one branch per agent/task.
    - Do not let multiple agents co-edit the same dirty worktree.
- **Handoff Required**:
    - Provide commit hashes, changed files, test results, and known risks.
- **Never**:
    - Never revert/overwrite others' unintegrated work.
    - Never use destructive git cleanup on shared work.
```
