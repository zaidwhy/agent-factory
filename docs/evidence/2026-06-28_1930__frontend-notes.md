# DriftGuard - Frontend Notes

## How to install and run

```bash
cd output/driftguard
npm install
npm run build          # produces dist/ via tsup
npm run dev            # tsc --watch for development
```

Requires **Node.js >= 20.0.0 < 22** (LTS). Verified path: `node --version`.

## Run the CLI

```bash
# After building:
node dist/cli/index.js check --help

# Or install globally:
npm install -g .
driftguard check

# Or use npx (after npm publish):
npx driftguard check

# Against a real project:
driftguard check --prisma ./prisma/schema.prisma --openapi ./openapi.yaml
driftguard check --format json
driftguard check --entity User
driftguard check --format github-annotations   # for CI

# MCP server (stdio for Cursor / Claude Code):
driftguard serve
driftguard serve --transport sse --port 3333
```

## Run tests

```bash
npm test               # vitest run (all tests)
npm run test:watch     # vitest --watch
npm run test:coverage  # coverage report in coverage/
```

Tests live in `tests/`. Unit tests for each engine module are in `tests/unit/`. Integration tests that run the full pipeline are in `tests/integration/`.

**Note**: Integration tests require the parsers to successfully load their dependencies (`@prisma/internals`, `ts-morph`). Run `npm install` first.

## Backend it expects

The CLI imports from these modules which must be implemented by the backend engineer:

| Module | Status | Needed for |
|---|---|---|
| `src/parsers/prisma.ts` | Written | `buildEntityMap()` |
| `src/parsers/openapi.ts` | Written | `buildEntityMap()` |
| `src/parsers/typescript.ts` | Written | `buildEntityMap()` |
| `src/engine/normalizer.ts` | Written | All parsers |
| `src/engine/entity-map.ts` | Written | `buildEntityMap()` |
| `src/engine/comparator.ts` | Written | `check()` |
| `src/config/loader.ts` | Written | All CLI commands |
| `src/config/discovery.ts` | Written | `loader.ts` |
| `src/cache/index.ts` | Written | `src/index.ts` |
| `src/mcp/server.ts` | Written | `driftguard serve` |
| `src/mcp/watch.ts` | Written | `driftguard serve` |

All modules are written. The package should typecheck and build.

## Environment variables (.env.example)

```bash
DRIFTGUARD_CACHE_DIR=<path>     # override default node_modules/.cache/driftguard
DRIFTGUARD_NO_COLOR=1           # disable ANSI colors in text reporter
DRIFTGUARD_LOG_LEVEL=debug      # enable debug logging to stderr
NO_COLOR=1                      # standard no-color env var (also respected)
```

## What the frontend engineer wrote

### New files created:
- `src/cli/report/color.ts` - ANSI color utility (util.styleText + fallback)
- `src/cli/report/text.ts` - complete rewrite: added renderProgress(), renderFatalError(), renderReport() + improved formatText()
- `tests/unit/parsers/prisma.test.ts`
- `tests/unit/parsers/openapi.test.ts`
- `tests/unit/parsers/typescript.test.ts`
- `tests/fixtures/*/expected-report.json` (all three fixtures)
- `.eslintrc.json`

### Bugs fixed in existing files:
- `src/types/drift.ts`: SourceKind imported from wrong module (canonical -> entity)
- `src/types/config.ts`: SourceKind imported from wrong module (canonical -> entity)
- `src/engine/comparator.ts`: SourceKind imported from wrong module (canonical -> entity)
- `src/cli/check.ts`: `loadConfigInternal` -> `loadConfig` (function name mismatch)
- `src/cli/serve.ts`: `loadConfigInternal` -> `loadConfig` (function name mismatch)
- `src/parsers/typescript.ts`: removed unused top-level `glob` import from `fs/promises`

### Extended:
- `src/cli/check.ts`: added renderProgress() and renderFatalError() calls for loading/error states; added error type imports

## Terminal output layout (text format)

```
============================================================
DriftGuard  scanned 3 entities  2 errors  1 warning
Scanned: Jan 15 2024 10:30:00  |  Config: ./driftguard.config.ts
Sources: prisma, openapi, typescript
============================================================

Entity: User  (2 errors)  [prisma · openapi · typescript]
--------------------------------------------------
  [ERROR]   type-mismatch "email"
            Type mismatch for "User.email": ...
              prisma       String
              openapi      string (email)
              typescript   string | null  (nullable)

  [ERROR]   nullability-mismatch "createdAt"
            ...

Entity: Product  (1 warning)  [prisma · openapi]
--------------------------------------------------
  [WARN]    entity-not-in-source (entity level)
            Present in:   prisma, openapi
            Missing from: typescript

============================================================
Summary: 3 issues, 2 errors, 1 warning
Entities checked: User, Product, Order
Entities with issues: 2
By kind: type-mismatch: 1  |  nullability-mismatch: 1  |  entity-not-in-source: 1
============================================================

  ✗  Exit 1 - fix errors to pass
```

Color is disabled automatically when piped (`|`), when `NO_COLOR=1`, or `DRIFTGUARD_NO_COLOR=1`.
