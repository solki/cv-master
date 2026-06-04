# CV Master Frontend Upgrade Plan

> **Status**: Design Audit & Planning | **Date**: 2026-06-04
>
> This document is a design audit and upgrade plan only. No implementation code is included.
> See [12-test-plan.md](./12-test-plan.md) for the pre-upgrade baseline test results.

---

## 1. Executive Summary

### 1.1 Current UI Assessment

CV Master has a functioning frontend with 9 pages, proper data fetching (TanStack Query), form handling (react-hook-form on 2 pages), and a dark color scheme. The app is structurally sound — navigation works, data flows from API to UI, and basic CRUD operations are functional.

However, the UI exhibits **multiple junior-level visual and interaction defects** that undermine the professional trustworthiness expected of a career-critical application:

| Dimension | Current Grade | Key Gap |
|---|---|---|
| Visual quality | C | Unicode icons, inconsistent spacing, no design tokens |
| Information architecture | B | Navigation structure is correct, but pages lack hierarchy |
| Interaction design | C | Two different form patterns, missing confirmation dialogs, raw JSON display |
| Typography | C | No scale, missing page descriptions on some pages, inconsistent weights |
| Component consistency | D | `<table>` on Library vs `<ul>` elsewhere; raw useState vs react-hook-form |
| Responsiveness | C | Works at mobile, but no tailored layouts |
| Accessibility | F | Zero aria attributes, no keyboard nav, no skip link |
| Error handling | B | Good inline errors, but no toast system, no retry guidance |
| Empty/loading states | D | All plain text strings, no skeleton loaders, no illustrations |

### 1.2 Target Design Direction

CV Master should feel like a **professional-grade personal productivity application** — calm, structured, trustworthy, and efficient for repeated daily use. The visual language should reference modern SaaS tools (Linear, Notion, Vercel) but stay restrained: dense information, clear hierarchy, minimal decoration.

### 1.3 Biggest Problems to Fix (Priority Order)

1. **No design token system** — Colors, spacing, radii, and shadows are hardcoded across 12+ files with no single source of truth.
2. **Inconsistent component patterns** — Two form patterns exist; list rendering uses `<table>` on one page and `<ul>` on another; StatusCard color logic has bugs (invalid `bg-*-9500` class).
3. **No icon system** — Unicode box-drawing characters render inconsistently across platforms.
4. **JD Analyzer shows raw JSON** — The most technical screen shows unformatted API responses.
5. **No loading skeletons or polished empty states** — Every loading state is "Loading..." text.
6. **Missing key interactions** — No export/download from Library, no search/filter on any list, no bulk operations.
7. **Accessibility is completely absent** — No aria attributes, keyboard navigation, or focus management.

---

## 2. Design Principles for CV Master

### Principle 1: Professional Productivity Tool
This is not a marketing landing page. The interface is used repeatedly to manage a career. Information density is appropriate — the user should scan quickly and act efficiently. Whitespace should guide the eye, not waste space.

### Principle 2: Calm and Focused
Dark mode is the default. Colors are muted and restrained. Animations are subtle (150-200ms). The interface should not compete for attention with the resume content being created.

### Principle 3: Evidence-Grounded Trustworthiness
Every generated resume bullet must feel traceable to source facts. The UI must make evidence connections visible and auditable. Confidence indicators must be clear and never rely solely on color.

### Principle 4: ATS/Resume Integrity
The output of this tool is career-critical. The interface must convey precision, correctness, and professionalism. Error states must be clear and actionable. Destructive actions require confirmation.

### Principle 5: Consistent and Predictable
Every list works the same way. Every form validates the same way. Every button hierarchy is consistent. The user should build muscle memory, not re-learn patterns per page.

---

## 3. Current Issues Found

### 3.1 Critical Issues (Must Fix Before Release)

| # | Issue | Impact | Affected Areas | Recommended Fix |
|---|---|---|---|---|
| C1 | No design token system — colors/spacing hardcoded | Any design change requires editing 12+ files; visual drift inevitable | All 12 `.tsx` files + `globals.css` | Create `lib/design-tokens.ts` + CSS custom properties; refactor all components to reference tokens |
| C2 | Unicode icons render inconsistently | "□" shows as empty box on some platforms; looks unprofessional | `nav-sidebar.tsx` (9 nav items) | Replace with SVG icons (inline or simple icon component) |
| C3 | Settings status dot uses invalid class `bg-*-9500` | Status indicator dot is invisible — user can't see health status | `settings/page.tsx` line 55 | Fix to `bg-green-500` / `bg-red-500` / `bg-yellow-500` |
| C4 | Library table uses `border-slate-50` on dark bg | White-ish line artifacts on dark theme table rows | `library/page.tsx` line 36 | Change to `border-slate-800` |
| C5 | JD Analyzer displays raw API JSON | Users see unformatted data dumps; zero readability | `jd/page.tsx` | Parse response into structured sections: Role, Required Skills, Keywords, Match Areas |

