"""ndi.lightsheet - lightsheet OME-Zarr pyramid tools for NDI sessions.

Mirrors +ndi/+fun/+doc/+lightsheet in NDI-matlab. The primary consumer is
the ``napariViewLightsheet`` console script (see :mod:`ndi.lightsheet.napari_view`),
which the MATLAB GUI shell-execs via
``/usr/local/bin/napariViewLightsheet``. The console script reads
``lightsheetZarrPyramid`` + ``lightsheetZarrLevel`` documents from an
NDI session through the (HIPAA-compliant) NDI cloud API and hands the
lazy multiscale arrays to napari.
"""

from ndi.lightsheet.napari_view import main as napari_view_main
from ndi.lightsheet.pyramid_reader import PyramidReader

__all__ = ["napari_view_main", "PyramidReader"]
