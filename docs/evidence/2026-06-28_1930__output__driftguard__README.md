# DriftGuard

Detect drift between your Prisma schema, OpenAPI spec, and TypeScript types - before it causes bugs.

## Quick start

```bash
npx driftguard check
```

DriftGuard auto-discovers `prisma/schema.prisma`, `openapi.yaml`, and `tsconfig.json` by walking up from your current directory. Zero config for standard projects.

## Installation

```bash
npm install -g driftguard
# or use without installing:
npx driftguard check
```

## CLI reference

### `driftguard check`

```
Options:
  --config <path>           Path to driftguard.config.ts or .json
                            Default: auto-discover in cwd and parent dirs
  --prisma <path>           Override prisma schema path
  --openapi <path>          Override openapi spec path
  --tsconfig <path>         Override tsconfig path
  --include <glob>          TypeScript include glob (repeatable)
  --entity <name>           Check a specific entity only (repeatable)
  --format <text|json|github-annotations>
                            Output format (default: text)
  --severity <error|warning|all>
                            Minimum severity to report (default: all)
  --no-exit-code            Always exit 0 (advisory-only runs)
  --cache / --no-cache      Enable parse cache (default: --cache)
  --cache-dir <path>        Cache directory (default: node_modules/.cache/driftguard)
  --sources <list>          Comma-separated sources to include
                            (default: prisma,openapi,typescript)

Exit codes:
  0   No drift found (or --no-exit-code)
  1   Drift issues found at error severity
  2   Parse/config error
```

### `driftguard serve`

```
Options:
  --transport <stdio|sse>   MCP transport (default: stdio)
  --port <number>           Port for SSE transport (default: 3333)
  --config <path>           Same as check --config
  --watch / --no-watch      Watch source files (default: --watch)
```

## Configuration file

Copy `driftguard.config.example.ts` to your project root:

```typescript
export default {
  prisma: "./prisma/schema.prisma",
  openapi: "./docs/openapi.yaml",
  typescript: {
    include: ["src/**/*.ts"],
    exclude: ["**/*.test.ts"],
  },
  ignore: [
    "User.password",   // never expose in API
    "AuditLog.*",      // internal table
  ],
  severity: {
    "missing-in-source": "error",
    "type-mismatch": "error",
    "nullability-mismatch": "warning",
    "entity-not-in-source": "warning",
  },
  entities: {
    // When TS name differs from Prisma/OpenAPI name:
    UserProfile: { prisma: "user_profile", openapi: "UserObject" },
  },
};
```

## Environment variables

| Variable | Description |
|---|---|
| `DRIFTGUARD_CACHE_DIR` | Override cache directory |
| `DRIFTGUARD_NO_COLOR` | Set to `1` to disable ANSI colors |
| `DRIFTGUARD_LOG_LEVEL` | Set to `debug` for verbose stderr logging |
| `NO_COLOR` | Standard no-color variable (also respected) |

## Programmatic API

```typescript
import { check, buildEntityMap, loadConfig } from "driftguard";

const config = await loadConfig({ cwd: process.cwd() });
const report = await check(config);

if (report.exitCode === 1) {
  console.log(`Found ${report.summary.errors} errors`);
  for (const issue of report.issues) {
    console.log(issue.message);
  }
}
```

## MCP server (for Cursor / Claude Code)

Add to your `.cursor/mcp.json` or `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "driftguard": {
      "command": "npx",
      "args": ["driftguard", "serve"]
    }
  }
}
```

Available tools:
- `check_drift` - run a full drift check, optionally scoped to one entity
- `get_entity_map` - see how each entity is defined across all three sources
- `list_entities` - list all discovered entities with drift status

## GitHub Action

```yaml
- name: Check API drift
  uses: driftguard/action@v1
  with:
    config: ./driftguard.config.json   # optional
    severity: error                    # optional, default: error
```

## Drift rules

| Situation | Issue kind | Default severity |
|---|---|---|
| Field present in prisma + openapi but missing from typescript | `missing-in-source` | error |
| Canonical types differ (e.g. prisma: number, ts: string) | `type-mismatch` | error |
| Nullable flag differs between sources | `nullability-mismatch` | warning |
| Entity in 2 sources but absent from a 3rd | `entity-not-in-source` | warning |
| Entity in only 1 source | (not reported) | - |

## What DriftGuard does NOT check

- Zod schema shapes (static AST analysis of Zod's fluent builder DSL is not reliable - ships as follow-on after interface coverage is proven stable)
- Database column types vs Prisma types (Prisma handles that)
- API response validation at runtime (use a runtime validator for that)

## Development

```bash
git clone <repo>
cd driftguard
npm install
npm test          # run tests
npm run build     # build dist/
npm run typecheck # type check only
```

## Contributing

1. Add a test fixture in `tests/fixtures/` that demonstrates the issue
2. Write the failing test
3. Fix the implementation
4. All three normalizer lookup tables (Prisma, OpenAPI, TypeScript) must stay in sync with `src/engine/normalizer.ts`