### 3.2 High-Priority Issues

| # | Issue | Impact | Affected Areas | Recommended Fix |
|---|---|---|---|---|
| H1 | Two inconsistent form patterns (raw useState vs react-hook-form) | Users encounter different validation/feedback per page | Profile, Resumes, JD (useState) vs Projects, Evidence (RHF) | Standardize all forms on react-hook-form + zod |
| H2 | No loading skeletons | Every loading state is plain "Loading..." text — looks unpolished | All 9 pages | Create `<Skeleton>` component; use in loading states |
| H3 | No confirmation dialogs for destructive actions | Delete is inline Confirm/No — no modal overlay, can be missed | Projects, Evidence delete flows | Create `<ConfirmDialog>` component; use before all deletes |
| H4 | No search/filter on any list | User can't find items in large lists | Projects, Evidence, Library, Resumes | Add search input with debounced local filter |
| H5 | No export/download from Library | Core workflow is incomplete — can't actually get the resume | Library page | Add download buttons per row (PDF, DOCX, MD, HTML) |

### 3.3 Medium-Priority Issues

| # | Issue | Impact | Affected Areas | Recommended Fix |
|---|---|---|---|---|
| M1 | No `<title>` per page — all pages share "CV Master" | Poor browser tab UX; bookmarking confusion | All pages | Add per-page metadata via `metadata` export or `<Head>` |
| M2 | No toast notification system | Success/error feedback is per-page banners — inconsistent | Profile upload, all mutations | Add toast system (custom or shadcn/ui sonner) |
| M3 | Profile form flickers between empty and loaded data | Form initializes with empty strings, then populates from API | `profile/page.tsx` | Use `useEffect` to sync form state from query data |
| M4 | Resume list is read-only (no edit/delete) | Users can't manage resumes after creation | `resumes/page.tsx` | Add edit/delete actions matching Projects/Evidence pattern |
| M5 | Confidence field hidden on Evidence form but sent on create | Users can't set confidence on new evidence | `evidence/page.tsx` | Add confidence slider/input to the form |
| M6 | `Position` type defined but no Position page exists | Positions are part of the data model but have no UI | New page needed | Add `/positions` page or integrate into Career Profile tab |
| M7 | No empty state illustrations | Empty states feel like errors rather than "you haven't started yet" | All list pages | Add simple SVG illustrations for empty states |
| M8 | Sidebar has no collapsed state on desktop | Fixed 224px sidebar always takes space | `nav-sidebar.tsx` | Add collapse toggle; persist to Zustand/localStorage |

### 3.4 Low-Priority Issues

| # | Issue | Impact | Affected Areas | Recommended Fix |
|---|---|---|---|---|
| L1 | No favicon | Browser tab shows default icon | Layout | Add favicon.ico |
| L2 | No keyboard shortcut hints | Power users can't navigate quickly | All pages | Add `⌘K` command palette (optional) |
| L3 | Vault page is entirely static | Page has zero interactivity — feels like placeholder | `vault/page.tsx` | Add markdown file listing from API or note explaining future plans |
| L4 | `avatar` field missing from Profile | No profile photo upload | `profile/page.tsx` | Add avatar upload or skip if out of scope |
| L5 | No print stylesheet | Resume export preview doesn't print cleanly | `globals.css` | Add `@media print` styles |

---

## 4. New Visual Design System

### 4.1 Color Palette

**Theme**: Dark-first, professional. Based on Slate + Blue.

```
Page Background:        slate-950   #020617
Surface (cards):        slate-900   #0f172a
Surface Hover:          slate-800   #1e293b
Border:                 slate-700   #334155
Border Subtle:          slate-800   #1e293b

Text Primary:           slate-100   #f1f5f9
Text Secondary:         slate-300   #cbd5e1
Text Muted:             slate-400   #94a3b8
Text Placeholder:       slate-500   #64748b

Accent (primary):       blue-500    #3b82f6
Accent Hover:           blue-400    #60a5fa
Accent Subtle BG:       blue-950    #172554
Accent Text:            blue-300    #93c5fd

Success BG:             emerald-950 #022c22
Success Text:           emerald-400 #34d399
Success Border:         emerald-800 #065f46

Error BG:               red-950     #450a0a
Error Text:             red-400     #f87171
Error Border:           red-800     #991b1b

Warning BG:             amber-950   #451a03
Warning Text:           amber-400   #fbbf24
Warning Border:         amber-800   #92400e
```

