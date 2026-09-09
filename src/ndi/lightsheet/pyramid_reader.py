"""PyramidReader - read lightsheetZarrPyramid + lightsheetZarrLevel documents
through the (HIPAA-compliant) NDI cloud API and present each level as a lazy
dask array.

Where this fits: :mod:`ndi.lightsheet.napari_view` opens a
``PyramidReader``, asks for its multiscale array list, and hands that
list to :func:`napari.Viewer.add_image`.

Status: scaffold. The parts that need writing are called out inline.

Design
------

- ``PyramidReader.open(session_path, pyramid_id)`` opens the NDI session
  (local dir or via ``ndi.session.dir``) and resolves the parent
  ``lightsheetZarrPyramid`` document by id.
- ``PyramidReader.list_levels()`` queries every ``lightsheetZarrLevel``
  whose ``lightsheetZarrPyramid_id`` depends_on the parent id and
  returns them in finest-first order.
- ``PyramidReader.multiscale(reduction=None, channel=None)`` returns a
  list of dask arrays, one per level, that each fetch chunks lazily
  from the level document's ``chunk.bin_#`` file series through the
  NDI cloud cache. napari expects such a list under ``multiscale=True``.
- ``PyramidReader.attach_controls(viewer)`` docks small magicgui panels
  for reduction switching (mean/max) and channel selection.

Reduction switching under this design is *pyramid switching*: mean and
max are separate ``lightsheetZarrPyramid`` documents in the session
(NDI documents are immutable, so a new reduction is a new document, not
an edit). ``PyramidReader.sibling(reduction)`` locates the sibling
parent that shares this pyramid's ``subject_id`` +
``source_file_id`` and returns another ``PyramidReader`` for it.

Chunk file series
-----------------

Each ``lightsheetZarrLevel`` owns a ``chunk.bin_#`` file series. To
find chunk ``(i0, i1, ..., in)`` in the level's ``chunk_grid``:

    # ``#`` is 1-based; C-order flatten of the chunk grid coordinates.
    n = 1 + ravel_multi_index(coords, chunk_grid, order="C")

Every file is one chunk's raw byte payload after the level's ``codec``
compression is applied (`raw` = uncompressed little-endian bytes in
``dtype`` / ``chunk_order``). The reader in this module does the
inverse.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Optional


@dataclass
class PyramidReader:
    """Reader for a single lightsheetZarrPyramid + its levels.

    Attributes
    ----------
    session_path
        Path to the ndi.session.dir on disk (or the cloud-cache local
        mirror of one).
    pyramid_id
        Document id of the parent lightsheetZarrPyramid.
    """

    session_path: str
    pyramid_id: str
    _parent: Optional[Any] = None
    _levels: Optional[List[Any]] = None

    @classmethod
    def open(cls, session_path: str, pyramid_id: str) -> "PyramidReader":
        """Open the session and resolve the parent document."""
        raise NotImplementedError(
            "PyramidReader.open needs the NDI-python session + cloud cache "
            "loader hooked up. See README-lightsheet-zarr.md at the top of "
            "ndi/lightsheet/ for the design and status."
        )

    @property
    def default_name(self) -> str:
        if self._parent is None:
            return "lightsheet zarr"
        props = self._parent.document_properties["lightsheetZarrPyramid"]
        label = props.get("label") or props.get("pyramid_name") or "lightsheet zarr"
        return label

    def list_levels(self) -> List[Any]:
        """Return the level documents, finest-first."""
        raise NotImplementedError(
            "list_levels needs the depends_on query wired up through the "
            "session's database. See README-lightsheet-zarr.md."
        )

    def multiscale(
        self,
        reduction: Optional[str] = None,
        channel: Optional[int] = None,
    ) -> List[Any]:
        """Return one lazy dask array per level, aligned with the level order.

        napari consumes this list under ``add_image(..., multiscale=True)``.
        """
        raise NotImplementedError(
            "multiscale needs the chunk.bin_# fetcher + a small dask "
            "wrapper. See README-lightsheet-zarr.md."
        )

    def sibling(self, reduction: str) -> "PyramidReader":
        """Return a PyramidReader for the sibling pyramid with a different reduction."""
        raise NotImplementedError(
            "sibling() needs a session-scope query by (subject_id, "
            "source_file_id, reduction). See README-lightsheet-zarr.md."
        )

    def attach_controls(self, viewer: Any) -> None:
        """Dock reduction / channel / level panels on the napari viewer."""
        raise NotImplementedError(
            "attach_controls needs the magicgui panels. See "
            "README-lightsheet-zarr.md."
        )
