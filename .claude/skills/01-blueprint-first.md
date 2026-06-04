# Blueprint First

Use before starting any non-trivial development task. This skill ensures you understand the product goal, repository state, technical scope, affected modules, risks, and test strategy before implementation.

## When to Use

- New feature
- Bug fix with unclear cause
- Refactor
- Backend API change
- Database/model change
- Frontend workflow change
- Agent workflow change
- Export pipeline change
- Security/privacy-sensitive change

## Required Workflow

1. Run `git status --short --branch`.
2. Read `CLAUDE.md`.
3. Read relevant docs from `docs/`.
4. Inspect current code before proposing changes.
5. Restate the user goal in clear English.
6. Decide scope: frontend-only / backend-only / full-stack / documentation-only.
7. State whether existing backend APIs can support the change.
8. Identify affected areas:
   - Product behavior
   - Backend API
   - Data model
   - Agent workflow
   - Retrieval
   - Export pipeline
   - Frontend UI
   - Tests
   - Documentation
9. Break work into small implementation steps.
10. Define acceptance criteria.
11. Define testing approach, including UI screenshot checks for frontend work.
12. List out-of-scope items to avoid scope creep.
13. Only then start implementation.

## CV Master-Specific Rules

- MVP is single-user and local/private.
- Do not add SaaS tenancy, billing, job-board auto-apply, or production auth unless explicitly requested.
- Career facts live in Postgres as source of truth. Markdown vault is not canonical.
- Resume generation must remain truthful and evidence-grounded.
- Export must happen only after user approval.
- Do not change the chosen core stack unless docs and ADRs are updated.

## Done Criteria

- There is a clear implementation plan.
- Scope is explicit.
- Affected files/modules are identified.
- Acceptance criteria and tests are defined.
- Out-of-scope items are listed.
- No code has been changed before repository inspection.

## Common Mistakes

- Jumping into code without reading docs.
- Adding infrastructure that was not requested.
- Adding new backend APIs when existing APIs are enough.
- Adding database fields before confirming necessity.
- Changing architecture without updating ADR/docs.
- Ignoring frontend test and screenshot requirements.