### 4.2 Semantic Color Tokens

```css
--color-page:           var(--slate-950);
--color-surface:        var(--slate-900);
--color-surface-hover:  var(--slate-800);
--color-border:         var(--slate-700);
--color-text:           var(--slate-100);
--color-text-secondary: var(--slate-300);
--color-text-muted:     var(--slate-400);
--color-accent:         var(--blue-500);
--color-accent-hover:   var(--blue-400);
--color-success:        var(--emerald-400);
--color-error:          var(--red-400);
--color-warning:        var(--amber-400);
```

### 4.3 Typography Scale

| Token | Size | Weight | Use |
|---|---|---|---|
| `text-xs` | 0.75rem (12px) | 400/500 | Badges, meta, timestamps |
| `text-sm` | 0.875rem (14px) | 400/500 | Body text, list items, form labels |
| `text-base` | 1rem (16px) | 400 | Long-form content, descriptions |
| `text-lg` | 1.125rem (18px) | 600 | Card titles, section headers |
| `text-xl` | 1.25rem (20px) | 600 | Page subtitles |
| `text-2xl` | 1.5rem (24px) | 700 | Page titles |
| `text-3xl` | 1.875rem (30px) | 700 | Dashboard hero numbers |

**Font Family**: `system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif` (no change needed — this is optimal).

**Line Height**: `leading-relaxed` (1.625) for body, `leading-normal` for headings.

### 4.4 Spacing Scale

Use Tailwind's default spacing scale (4px base):

| Token | Value | Use |
|---|---|---|
| `p-2` / `gap-2` | 8px | Compact items, icon buttons, badges |
| `p-3` / `gap-3` | 12px | Form fields, list item gaps |
| `p-4` / `gap-4` | 16px | Card internal padding |
| `p-6` / `gap-6` | 24px | Card padding, section gaps |
| `space-y-8` | 32px | Page section spacing |

### 4.5 Border Radius

| Token | Use |
|---|---|
| `rounded` (4px) | Buttons, inputs, badges |
| `rounded-md` (6px) | Small cards, dropdowns |
| `rounded-lg` (8px) | Standard cards |
| `rounded-xl` (12px) | Modal dialogs |

### 4.6 Shadow Usage

Shadows should be subtle on dark backgrounds:

| Token | Use |
|---|---|
| None | List items, text content areas |
| `shadow-sm` | Cards that need slight elevation |
| `shadow-md` | Modals, dropdowns |
| `shadow-lg` | Nothing in this app (too heavy for dark theme) |

### 4.7 Icon System

**Replace** all Unicode icons with a lightweight inline SVG approach:

- Navigation icons: 20×20px SVG, `currentColor` fill
- Action icons (edit, delete, download): 16×16px
- Status indicators: 8×8px filled circles

**Recommendation**: Use simple inline SVGs (no icon library dependency). 9 navigation icons + ~5 action icons = ~14 SVGs total. This is manageable without an icon library.

Alternative: Add `lucide-react` back and use their icon set — cleaner code, slightly larger bundle.

### 4.8 Button Hierarchy

| Level | Classes | Use |
|---|---|---|
| Primary | `bg-blue-600 text-white hover:bg-blue-500` | Main actions: Save, Create, Generate |
| Secondary | `bg-slate-800 text-slate-200 hover:bg-slate-700 border border-slate-600` | Cancel,次要操作 |
| Ghost | `text-slate-300 hover:text-slate-100 hover:bg-slate-800` | Edit, inline actions |
| Danger | `bg-red-600 text-white hover:bg-red-500` | Delete confirmation |
| Icon | `p-1.5 rounded hover:bg-slate-800` | Icon-only buttons |

### 4.9 Badge Styles

| Type | Classes | Use |
|---|---|---|
| Status: Active | `bg-emerald-900 text-emerald-400 text-xs px-2 py-0.5 rounded-full` | Approved, Healthy |
| Status: Draft | `bg-slate-800 text-slate-300 ...` | Draft, Pending |
| Status: Error | `bg-red-900 text-red-400 ...` | Error, Failed |
| Confidence: High | `bg-emerald-900 text-emerald-400` | ≥ 0.8 |
| Confidence: Medium | `bg-amber-900 text-amber-400` | 0.5-0.79 |
| Confidence: Low | `bg-red-900 text-red-400` | < 0.5 |

### 4.10 Status Indicators

Always pair color with a text label or icon. Never use color as the sole differentiator:

