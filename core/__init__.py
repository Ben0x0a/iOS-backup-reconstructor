"""Core iOS backup reconstruction logic.

Defines: the public surface of the reconstruction engine.
Used by: launcher.cli, gui.interface, tests.
Depends on: core.reconstructor, core.models, config.settings.
"""

from config.settings import TOOL_NAME, TOOL_VERSION
from core.models import FileRecord, ReconstructionResult
from core.reconstructor import BackupError, inspect_backup, reconstruct_backup

__all__ = [
    "TOOL_NAME",
    "TOOL_VERSION",
    "BackupError",
    "FileRecord",
    "ReconstructionResult",
    "inspect_backup",
    "reconstruct_backup",
]
