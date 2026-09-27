# Traceability artefacts

Every run writes two files into `_traceability/` inside the output folder or
zip. Both filenames carry the tool tag, so an artefact separated from its
output folder is still attributable.

```text
_traceability/
├── ios-backup-reconstruct.provenance.traceability.json
└── ios-backup-reconstruct.file-manifest.traceability.csv
```

When a run fails closed, the same pair is written to
`failed_traceability_reports/<output-name>-<UTC timestamp>/` instead.

## Provenance JSON

One object describing the run.

| Key | Meaning |
| --- | --- |
| `tool`, `tool_version` | Which build produced the output |
| `created_utc` | ISO-8601 UTC timestamp of the run |
| `host.system`, `host.release`, `host.python` | Execution environment |
| `command` | The command line, with any password argument redacted |
| `backup.path` | Source backup directory |
| `backup.manifest_plist_sha256` | SHA-256 of `Manifest.plist` as read |
| `backup.manifest_db_sha256` | SHA-256 of `Manifest.db` as read (ciphertext, if encrypted) |
| `backup.info_plist_sha256` | SHA-256 of `Info.plist` as read |
| `backup.status_plist_sha256` | SHA-256 of `Status.plist` as read |
| `backup.encrypted` | Whether the backup was encrypted |
| `backup.manifest_version`, `backup.system_domains_version`, `backup.manifest_date` | Backup-level metadata |
| `backup.status.*` | Snapshot state, whether the backup was full, its date |
| `backup.device.*` | Device name, product name and type, iOS version, serial, identifier |
| `output.path`, `output.format`, `output.layout` | What was produced and how |
| `output.domain_map`, `output.domain_map_name`, `output.domain_map_ios_versions` | Which mapping was applied |
| `output.dry_run`, `output.continue_on_error` | Which mode the run used |
| `output.try_default_passwords` | Whether acquisition-tool default passwords were tried |
| `output.cancelled` | Whether the operator stopped the run early, leaving an incomplete tree |
| `stats` | `records`, `written`, `missing`, `failed`, `directories` |

The password is never recorded, in any form.

## File manifest CSV

One row per `Manifest.db` record, written UTF-8 with a header.

| Column | Meaning |
| --- | --- |
| `file_id` | `fileID` from `Manifest.db`; the blob's filename |
| `domain` | Backup domain |
| `relative_path` | Path within the domain |
| `flags` | `1` = file, `2` = directory record |
| `source_path` | Absolute path of the source blob |
| `output_path` | Final destination path (folder output) or archive member name (zip) |
| `source_sha256` | Digest of the bytes read from the backup |
| `output_sha256` | Digest of the bytes written to the output |
| `source_size` | Size of the source blob on disk |
| `output_size` | Bytes written |
| `declared_size` | `Size` from the record's metadata, if present |
| `status` | See below |
| `error` | Failure message, when `status` is `failed` |

### Status values

| Status | Meaning |
| --- | --- |
| `written` | Content reconstructed successfully |
| `directory_record` | A `flags = 2` row; a directory was created. Not a missing file |
| `missing_source` | `Manifest.db` lists the file, but its blob is absent from the backup |
| `planned` | `--dry-run` only: the file would have been written here |
| `failed` | Reconstruction raised; see `error` |
| `pending` | Transient; never present in a completed manifest |

### Interpreting the digests

For an **unencrypted** backup, `source_sha256` and `output_sha256` are equal for
every `written` row: the blob is copied verbatim.

For an **encrypted** backup they necessarily differ — the source digest covers
the stored ciphertext, the output digest the decrypted plaintext. Compare
`output_size` with `declared_size` instead.

`declared_size` is recorded but never enforced on unencrypted output, so a
mismatch indicates stale metadata in the backup rather than data loss.