```
✅ Green dot + "Connected"  (not just green dot)
⚠️ Amber dot + "Not configured"  (not just amber dot)
❌ Red dot + "Error"  (not just red dot)
```

---

## 5. Layout System

### 5.1 App Shell

```
┌──────────────────────────────────────────────────┐
│ ┌──────────┐ ┌─────────────────────────────────┐ │
│ │          │ │ Page Header                      │ │
│ │ Sidebar  │ │ (title + description + actions)  │ │
│ │          │ │                                  │ │
│ │ 224px    │ │ Content Area                     │ │
│ │ fixed    │ │ (cards, lists, forms)            │ │
│ │          │ │                                  │ │
│ │          │ │ max-w-5xl (1024px)              │ │
│ └──────────┘ └─────────────────────────────────┘ │
└──────────────────────────────────────────────────┘
```

### 5.2 Sidebar

- **Width**: 224px (`w-56`) fixed on desktop
- **Collapsible**: Toggle to 56px (icons only) via sidebar footer button
- **Mobile**: Overlay drawer, 280px wide, closes on nav or overlay tap
- **Active indicator**: Left accent bar (`border-l-2 border-blue-500`) + subtle bg (`bg-blue-950`)
- **Branding**: "CV Master" at top, user avatar at bottom

### 5.3 Page Header Pattern

Every page must follow this structure:

```tsx
<div className="flex items-center justify-between">
  <div>
    <h1 className="text-2xl font-bold text-slate-100">{pageTitle}</h1>
    <p className="text-slate-400 mt-1">{pageDescription}</p>
  </div>
  <div className="flex items-center gap-2">
    {/* Primary action buttons */}
  </div>
</div>
```

### 5.4 Content Max Width

- **Default content**: `max-w-5xl` (1024px) — comfortable reading width for forms and lists
- **Full-width content**: Remove max-width for dashboards with grid layouts
- **Resume preview**: `max-w-3xl` (768px) — mimics A4/US Letter readability

### 5.5 Grid System

| Context | Grid | Gap |
|---|---|---|
| Dashboard cards | `grid-cols-1 md:grid-cols-2 lg:grid-cols-3` | `gap-4` |
| Form fields (2-col) | `grid-cols-1 sm:grid-cols-2` | `gap-4` |
| Form fields (3-col) | `grid-cols-1 sm:grid-cols-3` | `gap-4` |
| Settings panels | `grid-cols-1 lg:grid-cols-2` | `gap-6` |

### 5.6 Responsive Behavior

| Breakpoint | Behavior |
|---|---|
| < 768px (mobile) | Sidebar hidden, hamburger toggle; single-column layouts; full-width cards |
| 768-1024px (tablet) | Sidebar visible; 2-column grids; comfortable spacing |
| > 1024px (desktop) | Full layout; 2-3 column grids; max-width content |

---

## 6. Component Upgrade Plan

### 6.1 AppShell (`components/app-shell.tsx`)
**Current**: Layout is inline in `layout.tsx` with NavSidebar + ErrorBoundary.
**Target**: Separate AppShell component with:
- Sidebar + content area
- Optional top bar (breadcrumbs, search)
- Responsive sidebar toggle
- Skip-to-content link

### 6.2 Sidebar Navigation (`components/nav-sidebar.tsx`)
**Current**: Unicode icons, 9 nav items, active highlighting works.
**Target**:
- Replace Unicode with SVG icons (or lucide-react)
- Add collapsed state (icon-only mode)
- Add notification badges for incomplete items
- Add keyboard navigation (arrow keys, Enter)
- Add `aria-current="page"` on active item

### 6.3 PageHeader (`components/page-header.tsx`)
**New component** — currently each page manually renders heading + description.
```tsx
interface PageHeaderProps {
  title: string;
  description: string;
  actions?: React.ReactNode;  // Button group
}
```
Ensures consistent spacing and typography across all 9 pages.

### 6.4 Dashboard Cards (`components/dashboard/`)
**Current**: Three `QuickActionCard` links + two data cards inline.
**Target**:
- Separate `QuickActionCard` component
- `ProfileSummaryCard` with completeness progress bar
- `RecentResumesList` with status badges and timestamps
- `ActivityTimeline` (future: recent generation runs)

### 6.5 Entity Tables (`components/data-table.tsx`)
**Current**: `<table>` on Library, `<ul>` on Projects/Evidence — inconsistent.
**Target**: Single `DataTable` component:
- Sortable columns
- Row hover actions (edit, delete, export)
- Empty state slot
- Loading skeleton variant
- Consistent across Projects, Evidence, Library, Resumes

