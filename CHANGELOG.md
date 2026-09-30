# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] — 2026-09-30

### Added

- **`--mode decrypt`** — produce the same backup with its content in the clear,
  keeping the hash-addressed layout, instead of reconstructing a directory tree.
  The output is a structurally valid *unencrypted* backup, so tools that read iOS
  backups but cannot decrypt them can open it. Verified against an independent
  implementation (mf-scan), which reads the result as an unencrypted backup and
  confirms the recomputed digests with its own SHA-1 attestation.

  `--mode rebuild` (the default) is unchanged and still decrypts on the way.

  Because an encrypted backup records each `Digest` as the SHA-1 of the
  *ciphertext* and an unencrypted one records the SHA-1 of the *content*, three
  things are rewritten and all three are recorded in the traceability output:
  `Manifest.plist` (`IsEncrypted` false, key material removed), each `Files.file`
  record (`EncryptionKey` removed, `Digest` recomputed), and `Manifest.db` itself.
  Nothing else changes — records are re-encoded from the same decoded object graph,
  so uninterpreted fields survive byte-for-byte.

- The file manifest gains `manifest_digest_original` and
  `manifest_digest_rewritten` columns, so a rewritten digest is always auditable
  against the source's own value. Both are empty in `rebuild` mode.

- GUI mode selector, with the layout and output-type controls disabled when they
  do not apply.

### Fixed

- **Keybag class keys are delimited by `CLAS`, not by `UUID`.** The parser started
  a new protection-class record at each `UUID` tag, so a keybag written without a
  per-class `UUID` yielded **no class keys at all** — and the failure surfaced as
  *"Could not unlock backup keybag. Check the backup password."* when the password
  was correct. Real iOS keybags do carry those UUIDs, so this only bit keybags
  written otherwise, but the misleading error would have sent an examiner after
  entirely the wrong problem. `CLAS` is the tag that defines a class, so it is now
  the one that delimits — matching mf-scan's independent parser.

- A keybag containing no protection-class keys is now reported as malformed rather
  than as a bad password.

### Changed

- `--layout`, `--domain-map` and `--format` are refused with `--mode decrypt`
  rather than silently ignored.

## [0.1.1] — 2026-09-28

### Fixed

- **`CameraRollDomain` and `MediaDomain` produced a doubled path segment** under
  the default `filesystem` layout. Both were mapped to
  `private/var/mobile/Media`, but their `relativePath` values already begin with
  `Media/`, so files were written to `private/var/mobile/Media/Media/…`. Both now
  map to `private/var/mobile`. Verified against 2,638 rows of a real iPhone
  reconstruction, where 35 paths were affected; the fix reduces doubled-segment
  paths from 39 to 4, and those 4 are genuine nested directories on the device
  (`model.mdl/model/model`, `Recents/Recents`), not mapping errors.

  A `MediaDomain` file whose `relativePath` did *not* begin with `Media/` was
  also misplaced — under `Media/Library/…` rather than `Library/…`.

  **If you reconstructed a backup with 0.1.0 using the default layout**, camera
  roll and media paths in that output carry an extra `Media` segment. The file
  contents and all recorded digests are unaffected; only the output paths, and
  the `output_path` column of the file manifest, are wrong. Re-running with
  0.1.1 produces the corrected tree.

## [0.1.0] — 2026-09-27

First public release.

### Added

- Reconstruct an iOS local backup from `Manifest.plist` and `Manifest.db` into a
  folder or a zip archive, in either a filesystem-like layout (the default) or
  the raw backup-domain layout.
- Decryption of encrypted backups: keybag parsing, PBKDF2 key derivation,
  AES key unwrapping and AES-CBC file decryption.
- Forensic traceability on every run — a provenance record (tool version, host,
  source manifest digests, device metadata, redacted command line) and a
  per-record file manifest with source and output SHA-256 digests.
- Domain-to-path mapping driven by editable YAML maps with iOS version ranges
  (`config/domain_maps/`).
- `--dry-run` to plan output paths without reconstructing content.
- `--continue-on-error` to keep successful files when some rows fail; the default
  is to fail closed and write a failure report instead.
- `--info-only` to print backup metadata without reconstructing.
- `--try-default-passwords` to opt in to trying the backup passwords commonly set
  by acquisition tools. Off by default, and recorded in the provenance artefact.
- Progress reporting: a terminal counter for the CLI (`--quiet` to suppress) and a
  progress bar in the GUI.
- Cancellation in the GUI. A cancelled run keeps what it wrote and is recorded as
  `cancelled` in the traceability output; the CLI reports exit code `3`.
- PySide6 interface with drag-and-drop input and output paths, an encryption
  check, and reconstruction on a background thread.
- Documentation in `docs/` covering the backup format, the encryption scheme, the
  CLI, task workflows, the traceability formats and the library API.

### Security

- The CLI does not accept a backup password as an argument, so it cannot leak into
  shell history or the process table. Passwords are read via `getpass`, and only
  when stdin is a terminal.
- Output path segments from the backup are sanitised, and output is always written
  relative to the chosen destination, so a crafted manifest cannot escape it.
