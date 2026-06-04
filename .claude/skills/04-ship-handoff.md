# Ship Handoff

Use at the end of each task to preserve Git hygiene, document verification, and give the user a clear handoff.

## When to Use

- After implementation and QA
- Before final response to user
- Before committing completed work
- Before pausing a larger task

## Required Workflow

1. Run relevant verification commands from Experience QA.
2. Run `git status --short --branch`.
3. Review changed files.
4. Ensure no secrets, `.env`, generated private resumes, personal evidence files, or unrelated files are staged.
5. Commit finished work unless the user explicitly asks not to.
6. Keep commits atomic and milestone-focused.
7. Use clear commit messages. Examples:
   - `scaffold cv master app structure`
   - `add career profile crud api`
   - `implement resume generation workflow`
   - `add resume export pipeline`
   - `build jd analyzer screen`
8. If work is incomplete, do not pretend it is done.
9. Update documentation if architecture, setup, API, workflow, environment variables, or user behavior changed.
10. Produce a handoff summary.

## Handoff Summary

Must include:
- What changed
- Files changed
- Skills used (from this project's `.claude/skills/`)
- Tests run
- UI screenshots taken, if frontend changed
- Verification results
- Commit hash, if committed
- Known risks or TODOs
- Recommended next step

## Git Rules

- Run `git status` before and after.
- Do not revert user changes.
- Do not commit unrelated changes.
- Do not commit secrets.
- Prefer one commit per coherent milestone.
- If tests fail, summarize the failure honestly and explain what remains.

## Done Criteria

- Working tree status is known.
- Finished work is committed unless told not to.
- Verification results are documented.
- User can understand exactly what was done and what remains.
- No secrets or unrelated files are committed.

## Common Mistakes

- Handing off without `git status`.
- Claiming tests passed without running them.
- Bundling unrelated work into one commit.
- Hiding known failures.
- Forgetting to mention screenshots for frontend changes.
- Leaving documentation stale.