### 6.6 Forms (`components/form/`)
**Current**: Two patterns (raw useState vs react-hook-form).
**Target**: Standardize on react-hook-form + zod. Create shared form components:
- `FormField` — label + input + error message
- `FormTextarea` — label + textarea + error + character count
- `FormSelect` — label + select + error
- `FormActions` — Save/Cancel button group with loading state

### 6.7 ConfirmDialog (`components/confirm-dialog.tsx`)
**New component** — replaces current inline Delete Confirm/No pattern.
```tsx
<ConfirmDialog
  open={open}
  title="Delete Project"
  description="This will permanently delete 'Data Pipeline'. This action cannot be undone."
  confirmLabel="Delete"
  variant="danger"
  onConfirm={() => deleteMutation.mutate(id)}
  onCancel={() => setOpen(false)}
/>
```

### 6.8 Empty States (`components/empty-state.tsx`)
**New component** — replaces current "No projects yet." text.
```tsx
<EmptyState
  icon={<FolderIcon />}
  title="No projects yet"
  description="Add your first project to start building your resume blocks."
  action={{ label: "New Project", onClick: () => setShowForm(true) }}
/>
```

### 6.9 Loading States (`components/skeleton.tsx`)
**New component** — replaces all plain "Loading..." text.
```tsx
// Card skeleton
<div className="bg-slate-900 rounded-lg border border-slate-700 p-6 animate-pulse">
  <div className="h-4 bg-slate-800 rounded w-1/3 mb-4" />
  <div className="h-3 bg-slate-800 rounded w-full mb-2" />
  <div className="h-3 bg-slate-800 rounded w-2/3" />
</div>
```

### 6.10 Resume Preview (`components/resume-preview/`)
**New feature** — critical for the core workflow.
- Renders generated resume content in a professional preview
- Annotates ATS keyword coverage (highlight matched/missing)
- Click on bullet → show evidence trace panel
- Toggle between raw/preview mode
- Responsive: A4-like width on desktop, full-width on mobile

### 6.11 Evidence Trace Panel (`components/evidence-trace.tsx`)
**New feature** — shows which source facts support a given resume bullet.
- Slide-out panel or inline expand
- Lists evidence items with confidence badges
- Link to view/edit source evidence

### 6.12 JD Keyword Coverage (`components/jd-keywords.tsx`)
**New feature** — visualizes how well profile matches JD.
- Required skills: Matched ✅ / Partial ⚠️ / Missing ❌
- Keyword frequency bar or word cloud
- Gap summary (e.g., "3 of 7 required skills matched")

### 6.13 Export Buttons (`components/export-buttons.tsx`)
**New component** — download buttons for generated resumes.
- PDF, DOCX, Markdown, HTML format buttons
- Loading state during export generation
- Success → trigger browser download

### 6.14 Settings Panels (`components/settings/`)
**Current**: Inline StatusCard with invalid color classes.
**Target**:
- `StatusCard` — fixed color logic
- `ProviderConfig` — shows active LLM provider with test button
- `ApiKeyField` — masked input for API keys

---

## 7. Page-by-Page Redesign Plan

### 7.1 Dashboard

**Current State**: Quick action cards + profile overview + recent resumes. Works but feels sparse.

**Target**:
- **Top row**: 3 quick action cards with icons (upload, paste JD, new resume)
- **Middle row**: Profile completeness bar (e.g., "Profile 60% complete — add 3 missing items")
- **Bottom row**: Recent resumes list with status + timestamps + quick-export buttons
- **Future**: Activity timeline showing recent generation runs

**Files**: `app/page.tsx`, new `components/dashboard/*.tsx`

### 7.2 Career Profile

**Current State**: View/edit toggle with text inputs. PDF upload section. Works but form flickers.

**Target**:
- **Tab bar**: "Personal Info" | "Positions" | "Education" | "Certifications"
- **Personal Info tab**: Current fields + avatar placeholder
- **Positions tab**: List of positions with inline add/edit (using DataTable)
- **Education tab**: Same pattern
- **Certifications tab**: Same pattern
- **PDF Import**: Move to a more prominent position with progress indicator
- **Form sync**: Populate form from API data in useEffect to prevent flicker

**Files**: `app/profile/page.tsx`, new `app/positions/page.tsx`

### 7.3 Projects

**Current State**: Best-implemented page. react-hook-form validation, edit/delete, hover actions. Solid foundation.

**Target**:
- Replace `<ul>` with DataTable component
- Add search/filter by title or skills
- Add skill chips (parse comma-separated skills into visual tags)
- Add "Used in X resumes" count per project
- Move form to a slide-out panel or modal (current inline form pushes list down)

**Files**: `app/projects/page.tsx`

### 7.4 Evidence

