# obj-island-audit

Explain edge-connected triangle islands and edge defects in a bounded OBJ mesh.

For: CAD/export pipeline maintainers inspecting a triangulated OBJ before downstream processing. Disconnected parts, seam duplicates and orientation conflicts need attributable face/edge evidence rather than an unexplained pass/fail.

## Quickstart

Python 3.10 or newer; no runtime packages or network access. The wheel build needs setuptools from the normal Python package registry.

```sh
git clone https://github.com/nripankadas07/obj-island-audit.git
cd obj-island-audit
python3 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/obj-island-audit example.obj
```

The invented OBJ has two separate closed tetrahedral edge surfaces, eight faces and no reported edge defects; exit 0. Multiple closed islands alone are not an error.

Windows equivalents use `.venv\Scripts\python.exe` and `.venv\Scripts\obj-island-audit.exe`; Windows/macOS are not executed by this release’s Linux CI.

## Contract

UTF-8 OBJ triangle faces only. Positive and relative negative indices are validated at the face declaration, including texture/normal references. Exact-coordinate welding always applies. --weld-decimals 0–9 adds half-even decimal-grid quantization, not a Euclidean distance tolerance. Degenerate and duplicate faces are reported and excluded before edge incidence and island grouping. Point-touch contacts remain separate edge islands and are reported. Metadata is counted; materials are never loaded.

JSON goes to stdout. Exit 0 means a valid report without findings; exit 1 means a valid report with the documented findings; exit 2 means invalid input or an I/O failure, with an error on stderr and no partial report. `--help` describes options. Review outputs before sharing them; they may contain input identifiers.

## Limits

2 MiB, 20,000 vertices and 30,000 triangle faces. Coordinates: zero or absolute magnitude 1e-12 through 1e9, bounded decimal precision. No polygons, freeform curves, repair, self-intersection detection, vertex-manifold certification, solid volume or printability guarantee. closed_edge_surface only means each retained component edge has incidence two; it is not a full watertightness claim. Area is approximate.

## Verify

```sh
python3 -m unittest -v test_behavior
python3 -m compileall -q .
python3 -m pip wheel --no-deps --wheel-dir dist .
python3 -m venv /tmp/obj-island-audit-check
/tmp/obj-island-audit-check/bin/python -m pip install --no-deps dist/*.whl
python3 verify_installed.py /tmp/obj-island-audit-check/bin/python
```

Installed-command checks run outside the checkout. See [validation](VALIDATION.md), [research](RESEARCH.md), [contributing](CONTRIBUTING.md), [support](SUPPORT.md) and [security](SECURITY.md).

Original implementation and invented fixtures developed with AI assistance. MIT license. No production adoption, competitor feature-absence or performance-superiority claim.
