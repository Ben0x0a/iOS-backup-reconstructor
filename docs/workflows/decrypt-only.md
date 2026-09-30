# Decrypt without rebuilding

`--mode decrypt` produces the **same backup with its content in the clear**. The
output keeps the backup's own hash-addressed layout, so it is a structurally valid
unencrypted backup that any tool reading iOS backups can open — including tools
that cannot read encrypted ones.

```bash
uv run python main.py /path/to/encrypted-backup /path/to/output --mode decrypt
```

```text
output/
├── Manifest.plist          IsEncrypted false, key material removed
├── Manifest.db             decrypted, metadata rewritten
├── Info.plist              copied unchanged
├── Status.plist            copied unchanged
├── 3d/3d0d7e5fb2ce2888…    decrypted blob
└── _traceability/          provenance + per-file manifest
```

## Which mode do I want?

| Goal | Mode |
| --- | --- |
| Browse the device's files by name | `--mode rebuild` (the default) |
| Feed the backup to another tool that cannot decrypt | `--mode decrypt` |
| Both | Decrypt first, then rebuild from the decrypted copy — or just rebuild, which decrypts on the way |

`--mode rebuild` already decrypts when it needs to; `--mode decrypt` exists for when
you want the backup itself rather than a reconstructed tree.

## What is rewritten, and why it has to be

This is the part to understand before using the output as evidence.

An encrypted backup records each file's `Digest` as the **SHA-1 of the ciphertext
as stored**. An unencrypted backup records the **SHA-1 of the content**. Decrypting
the blobs without touching the manifest would leave every digest mismatched, and
the output would read as corrupt to any tool that verifies it.

So three things change:

| What | Change |
| --- | --- |
| `Manifest.plist` | `IsEncrypted` → `false`; `BackupKeyBag` and `ManifestKey` removed |
| Each `Files.file` record | `EncryptionKey` removed; `Digest` replaced with the SHA-1 of the plaintext |
| `Manifest.db` | Decrypted, then updated in place with those records |

Nothing else is touched. The metadata records are re-encoded from the same decoded
object graph, so fields this tool does not interpret survive byte-for-byte.

Every rewrite is recorded:

- `_traceability/…provenance.traceability.json` carries a `rewritten_metadata`
  block naming each change.
- The file manifest gains two columns, `manifest_digest_original` and
  `manifest_digest_rewritten`, so the original ciphertext digest is never lost.

## Edge cases

**A file the manifest lists but the backup does not hold** cannot be decrypted. Its
row keeps the digest the source recorded (that is the only record of that file's
content), but its wrapped key is still removed — no key material survives in an
output that declares itself unencrypted. The row is reported as `missing_source`.

**A file with no recorded digest** keeps none. Adding one would invent metadata the
source never held.

**An unencrypted source** is refused, rather than silently copied:

```text
ERROR: This backup is not encrypted, so there is nothing to decrypt.
Use --mode rebuild to reconstruct it into a filesystem-like tree.
```

**Flags that do not apply** (`--layout`, `--domain-map`, `--format`) are an error,
not a silent no-op — passing one means you expected something the mode cannot do.

## Verifying the result

The decrypted output should verify against any independent backup reader. A useful
check with [mf-scan](https://github.com/Ben0x0a):

```bash
mf-scan ios-backup info    /path/to/output --dir-mode
mf-scan ios-backup rebuild /path/to/output --dir-mode --to ./rebuilt
```

`info` should report the backup as unencrypted with the expected file count, and
`rebuild`'s `export-report.json` should show `stored_integrity: verified` for every
file that carried a digest — an independent confirmation that the recomputed
digests are right.