**Current State**: Similar to Projects but with type selector and confidence badge. Missing confidence input.

**Target**:
- Replace `<ul>` with DataTable
- Add confidence slider/input to form
- Add evidence type filter tabs
- Show linked projects/achievements for each evidence item
- Add file attachment support (beyond URL)

**Files**: `app/evidence/page.tsx`

### 7.5 JD Analyzer

**Current State**: Three input methods (paste, URL, file). Results shown as raw JSON. Biggest gap.

**Target**:
- **Top section**: Tab bar — "Paste Text" | "URL Fetch" | "Upload .md"
- **Paste tab**: Large textarea + "Analyze" button
- **URL tab**: URL input + "Fetch & Analyze" button
- **Upload tab**: File input with drag-and-drop zone
- **Results section** (appears after analysis):
  - Parsed structured output: Role, Company (if detected), Seniority
  - Required Skills list with match indicators (✅❌⚠️)
  - Preferred Skills list
  - Keyword frequency visualization
  - "Generate Resume from this JD" call-to-action button
- **History**: Recently analyzed JDs list in sidebar or bottom section

**Files**: `app/jd/page.tsx`, new `components/jd-keywords.tsx`

### 7.6 Resume Generator

**Current State**: Simple create form + resume list. No preview, no export.

**Target**:
- **Generation panel** (left/top):
  - JD selector (dropdown with search)
  - Template selector (ATS Compact, Modern, Academic)
  - Tone selector (Professional, Balanced, Bold)
  - Length selector (1 page, 2 pages)
  - Output format checkboxes (PDF, DOCX, MD, HTML)
  - "Generate Resume" primary button
- **Preview panel** (right/bottom):
  - Live resume preview with ATS annotations
  - Keyword coverage overlay
  - Click bullet → evidence trace panel
- **Generation progress**: Multi-step indicator showing pipeline stages (Analyze → Research → Retrieve → Strategy → Draft → Review → Ground)
- **Post-generation**: Edit individual bullets, regenerate sections, approve/export

**Files**: `app/resumes/page.tsx`, new `components/resume-preview/*.tsx`

### 7.7 Resume Library

**Current State**: Read-only table. No actions, no export, no search. `border-slate-50` bug.

**Target**:
- DataTable with columns: Title, Target Role, JD, Status, Created, Actions
- Actions per row: View Preview, Download (PDF/DOCX/MD/HTML), Delete
- Sort by date or status
- Filter by status (All, Draft, Approved)
- Status tabs at top
- Click row → navigate to Resume Generator with that resume loaded

**Files**: `app/library/page.tsx`

### 7.8 Knowledge Vault

**Current State**: Static informational page. Zero interactivity.

**Target**:
- File listing from API (actual vault contents)
- File/folder icons
- Click to view markdown content
- Edit button opens markdown editor (future phase)
- Sync status indicator
- Or: If vault integration is Phase 2, show a clear "Coming Soon" with explanation

**Files**: `app/vault/page.tsx`

### 7.9 Settings

**Current State**: Two status cards + config text. Invalid status dot classes.

**Target**:
- **System Status**: Health card with real-time check (working)
- **LLM Configuration**: Provider selector dropdown (read from env, no edit in MVP)
- **Search Configuration**: Tavily status indicator
- **Export Defaults**: Default format selector, default template
- **About**: Version number, documentation links
- Fixed status dot colors

**Files**: `app/settings/page.tsx`

---

## 8. Interaction Design Improvements

### 8.1 Form Submission Feedback
- **Inline validation**: Show errors as user types (after first blur), not just on submit
- **Submit button**: Disabled during mutation, shows spinner + "Saving..."
- **Success**: Toast notification + form close/data refresh (not page redirect)
- **Error**: Inline error message below form, not page-top banner

### 8.2 Destructive Action Confirmation
- **Delete**: Always use ConfirmDialog modal (never inline Confirm/No)
- **Discard changes**: Warn if form has unsaved changes and user clicks away
- **Irreversible actions**: Require typing the item name to confirm (e.g., "Type 'DELETE' to confirm")

### 8.3 Inline Validation
- Required fields: Show "Required" hint on focus, error on blur if empty
- Format validation: URL format, email format — validate on blur
- Character limits: Show remaining characters (e.g., "234/500")

### 8.4 Skeleton Loading
Replace all "Loading..." text with skeleton placeholders:
- **Cards**: 3-4 horizontal bars of varying width
- **Tables**: 5 rows of skeleton cells
- **Forms**: Skeleton input fields matching real input width

