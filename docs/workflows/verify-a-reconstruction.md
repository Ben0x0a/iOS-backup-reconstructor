# Verify a reconstruction

Every run produces the evidence needed to check itself.

## Confirm the source was unchanged

`ios-backup-reconstruct.provenance.traceability.json` records SHA-256 digests of
`Manifest.plist`, `Manifest.db`, `Info.plist` and `Status.plist` as they were
read. Re-hash the source backup and compare:

```bash
shasum -a 256 /path/to/backup/Manifest.db
jq -r '.backup.manifest_db_sha256' \
  out/_traceability/ios-backup-reconstruct.provenance.traceability.json
```

## Confirm each file arrived intact

The file manifest carries `source_sha256` and `output_sha256` per row.

For an **unencrypted** backup the two must be identical — the blob is copied
verbatim:

```bash
awk -F, 'NR>1 && $12=="written" && $7!=$8 {print "MISMATCH:", $3}' \
  out/_traceability/ios-backup-reconstruct.file-manifest.traceability.csv
```

For an **encrypted** backup they differ by definition: `source_sha256` is the
ciphertext as stored, `output_sha256` the decrypted plaintext. Compare
`output_size` against `declared_size` instead.

## Confirm nothing was silently dropped

```bash
jq '.stats' out/_traceability/ios-backup-reconstruct.provenance.traceability.json
```

`records` must equal `written + missing + failed + directories`. A
`missing_source` row means `Manifest.db` listed a file whose blob is absent
from the backup — a property of the acquisition, not of the reconstruction.

## Confirm the output paths

Each row's `output_path` is the final destination path, not a temporary one.
Spot-check that the files named there exist.
