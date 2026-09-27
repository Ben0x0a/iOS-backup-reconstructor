#!/usr/bin/env python3
"""Application entry point.

Defines: argument-free dispatch between the GUI and the CLI.
Used by: the user, directly (`python main.py ...`).
Depends on: launcher.gui, launcher.cli.
"""

from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    # No arguments means the GUI: the CLI requires a backup and an output path,
    # so a bare invocation can only sensibly mean "open the interface".
    if not args or args[0] in ("--gui", "gui"):
        from launcher.gui import main as gui_main

        return gui_main()

    from launcher.cli import main as cli_main

    return cli_main(args)


if __name__ == "__main__":
    raise SystemExit(main())
