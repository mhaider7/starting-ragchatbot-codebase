# Frontend Changes — Code Quality Tooling

## What was added

### Prettier (formatter)
- `frontend/.prettierrc` — config: 4-space indent, single quotes, trailing commas (ES5), 100-char line width
- `frontend/.prettierignore` — excludes `package-lock.json` and `node_modules/`
- All three existing frontend files were auto-formatted:
  - `frontend/script.js`
  - `frontend/style.css`
  - `frontend/index.html`

### ESLint (linter)
- `frontend/eslint.config.js` — flat config for ES2022, browser globals (`document`, `fetch`, `marked`, etc.)
- Rules enforced: `no-undef` (error), `no-var` (error), `eqeqeq` (error), `no-unused-vars` (warn), `prefer-const` (warn)

### package.json
- `frontend/package.json` — declares `prettier` and `eslint` as dev dependencies with npm scripts:
  - `npm run format` — auto-format all files
  - `npm run format:check` — check formatting without writing
  - `npm run lint` — lint `script.js`
  - `npm run lint:fix` — auto-fix lint issues
  - `npm run quality` — run format check + lint together

### Dev scripts (project root)
- `scripts/format-frontend.sh` — auto-installs deps if needed, runs `prettier --write`
- `scripts/check-frontend.sh` — runs Prettier check + ESLint, exits non-zero on failure (CI-friendly)

## How to use

```bash
# Format all frontend files
./scripts/format-frontend.sh

# Check formatting + lint (use in CI or pre-commit)
./scripts/check-frontend.sh

# Or directly via npm inside frontend/
cd frontend
npm run quality
```

## Files changed
| File | Action |
|------|--------|
| `frontend/script.js` | Reformatted by Prettier |
| `frontend/style.css` | Reformatted by Prettier |
| `frontend/index.html` | Reformatted by Prettier |
| `frontend/package.json` | Created |
| `frontend/.prettierrc` | Created |
| `frontend/.prettierignore` | Created |
| `frontend/eslint.config.js` | Created |
| `scripts/format-frontend.sh` | Created |
| `scripts/check-frontend.sh` | Created |
| `.gitignore` | Added `frontend/node_modules/` and `frontend/package-lock.json` |

---

# Frontend Changes — UI Feature

## Feature 1: Dark/Light Theme Toggle Button

Added a dark/light mode toggle button fixed to the top-right corner of the UI.

### `frontend/index.html`
- Added `#themeToggle` button element before `.container`, fixed-positioned top-right
- Button contains two SVG icons: a **sun** (shown in dark mode) and a **moon** (shown in light mode)
- `aria-label` and `title` attributes set for accessibility; updated dynamically by JS
- Bumped CSS and JS cache-busting version query strings from `v=9` to `v=10`

### `frontend/style.css`
- Added `body.light-mode` CSS variable overrides for all theme-sensitive colors
- Added a broad transition rule on key elements so theme switches animate smoothly over 0.3s
- Added `.theme-toggle` styles: 40×40px circular fixed button, top-right, `z-index: 1000`
- Sun/moon icons swap using `opacity` + `transform` (rotate + scale) transitions

### `frontend/script.js`
- Added `initTheme()` — reads `localStorage` key `theme` on load and applies `light-mode` class
- Added `toggleTheme()` — toggles `body.light-mode`, persists to `localStorage`
- Added `updateToggleLabel(isLight)` — keeps `aria-label` / `title` in sync
- Wired `#themeToggle` click in `setupEventListeners()`

---

## Feature 2: Full Light Theme — Accessible Color System

Completed the light theme with a fully WCAG AA–compliant color system. Every previously hardcoded color was replaced with a CSS variable that is properly overridden in `body.light-mode`.

### `frontend/style.css` — variables expanded

All new/updated variables in `:root` (dark defaults) with `body.light-mode` overrides:

