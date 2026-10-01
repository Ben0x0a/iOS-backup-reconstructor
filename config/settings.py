"""Operator-tuneable constants for the iOS backup reconstructor.

Defines: tool identity, traceability artefact names, output layouts, and the
default backup passwords tried for encrypted backups. Everything here is a
value an operator may reasonably want to change without editing logic.
Used by: core.reconstructor, core.models, gui.interface, tests.
Depends on: nothing.
"""

from __future__ import annotations

# Tool identity. Written into every traceability artefact so reconstructed
# evidence is attributable to the tool and version that produced it.
TOOL_NAME = "ios-backup-reconstruct"
TOOL_VERSION = "0.2.2"

# Traceability artefact names. Both carry the tool tag so an artefact found
# outside its output folder is still attributable.
# Consumed by: core.reconstructor (write_trace_folder, write_trace_zip,
# write_failure_report, output_has_tool_collision), core.models.
TRACEABILITY_DIR_NAME = "_traceability"
TRACEABILITY_PROVENANCE_NAME = f"{TOOL_NAME}.provenance.traceability.json"
TRACEABILITY_FILE_MANIFEST_NAME = f"{TOOL_NAME}.file-manifest.traceability.csv"
FAILURE_REPORT_DIR_NAME = "failed_traceability_reports"

# Output layouts. "backup" keeps Apple backup domains as top-level folders;
# "filesystem" maps domains to filesystem-like paths via config/domain_maps.
# Consumed by: core.reconstructor (parse_args, normalise_output_layout).
OUTPUT_LAYOUTS = ("backup", "filesystem")
DEFAULT_OUTPUT_LAYOUT = "filesystem"

# Passwords tried, in order, ONLY when --try-default-passwords is given. These
# are the defaults commonly set by acquisition tools, not a cracking wordlist.
# Opt-in by design: guessing is an examiner's decision to make and account for,
# and the choice is recorded in the provenance artefact.
# Consumed by: core.reconstructor (prepare_manifest_db).
DEFAULT_BACKUP_PASSWORDS = ("1234", "12345", "123456", "password")

# The files a backup must have. Only these two are load-bearing: Manifest.plist
# carries the encryption state and key material, Manifest.db the file table.
# Consumed by: core.reconstructor (resolve_backup_dir).
REQUIRED_BACKUP_FILES = ("Manifest.plist", "Manifest.db")

# Files that carry provenance only, and that older backups may not have.
# WHY optional: nothing in reconstruction or decryption reads them, so requiring
# them rejected backups the tool could otherwise handle perfectly. Their absence
# is recorded in the provenance artefact rather than passed over.
# Consumed by: core.reconstructor, core.decryptor.
OPTIONAL_BACKUP_FILES = ("Info.plist", "Status.plist")

# Read/decrypt chunk size, in bytes. Consumed by: core.reconstructor.
CHUNK_SIZE = 1024 * 1024

# Threshold above which zip members spool to disk instead of memory, in bytes.
# Consumed by: core.reconstructor (reconstruct_to_zip).
ZIP_SPOOL_MAX_SIZE = 64 * 1024 * 1024