### 8.5 Toast Notifications
- **Success**: Green toast, auto-dismiss 5s (e.g., "Project saved")
- **Error**: Red toast, manual dismiss (e.g., "Failed to save project")
- **Info**: Blue toast, auto-dismiss 3s (e.g., "Resume generated")
- Position: Bottom-right corner, stacking

### 8.6 Selected/Hover/Focus States
- **Focus ring**: `focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500` on all inputs
- **Row hover**: `hover:bg-slate-800` with visible action buttons
- **Selected row**: `bg-blue-950 border-l-2 border-blue-500`
- **Active nav**: Current implementation works — keep pattern

### 8.7 Keyboard Accessibility
- **Tab order**: Logical flow through form fields → actions → navigation
- **Enter**: Submit form
- **Escape**: Close modal/dialog/dropdown
- **Arrow keys**: Navigate list items, DataTable rows
- **⌘K**: Command palette (optional, Phase F)
- **Skip link**: "Skip to main content" as first focusable element

### 8.8 Responsive Interactions
- **Touch targets**: Minimum 44×44px for all interactive elements on mobile
- **Swipe**: Swipe-to-delete on list items (optional, Phase F)
- **Pull-to-refresh**: On mobile list pages (optional)
- **Bottom sheet**: Forms open as bottom sheets on mobile instead of inline

---

## 9. Implementation Plan

### Phase A: Design Tokens & Global Styles (3-5 files)
1. Create `lib/design-tokens.ts` with color, spacing, typography constants
2. Refactor `globals.css` to use CSS custom properties from tokens
3. Update `tailwind.config.ts` if using Tailwind v4 theme customization
4. Fix critical CSS bugs (status dot `bg-*-9500`, table border `slate-50`)
5. Add per-page `<title>` metadata

**Files**: `lib/design-tokens.ts` (NEW), `app/globals.css`, `tailwind.config.ts`

### Phase B: App Shell, Navigation, Layout (3-5 files)
1. Create `AppShell` component extracted from `layout.tsx`
2. Replace Unicode nav icons with SVGs (or re-add lucide-react)
3. Add skip-to-content link
4. Add sidebar collapse toggle
5. Add `aria-*` attributes to navigation

**Files**: `components/app-shell.tsx` (NEW), `components/nav-sidebar.tsx`, `app/layout.tsx`

### Phase C: Shared Components (8-12 files)
1. `PageHeader` — consistent heading + description + actions
2. `DataTable` — unified list/table component
3. `EmptyState` — illustrated empty states
4. `Skeleton` — loading skeletons
5. `ConfirmDialog` — modal confirmation
6. `Toast` — notification system
7. `Badge` — status/confidence badges
8. `FormField`, `FormTextarea`, `FormSelect` — standardized form controls

**Files**: `components/ui/*` (NEW directory)

### Phase D: Page Redesigns (9 pages)
1. Standardize all 9 pages to use PageHeader, DataTable, shared components
2. Convert all forms to react-hook-form + zod
3. Add loading skeletons to all pages
4. Add empty states with illustrations
5. Fix profile form flicker
6. Standardize error display

**Files**: All `app/**/page.tsx`

### Phase E: Workflow-Specific UX (4-6 files)
1. `ResumePreview` component with clickable bullets
2. `EvidenceTracePanel` slide-out
3. `JDKeywordCoverage` visualization
4. `ExportButtons` with format download
5. `GenerationProgress` multi-step indicator
6. JD Analyzer structured output (replace raw JSON)

**Files**: `components/resume-preview/*`, `components/jd-keywords.tsx`, `components/evidence-trace.tsx`

### Phase F: Responsive & Accessibility Polish
1. Add `aria-*` attributes throughout
2. Ensure keyboard navigation works on all interactive elements
3. Test screen reader flow
4. Mobile-optimized layouts (bottom sheets, touch targets)
5. Print stylesheet for resume preview

### Phase G: QA, Screenshot Review & Tests
1. Take before/after screenshots of all 9 pages
2. Run build + lint + typecheck
3. Manual interaction test checklist
4. Responsive test at 375/768/1280/1440px
5. Keyboard-only navigation test
6. Update `docs/12-test-plan.md` with verification results

---

## 10. Acceptance Criteria

A PR-ready frontend upgrade must satisfy:

- [ ] All 9 pages use consistent components (PageHeader, DataTable, forms)
- [ ] All forms use react-hook-form + zod validation
- [ ] No plain "Loading..." text — all loading states use skeletons
- [ ] All empty states have illustration + description + action
- [ ] Unicode icons replaced with proper SVGs
- [ ] Settings status dots display correct colors
- [ ] Library table has no white border artifact
- [ ] JD Analyzer displays structured output, not raw JSON
- [ ] ConfirmDialog used for all destructive actions
- [ ] At minimum, `aria-label` on interactive elements
- [ ] `npm run build` succeeds with zero errors
- [ ] `npx tsc --noEmit` succeeds with zero errors
- [ ] Screenshots of all 9 pages show consistent visual quality
- [ ] Responsive layout works at 375px, 768px, 1280px
- [ ] Dark theme is the default and all elements are readable

