# Local paper workbench

The Interlinear paper workbench is a local viewer and inspection surface for
technical PDF and CAJ documents. It complements the portable Skill; it does not
replace the annotation workflow or add dependencies to an installed Skill.

## What it preserves

The central viewer uses
[PyMuPDF](https://pymupdf.readthedocs.io/en/latest/page.html) to render each PDF
page as a complete page image. Equations, vector diagrams, embedded images,
unusual fonts, and page geometry therefore remain visible even when the
document's text layer is incomplete.

The inspector exposes information that is useful separately:

- sorted page text for reading and full-document search;
- embedded PDF outline and page destinations;
- title, author, subject, keywords, source format, size, and digest;
- visible embedded raster dimensions, bit depth, color-space count, and page
  bounding box;
- vector drawing-group count and combined page bounds.

PDF vector drawings are not mislabeled as embedded rasters. They are reported
as drawing groups and remain visible in the rendered page.

## Run locally

From the repository root:

```bash
python -m venv .venv
python -m pip install -r requirements-web.txt
python -m interlinear_web --open
```

Useful options:

```text
--host 127.0.0.1       listening address; local-only by default
--port 8765            listening port
--library PATH         private document-library location
--open                 open the default browser after startup
```

The maximum import size defaults to 512 MB. Set
`INTERLINEAR_MAX_UPLOAD_MB` before launch to choose another limit.

## CAJ conversion

When a [`caj2pdf`](https://github.com/caj2pdf/caj2pdf) executable is available
on `PATH`, the workbench invokes:

```text
caj2pdf convert {input} -o {output}
```

For another local converter, set a command template containing both exact
placeholders:

```text
INTERLINEAR_CAJ_COMMAND=converter {input} {output}
```

The command is split into an argument list and run without a shell. The
workbench then checks the generated file before parsing it as PDF.

CAJ support is necessarily best-effort. Public converters document partial
support for CAJ/HN variants, and unknown variants can fail. The UI reports this
state directly and suggests printing to PDF from CAJViewer as a fallback.

## Local API

| Endpoint | Purpose |
|:--|:--|
| `GET /api/health` | PDF and CAJ capability status |
| `GET /api/documents` | Private-library index |
| `POST /api/documents/import` | Stream a PDF or CAJ into the local library |
| `GET /api/documents/{id}` | Document metadata and outline |
| `GET /api/documents/{id}/pages/{page}` | Text and raster information |
| `GET /api/documents/{id}/pages/{page}/image` | 72–300 DPI PNG page |
| `GET /api/documents/{id}/search?q=...` | Full-document text search |
| `GET /api/documents/{id}/pdf` | Original or normalized PDF |
| `GET /api/documents/{id}/source` | Original imported file |

Interactive API documentation is available locally at `/api/docs`.

## Privacy and storage

- The server listens on `127.0.0.1` unless the user explicitly changes it.
- The UI has no CDN, analytics, remote fonts, or remote JavaScript.
- Imported documents and cached pages live under `.interlinear-web/` by
  default; that directory is ignored by Git.
- Document IDs are derived from SHA-256 and validated before path resolution.
- Upload filenames are reduced to safe base names.
- A 512 MB default streaming limit prevents unbounded in-memory uploads.
- CAJ conversion never uses `shell=True`.

Do not expose the server on a public interface unless an appropriate
authentication and authorization layer has been added.
