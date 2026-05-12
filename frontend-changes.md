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
