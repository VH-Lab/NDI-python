# ndi.lightsheet (Python)

Python-side companion to `+ndi/+fun/+doc/+lightsheet/` in NDI-matlab.
Provides the `napariViewLightsheet` console script that the MATLAB
`LightsheetZarrManager` GUI shells out to, and the `PyramidReader`
that pulls `lightsheetZarrPyramid` + `lightsheetZarrLevel` documents
through the NDI cloud API and presents them to napari.

## Layout

```
src/ndi/lightsheet/
    __init__.py
    napari_view.py            # console-script entry
    pyramid_reader.py         # dask-backed reader (scaffold)
scripts/
    napariViewLightsheet      # shell wrapper installed to /usr/local/bin
```

## pyproject.toml additions

Add to the `[project.optional-dependencies]` block (or `[project.dependencies]`
if you want the viewer to be part of the base install):

```toml
[project.optional-dependencies]
viewer = [
    "napari[all]>=0.5",
    "magicgui>=0.8",
    "qtpy>=2.4",
    "dask>=2024.3",
    "zarr>=2.13",
    "numcodecs>=0.10",
]
```

Add the console script:

```toml
[project.scripts]
napariViewLightsheet = "ndi.lightsheet.napari_view:main"
```

## Status

Scaffold. What is wired:

- `napari_view.py` parses the argument set that
  `ndi.fun.doc.lightsheet.viewCommand` in NDI-matlab emits.
- `PyramidReader` names the exact hooks the console script uses
  (`open`, `list_levels`, `multiscale`, `sibling`, `attach_controls`).

What still needs building (each `raise NotImplementedError` in
`pyramid_reader.py` marks a hook):

1. Session open + parent-document resolution through the NDI cloud
   API (via `ndi.session.dir` or the cloud-cache equivalent).
2. `list_levels` - the depends_on query for `lightsheetZarrLevel`
   with a matching `lightsheetZarrPyramid_id`.
3. `multiscale` - the actual chunk fetcher. Each level is a
   `dask.array.Array` built from `dask.array.from_delayed` blocks;
   each delayed block reads one chunk from the level's `chunk.bin_#`
   file series (through the cloud API), decodes it per the level's
   `codec` field, and reshapes to the level's `chunks` shape in
   `dtype` / `chunk_order`. Missing chunks (not in
   `n_chunks_stored`) are filled with `fill_value`.
4. `sibling` - session-scope query by `(subject_id, source_file_id,
   reduction)` to find the sibling parent for a reduction swap.
5. `attach_controls` - magicgui dock widgets:
     * reduction (radio: mean / max) - switches the layer's data
       source via `sibling`
     * channel (dropdown) - swaps which channel(s) render
     * level lock (spin box; -1 = auto) - forces a level regardless
       of napari's zoom
