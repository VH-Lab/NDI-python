"""napariViewLightsheet - open a lightsheetZarrPyramid in napari.

Console-script entry point declared in NDI-python's ``pyproject.toml``.

Usage
-----

    napariViewLightsheet <session-path> --pyramid <id> [--reduction mean|max]
                        [--channel N] [--level L] [--no-controls]
                        [--name NAME]

The command line is built by ``ndi.fun.doc.lightsheet.viewCommand`` in
NDI-matlab. Keep the flag set in sync there.

Why a console script and not a napari plugin
--------------------------------------------

The MATLAB GUI shells out to
``/usr/local/bin/napariViewLightsheet``, a small wrapper that scrubs
``LD_LIBRARY_PATH`` / ``DYLD_*`` (MATLAB pollutes them) and then execs
this console script. If the Python side were a napari plugin the wrapper
would still need to exist -- MATLAB's library paths kill any Python
started from MATLAB -- but the plugin would then have to be installed
into whatever napari environment the user has, and there is no way for
the MATLAB manager to check whether it is. A console script installed
alongside NDI-python is what the wrapper points at and what the manager
knows how to depend on.

This file is currently a scaffold: it parses arguments, opens the
session, resolves the pyramid document, and exits with a message that
says which piece is still to land. The reader lives in
:mod:`ndi.lightsheet.pyramid_reader`; that is where dask + napari get
wired up.
"""

from __future__ import annotations

import argparse
import sys
from typing import Sequence


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="napariViewLightsheet",
        description="Open a lightsheetZarrPyramid from an NDI session in napari.",
    )
    p.add_argument(
        "session_path",
        help="Path to the ndi.session.dir on disk (its top-level directory).",
    )
    p.add_argument(
        "--pyramid",
        required=True,
        help="Document id of the lightsheetZarrPyramid to open.",
    )
    p.add_argument(
        "--reduction",
        choices=("mean", "max"),
        default=None,
        help="Open the sibling pyramid with this reduction instead of "
        "the one --pyramid names.",
    )
    p.add_argument(
        "--channel",
        type=int,
        default=None,
        help="1-based channel index to display. Omit to add every "
        "channel as its own napari layer.",
    )
    p.add_argument(
        "--level",
        type=int,
        default=None,
        help="0-based level to display at startup. Omit to let the "
        "viewer pick from the window size.",
    )
    p.add_argument(
        "--no-controls",
        dest="controls",
        action="store_false",
        default=True,
        help="Do not dock the reduction / channel / level panels.",
    )
    p.add_argument(
        "--name",
        default=None,
        help="Layer name. Omit to use the pyramid document's label.",
    )
    return p


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    # Lazy imports so ``--help`` does not pay the napari / ndi cost.
    try:
        import ndi  # noqa: F401
    except ImportError as exc:  # pragma: no cover
        print(f"ndi package not importable: {exc}", file=sys.stderr)
        return 2

    from ndi.lightsheet.pyramid_reader import PyramidReader

    try:
        reader = PyramidReader.open(args.session_path, pyramid_id=args.pyramid)
    except NotImplementedError as exc:
        print(f"napariViewLightsheet: {exc}", file=sys.stderr)
        print(
            "This is the scaffold PR. See README-lightsheet-zarr.md at "
            "the top of ndi/lightsheet/ for the next steps.",
            file=sys.stderr,
        )
        return 3

    # The rest of the wiring lands with the PyramidReader implementation:
    #   import napari
    #   viewer = napari.Viewer()
    #   arrays = reader.multiscale(reduction=args.reduction, channel=args.channel)
    #   viewer.add_image(arrays, name=args.name or reader.default_name,
    #                    multiscale=True)
    #   if args.controls: reader.attach_controls(viewer)
    #   napari.run()

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