| Variable | Dark default | Light override | Notes |
|---|---|---|---|
| `--background` | `#0f172a` | `#f8fafc` | Page canvas |
| `--surface` | `#1e293b` | `#ffffff` | Sidebar, message bubbles |
| `--surface-hover` | `#334155` | `#f1f5f9` | Hover states |
| `--text-primary` | `#f1f5f9` | `#0f172a` | ~18:1 on light bg ✓ |
| `--text-secondary` | `#94a3b8` | `#475569` | ~5.9:1 on light bg ✓ |
| `--border-color` | `#334155` | `#cbd5e1` | Slightly stronger than before |
| `--shadow` | dark rgba | subtle rgba | Lighter opacity for light bg |
| `--focus-ring` | `rgba(37,99,235,0.25)` | `rgba(37,99,235,0.2)` | |
| `--welcome-bg` | `#1e3a5f` | `#eff6ff` | |
| `--welcome-border` | `#2563eb` | `#3b82f6` | |
| `--welcome-shadow` | `rgba(0,0,0,0.25)` | `rgba(0,0,0,0.07)` | Replaces hardcoded value |
| `--code-bg` | `rgba(0,0,0,0.25)` | `rgba(15,23,42,0.06)` | Replaces hardcoded value |
| `--source-link-color` | `#93c5fd` | `#1d4ed8` | ~5.1:1 on white ✓ |
| `--source-link-hover-color` | `#bfdbfe` | `#1e40af` | Darker on hover ✓ |
| `--source-link-bg` | `rgba(37,99,235,0.15)` | `rgba(37,99,235,0.07)` | |
| `--source-link-hover-bg` | `rgba(37,99,235,0.3)` | `rgba(37,99,235,0.14)` | |
| `--error-color` | `#f87171` | `#b91c1c` | ~5.8:1 on error-bg ✓ |
| `--error-bg` | `rgba(239,68,68,0.1)` | `rgba(239,68,68,0.07)` | |
| `--error-border` | `rgba(239,68,68,0.2)` | `rgba(185,28,28,0.22)` | |
| `--success-color` | `#4ade80` | `#15803d` | ~5.3:1 on success-bg ✓ |
| `--success-bg` | `rgba(34,197,94,0.1)` | `rgba(34,197,94,0.07)` | |
| `--success-border` | `rgba(34,197,94,0.2)` | `rgba(21,128,61,0.22)` | |
| `--toggle-bg` | `#1e293b` | `#ffffff` | |
| `--toggle-border` | `#334155` | `#cbd5e1` | |
| `--toggle-color` | `#94a3b8` | `#64748b` | |

---

## Feature 3: Migrate theme switching to `data-theme` attribute

Replaced the `body.light-mode` class approach with a `data-theme` attribute on the `<html>` element, following the standard pattern used by modern design systems.

### `frontend/index.html`
- Added `data-theme="dark"` to `<html>` as the explicit default — theme is declared in markup from the first paint, eliminating any flash of wrong theme
- Bumped cache-busting version strings to `v=11`

### `frontend/style.css`
- Added `color-scheme: dark` to `:root` — tells the browser to render native UI controls (scrollbars, inputs, selects) in dark mode by default
- Renamed `body.light-mode { … }` → `[data-theme="light"] { … }` and added `color-scheme: light` inside it — browser native controls now follow the active theme
- Updated both icon-state rules: `body.light-mode .theme-toggle .icon-*` → `[data-theme="light"] .theme-toggle .icon-*`

### `frontend/script.js`
- `initTheme()` — reads `localStorage` (defaulting to `'dark'`), then calls `document.documentElement.setAttribute('data-theme', saved)` instead of toggling a body class
- `toggleTheme()` — reads current value with `document.documentElement.getAttribute('data-theme')`, flips it, writes it back with `setAttribute`, and persists to `localStorage`
- `updateToggleLabel()` — unchanged; driven by the same `isLight` boolean

### Why `data-theme` on `<html>`

| | `body.light-mode` class | `[data-theme]` on `<html>` |
|---|---|---|
| Matches `:root` cascade | No — `:root` = `<html>`, body class can't override `:root` variables without a body-level specificity trick | Yes — `[data-theme]` sits on `<html>` so overrides cascade naturally |
| `color-scheme` propagation | Must be set on `<html>` or `:root` separately | Set directly on the themed element |
| Industry standard | Older pattern | Used by Radix UI, shadcn/ui, Tailwind dark mode |
| Scriptable | `classList.toggle` | `setAttribute` — same ergonomics, clearer intent |
