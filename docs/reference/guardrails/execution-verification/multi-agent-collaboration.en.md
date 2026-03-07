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
version: v1.3.0
last_updated: 2026-03-08
updated_by: codex
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
  - Owns carrying accepted contributor changes back to the user's delivery branch
  - Defines the task split, prompt structure, acceptance criteria, and integration order for each round
  - Decides when the default fixed-contributor model is sufficient and when a temporary specialist agent is needed
- **Contributor Agent**
  - Edits only assigned scope
  - Delivers atomic commits and handoff notes for integration

## Integrator First Workflow

Every new Integrator Agent should start with this workflow:

1. **Read SoT**
   - Read this document and the current architecture / guardrail SoT for the active topic.
   - Determine whether the work continues an existing delivery line or starts a new phase.

2. **Audit the delivery branch**
   - Confirm the user's actual delivery branch (usually `main`).
   - Audit integrated, non-integrated, and obsolete branches / worktrees.
   - Do not treat changes that exist only in an isolated integration branch as already integrated.

3. **Decide task split**
   - First decide which work must stay with the Integrator:
     - cherry-pick / conflict resolution
     - overlap hot zones
     - final regression / acceptance
   - Then split the remaining work into contributor tasks.

4. **Docs first, then code**
   - If the task changes contracts, architecture, or semantics, require contributors to read guardrails, update docs first, then apply code in one cohesive pass.
   - The Integrator should follow the same rule.

5. **Issue prompts**
   - Every contributor task must define:
     - `Task ID / Topic`
     - `Goal`
     - `Allowed Files`
     - `Non-Goals` / `Constraints`
     - `Verification`
     - `Contributor Report v1`
   - `Allowed Files` are defined per task by the Integrator; they are not permanently hardcoded by this document.

6. **Integrate and verify**
   - Integrate only real incremental commits.
   - If a contributor report is incomplete, out of scope, or only exists as a dirty worktree without a commit, the Integrator should not treat it as a complete deliverable.
   - Final accepted changes must be integrated back into the user's delivery branch.

## Recommended Default Contributor Setup

To reduce long-running token overhead, prefer a default setup of **3 fixed Contributor Agents**:

1. `Platform Agent`
   - persistence / repositories / TraceStore / metadata contracts / ingest write paths
2. `Simulation Agent`
   - simulation page / post-processing page / result views / Josephson examples E2E
3. `Characterization Agent`
   - characterization page / analysis services / trace scope / characterization regressions

!!! note "Recommended default, not a permanent hard boundary"
    This document does not permanently freeze contributor file boundaries.
    The exact `Allowed Files`, bridge responsibilities, and cross-cutting scope are still defined by the Integrator in each task prompt.

### Why prefer 3 fixed contributors

- It reduces repeated thread bootstrap cost
- It lets contributors accumulate stable context in their subdomains
- It lets the Integrator focus on task split, integration, and acceptance instead of redesigning the collaboration model every round

### When to add temporary specialist agents

Add temporary specialist agents only when the default 3 contributors are not enough, for example:

- docs-only refactors
- validation matrix expansion
- deployment / infra / CI work
- one-off large Playwright stabilization

Temporary agents are supplements, not replacements for the Integrator's task-splitting responsibility.

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
    - Integrator MUST carry accepted contributor changes back to the user's delivery branch.
    - Integrator MUST define the task split, prompt structure, `Allowed Files`, and acceptance criteria for each round.
    - Integrator MUST treat prompt design as part of the integration job, not as optional overhead.
- **Recommended Default Contributor Setup**:
    - Prefer 3 long-lived contributors by default: Platform, Simulation, Characterization.
    - Treat these as working defaults, not permanent hard boundaries.
    - Exact file boundaries are defined per task by the Integrator.
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
    - Dirty worktree changes without a committed handoff are not a complete contributor deliverable.
- **Never**:
    - Never revert/overwrite others' unintegrated work.
    - Never use destructive git cleanup on shared work.
```
