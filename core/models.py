"""Data containers shared across the reconstruction pipeline.

Defines: `FileRecord` (one `Manifest.db` row resolved to source and output
paths) and `ReconstructionResult` (the outcome reported by a run).
Used by: core.reconstructor, gui.interface, launcher.cli.
Depends on: config.settings.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from config.settings import (
    TRACEABILITY_DIR_NAME,
    TRACEABILITY_FILE_MANIFEST_NAME,
    TRACEABILITY_PROVENANCE_NAME,
)


@dataclass
class FileRecord:
    """One `Manifest.db` row, resolved to its backup blob and output path."""

    file_id: str
    domain: str
    relative_path: str
    flags: int
    metadata: dict[str, Any]
    source_path: Path
    output_path: PurePosixPath


@dataclass
class ReconstructionResult:
    """Aggregate outcome of a reconstruction run, as reported to the caller."""

    output: Path
    output_format: str
    output_layout: str
    encrypted: bool
    stats: dict[str, int]
    dry_run: bool = False
    cancelled: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "output": str(self.output),
            "format": self.output_format,
            "layout": self.output_layout,
            "encrypted": self.encrypted,
            "dry_run": self.dry_run,
            "cancelled": self.cancelled,
            "stats": self.stats,
            "traceability": (
                f"{TRACEABILITY_DIR_NAME}/{TRACEABILITY_PROVENANCE_NAME} and "
                f"{TRACEABILITY_DIR_NAME}/{TRACEABILITY_FILE_MANIFEST_NAME}"
            ),
        }
