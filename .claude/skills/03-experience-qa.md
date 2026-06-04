# Experience QA

Use after implementation and before handoff. This skill verifies that the feature actually works, tests are updated, and frontend behavior is visually and interactively correct.

## When to Use

- After any implementation
- After frontend changes
- After API changes
- After agent workflow changes
- After export changes
- Before committing or handing off work

## Required Workflow

1. Identify what changed.
2. Identify the expected user-visible behavior.
3. Run relevant automated tests.

### Backend Verification

- Run pytest or the project-specific backend test command.
- Test API validation where applicable.
- Test error cases, not only the happy path.

### Database Verification

- Run Alembic migration check (`alembic upgrade head`, `alembic check`).
- Confirm no unnecessary schema changes.

### Agent Workflow Verification

- Use mock LLM tests.
- Verify structured outputs match expected schemas.
- Verify unsupported claims are flagged.
- Verify evidence references exist where expected.

### Export Verification

- Generate test Markdown, HTML, PDF, and DOCX where applicable.
- Confirm files exist and are readable.
- Confirm filenames and paths are safe.

### Frontend Verification

- Run lint, typecheck, test, and build commands where available.
- Use browser automation or UI inspection tool to open the page.
- Take screenshots of changed pages or components.
- Visually inspect layout, spacing, readability, and responsive behavior.
- Test every affected interactive function.
- Test loading, success, error, empty, and confirmation states where applicable.

## Frontend Interaction Checklist

- Navigation works.
- Forms validate required fields.
- Submit actions show loading and success/error feedback.
- Dialogs open and close correctly.
- Tables/lists handle empty states.
- Edit/delete actions require confirmation where destructive.
- Generated resume preview updates correctly.
- Evidence trace panel works for selected bullets.
- Export buttons behave correctly.
- Errors are visible and understandable.
- Screenshots confirm UI is visually acceptable.

## CV Master-Specific Quality Checks

- Resume content is ATS-friendly and parseable.
- Section headings are standard and clear.
- JD keywords are included naturally, not stuffed.
- Strong claims link back to evidence.
- Unsupported claims are flagged.
- User approval is required before export.
- Generated files are professional and readable.

## Done Criteria

- Relevant automated tests pass or failures are clearly explained.
- Frontend changes were inspected through browser/UI tooling with screenshots.
- Every affected interaction was manually or automatically tested.
- Tests were added or updated for new behavior.
- Verification evidence is ready for the handoff summary.

## Common Mistakes

- Only running lint but not testing interactions.
- Assuming UI looks right without opening it.
- Not testing error or empty states.
- Not updating tests after adding features.
- Not verifying exported files.
- Not recording verification commands.
