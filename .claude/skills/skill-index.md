# CV Master Project Skills Index

Use these project-local skills before and during development.

These skills are local to this repository. Do not install them globally.

## Skill Selection

### 01 - Blueprint First
Use before any non-trivial task.
Applies to: planning, scoping, feature design, bug investigation, architecture impact, and test planning.

### 02 - Build Discipline
Use while implementing.
Applies to: backend, frontend, database, agent workflow, retrieval, export, configuration, and documentation changes.

### 03 - Experience QA
Use after implementation.
Applies to: automated tests, frontend screenshot inspection, interaction testing, export verification, and regression checks.

### 04 - Ship Handoff
Use before final response or commit.
Applies to: Git hygiene, commit discipline, verification summary, and user handoff.

## Standard Workflow

For most implementation tasks, use all four in order:

1. Blueprint First — plan the work
2. Build Discipline — implement
3. Experience QA — verify
4. Ship Handoff — commit and summarize

### Shortcuts for smaller tasks

Documentation-only changes:
1. Blueprint First → 2. Build Discipline → 4. Ship Handoff

Bug investigation (no fix yet):
1. Blueprint First → 4. Ship Handoff (with findings)

## Discipline-Specific Requirements

**Frontend changes**: Experience QA is mandatory and must include browser/UI screenshot inspection plus interaction testing.

**Database changes**: Experience QA must include migration verification (`alembic upgrade head`, `alembic check`).

**Agent workflow changes**: Experience QA must include mock LLM or deterministic tests.

**Export changes**: Experience QA must verify generated files exist, are readable, and are ATS-safe.

**Security/privacy changes**: Blueprint First must note network-call and data-exposure implications.
