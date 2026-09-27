"""GUI launcher.

Defines: the GUI entry point, translating a missing-PySide6 failure into an
exit code rather than a traceback.
Used by: main.
Depends on: gui.interface.
"""

from __future__ import annotations

import logging
import sys

from gui.interface import launch

_LOG = logging.getLogger(__name__)


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s", stream=sys.stderr)
    try:
        return launch()
    except RuntimeError as exc:
        _LOG.error(f"{exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
