# `ios-backup-reconstruct`

```text
python main.py <backup> <output> [options]
```

## Positional arguments

| Argument | Description |
| --- | --- |
| `backup` | An iOS backup directory, or its `Manifest.plist` |
| `output` | Destination folder or `.zip` path. Must not be inside `backup` |

## Options

Listed in the order an operator uses them.

| Option | Default | Description |
| --- | --- | --- |
| `--info-only` | off | Print backup metadata as JSON and exit. Does not need the password or the `cryptography` package |
| `--dry-run` | off | Write only traceability and planned output paths; reconstruct no content |
| `--layout {filesystem,backup}` | `filesystem` | `filesystem` maps domains to device-like paths; `backup` keeps domains as top-level folders |
| `--domain-map PATH` | shipped maps | A YAML file, or a directory of them, overriding the domain-to-path mapping |
| `--format {auto,folder,zip}` | `auto` | `auto` selects zip on Windows, folder elsewhere |
| `--force` | off | Append to an existing output folder, or overwrite an existing zip |
| `--try-default-passwords` | off | Before prompting, try the backup passwords commonly set by acquisition tools |
| `--continue-on-error` | off | Keep successfully reconstructed files when some rows fail |
| `--quiet` | off | Suppress the progress counter |
| `--verbose` | off | Log debug-level diagnostics to stderr |
| `--version` | — | Print the tool name and version |

## Output

On success the result is printed to stdout as JSON, so it can be piped:

```bash
python main.py /path/to/backup /path/to/out | jq .stats
```

```json
{
  "output": "/path/to/out",
  "format": "folder",
  "layout": "filesystem",
  "encrypted": false,
  "dry_run": false,
  "stats": {"records": 2, "written": 1, "missing": 0, "failed": 0, "directories": 1},
  "traceability": "_traceability/... and _traceability/..."
}
```

Diagnostics go to stderr via `logging`; only the result goes to stdout.

While reconstructing to a terminal, a one-line counter is written to stderr. It
is suppressed automatically when stderr is not a TTY — so `2>logfile` and pipes
stay clean — and can be turned off with `--quiet`.

## Exit codes

| Code | Meaning |
| --- | --- |
| `0` | Success |
| `1` | Failure; no output produced. A failure report is written under `failed_traceability_reports/` |
| `2` | Completed with failed rows, under `--continue-on-error` |
| `3` | Cancelled; the output is incomplete and is recorded as `cancelled` |

## Passwords

There is no `--password` option, by design; see
[Encryption](../concepts/encryption.md#passwords). The tool prompts securely,
and only tries acquisition-tool defaults when you pass
`--try-default-passwords`. The choice is recorded in the provenance artefact.
