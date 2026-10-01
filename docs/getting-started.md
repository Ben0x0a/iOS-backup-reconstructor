# Getting started

## Requirements

- Python 3.12 or newer
- [`uv`](https://docs.astral.sh/uv/) (recommended) or `pip`

## Install

### With uv

```bash
uv sync
```

`uv sync` installs from `pyproject.toml` and the committed `uv.lock`, so you get
exactly the dependency versions the project was tested against.

### With pip

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .\.venv\Scripts\Activate.ps1
python3 -m pip install -e .
```

## Locate a backup

A local iOS backup is a directory containing `Manifest.plist`, `Manifest.db`,
`Info.plist` and `Status.plist`, alongside two-character subdirectories of
hashed file blobs. Default locations:

| Platform | Path |
| --- | --- |
| macOS | `~/Library/Application Support/MobileSync/Backup/<UDID>` |
| Windows | `%APPDATA%\Apple Computer\MobileSync\Backup\<UDID>` |

You may pass either the directory or its `Manifest.plist`.

## Inspect before reconstructing

```bash
uv run python main.py /path/to/ios-backup /path/to/output --info-only
```

```json
{
  "backup": "/path/to/ios-backup",
  "date": "2026-04-13 11:29:13",
  "device": "iPhone SE",
  "encrypted": true,
  "ios": "14.0.1",
  "product": "iPhone SE (2nd generation)"
}
```

`encrypted: true` means you will need the backup password.

## Plan the output

A dry run writes only the traceability artefacts, listing where every file
*would* go, without reconstructing any content:

```bash
uv run python main.py /path/to/ios-backup /path/to/output --dry-run
```

## Reconstruct

```bash
uv run python main.py /path/to/ios-backup /path/to/output
```

### Long paths on Windows

A rebuilt iOS path is long before your destination is added, so many exceed
Windows' 260-character limit. The tool writes them anyway, using the
extended-length path form — nothing is skipped. The run reports how many were
affected (`stats.long_paths`), because a tool that does not handle long paths will
not be able to open those files afterwards.

A zip archive avoids the question entirely, since the limit applies when files are
extracted rather than when the archive is written:

```bash
uv run python main.py /path/to/ios-backup /path/to/output.zip --format zip
```

## Read the output

```text
output/
├── _traceability/
│   ├── ios-backup-reconstruct.provenance.traceability.json
│   └── ios-backup-reconstruct.file-manifest.traceability.csv
└── private/var/mobile/Library/SMS/sms.db
```

The provenance JSON records the run; the file manifest records one row per
`Manifest.db` record. See [formats/traceability.md](formats/traceability.md).

## Exit codes

| Code | Meaning |
| --- | --- |
| `0` | Success, every row handled |
| `1` | The run failed; no output was produced |
| `2` | Completed with failed rows, under `--continue-on-error` |