---

## 11. QA Plan

### 11.1 Automated Checks
```bash
npm run build        # Next.js production build
npm run lint         # ESLint
npx tsc --noEmit     # TypeScript type checking
```

### 11.2 Screenshot Inspection
Take full-page screenshots of all 9 pages at 1440×900:
- [ ] Dashboard
- [ ] Career Profile (view + edit states)
- [ ] Projects (list + form states)
- [ ] Evidence (list + form states)
- [ ] JD Analyzer (empty + results states)
- [ ] Resume Generator (list + create states)
- [ ] Resume Library (table + empty states)
- [ ] Knowledge Vault
- [ ] Settings

Visually verify: consistent spacing, no overlapping elements, readable text, correct colors.

### 11.3 Interaction Testing Checklist
- [ ] Navigate between all 9 pages via sidebar
- [ ] Create, edit, delete a Project — verify all states
- [ ] Create, edit, delete Evidence — verify all states
- [ ] Paste JD and analyze — verify structured output
- [ ] Create resume — verify generation trigger
- [ ] Upload PDF to Profile — verify error/success feedback
- [ ] Check Settings health/LLM status
- [ ] Mobile: toggle sidebar, navigate, fill form
- [ ] Keyboard: Tab through form, Enter to submit, Escape to close

### 11.4 Responsive Testing
| Breakpoint | Check |
|---|---|
| 375px | Sidebar hidden, hamburger works, forms single-column |
| 768px | Sidebar visible, 2-col grids work |
| 1280px | Full layout, max-width content centered |
| 1440px | No layout break at large widths |

### 11.5 Accessibility Checks
- [ ] All interactive elements reachable via Tab
- [ ] Focus ring visible on all focused elements
- [ ] Forms have associated labels (htmlFor or aria-label)
- [ ] Color is never the sole indicator (text/icon always present)
- [ ] Skip-to-content link present and functional

---

## 12. Out of Scope

The following are explicitly excluded from this frontend upgrade:

- Backend API changes or new endpoints
- New product features (Phase 2 roadmap items)
- Authentication / multi-user / billing
- AI agent workflow changes
- Database schema changes
- New entity types (interview prep, job tracker, etc.)
- Internationalization (i18n)
- Real-time collaboration features
- Analytics or telemetry
- E2E test implementation (covered by test plan, not part of visual upgrade)
- Performance optimization beyond build-size checks

---

## Appendix A: Files to be Changed in Implementation

### New Files (~20)
```
apps/web/
  lib/design-tokens.ts
  components/
    app-shell.tsx
    ui/
      page-header.tsx
      data-table.tsx
      empty-state.tsx
      skeleton.tsx
      confirm-dialog.tsx
      toast.tsx
      badge.tsx
      form-field.tsx
      form-textarea.tsx
      form-select.tsx
    dashboard/
      quick-action-card.tsx
      profile-summary-card.tsx
    resume-preview/
      index.tsx
      evidence-trace-panel.tsx
    jd-keywords.tsx
    export-buttons.tsx
    icons.tsx (inline SVG icon components)
```

### Modified Files (~14)
```
apps/web/
  app/
    globals.css
    layout.tsx
    providers.tsx
    page.tsx (Dashboard)
    profile/page.tsx
    projects/page.tsx
    evidence/page.tsx
    jd/page.tsx
    resumes/page.tsx
    library/page.tsx
    vault/page.tsx
    settings/page.tsx
  components/
    nav-sidebar.tsx
    error-boundary.tsx
  lib/
    types.ts
    store.ts
```

---

## Appendix B: Audit Screenshots Reference

Pre-upgrade screenshots captured at 1440×900, dark theme:

| File | Page |
|---|---|
| [audit-01-dashboard.png](screenshots/audit-01-dashboard.png) | Dashboard |
| [audit-02-projects.png](screenshots/audit-02-projects.png) | Projects |
| [audit-03-jd.png](screenshots/audit-03-jd.png) | JD Analyzer |
| [audit-04-resumes.png](screenshots/audit-04-resumes.png) | Resume Generator |
| [audit-05-library.png](screenshots/audit-05-library.png) | Resume Library |
| [audit-06-settings.png](screenshots/audit-06-settings.png) | Settings |
