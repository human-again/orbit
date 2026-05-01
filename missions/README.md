# Mission Templates

Ready-made `mission.md` + `backlog.json` pairs for common engineering tasks. Copy one into your project and point Orbit at it.

| Template | What it covers |
|---|---|
| [`rest-api/`](rest-api/) | CRUD endpoints, request validation, structured error responses |
| [`auth-service/`](auth-service/) | Login, tokens, password hashing, validation middleware |
| [`db-migration/`](db-migration/) | Schema change with up/down migration and model tests |
| [`python-cli/`](python-cli/) | CLI entry point, argument parsing, exit codes |
| [`frontend-component/`](frontend-component/) | UI component, props, accessibility, snapshot tests |

## Usage

```bash
# Copy a template into your project
cp -r missions/rest-api/ /path/to/my-project/

cd /path/to/my-project

# Edit mission.md to match your actual objective and codebase
# Edit backlog.json to match your tasks

# Run Orbit
python /path/to/orbit/orchestrator.py --config runtime/config.json
```

## Adding your own template

Templates are just a `mission.md` + `backlog.json`. Follow the pattern in any existing template. PRs welcome.
