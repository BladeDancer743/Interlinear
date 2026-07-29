# Local paper workbench

The Interlinear paper workbench is a local viewer and inspection surface for
technical PDF and CAJ documents. It is launched independently from the portable
terminal Skill and does not add dependencies, state, or Web behavior to an
installed Skill.

## Surface isolation

- Start Web only with `python -m interlinear_web`; invoking `$interlinear` does
  not start it.
- Web owns `.interlinear-web`, PDF coordinates, visual cards, and annotated-PDF
  exports.
- The terminal Skill owns chat/terminal text and requested Markdown exports.
- Web does not read terminal conversation state or invoke the Skill.
- Moving notes between the surfaces is an explicit user action.
- Importing the Web module does not create a library; the ASGI factory is
  instantiated only by an explicit Web launch or application call.

## What it preserves

The central viewer uses
[PyMuPDF](https://pymupdf.readthedocs.io/en/latest/page.html) to render each PDF
page as a complete page image. Equations, vector diagrams, embedded images,
unusual fonts, and page geometry therefore remain visible even when the
document's text layer is incomplete.

The inspector exposes information that is useful separately:

- sorted page text for reading and full-document search;
- coordinate-anchored Chinese notes with verified, inferred, and pending states;
- embedded PDF outline and page destinations;
- title, author, subject, keywords, source format, size, and digest;
- visible embedded raster dimensions, bit depth, color-space count, and page
  bounding box;
- vector drawing-group count and combined page bounds.

PDF vector drawings are not mislabeled as embedded rasters. They are reported
as drawing groups and remain visible in the rendered page.

## Annotation and layout

Select a continuous passage in the **Text** inspector and choose
**Add from selection**. The server maps the selected words back to PDF page
coordinates. Notes are stored separately from the imported file.

The browser layout engine chooses one presentation per page:

| Mode | Default decision |
|:--|:--|
| Margin | At least 300 px of side space, at most 10 notes, no note over 260 characters, and cards fit in 92% of page height |
| Focus | The page is readable but all cards do not fit beside it |
| List | Viewport below 720 px, page above 88% of viewport width, over 12 notes, or a note over 420 characters |

Margin cards are sorted by anchor position and separated by at least 12 px. If
collision resolution still cannot fit them on the page, the engine switches to
focus mode. The toolbar can override automatic selection.

The annotated-PDF action writes a new PDF with standard highlight and comment
objects. It does not overwrite the imported PDF.

The complete Web-only decision contract is in
[`annotation-layout.md`](annotation-layout.md).

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
| `GET /api/health` | Web-surface identity plus PDF and CAJ capability status |
| `GET /api/documents` | Private-library index |
| `POST /api/documents/import` | Stream a PDF or CAJ into the local library |
| `GET /api/documents/{id}` | Document metadata and outline |
| `GET /api/documents/{id}/pages/{page}` | Text and raster information |
| `GET /api/documents/{id}/pages/{page}/image` | 72–300 DPI PNG page |
| `GET /api/documents/{id}/search?q=...` | Full-document text search |
| `GET /api/documents/{id}/annotations?page=...` | Page notes and document total |
| `POST /api/documents/{id}/annotations` | Create and coordinate-anchor a note |
| `PATCH /api/documents/{id}/annotations/{note}` | Update text or confidence |
| `DELETE /api/documents/{id}/annotations/{note}` | Delete one note |
| `GET /api/documents/{id}/annotations.pdf` | Export a new PDF with native annotations |
| `GET /api/documents/{id}/pdf` | Original or normalized PDF |
| `GET /api/documents/{id}/source` | Original imported file |

Interactive API documentation is available locally at `/api/docs`.

## Privacy and storage

- The server listens on `127.0.0.1` unless the user explicitly changes it.
- The UI has no CDN, analytics, remote fonts, or remote JavaScript.
- Imported documents and cached pages live under `.interlinear-web/` by
  default; that directory is ignored by Git.
- Annotation JSON and generated annotated PDFs remain in the same private
  library/cache boundary.
- Document IDs are derived from SHA-256 and validated before path resolution.
- Upload filenames are reduced to safe base names.
- A 512 MB default streaming limit prevents unbounded in-memory uploads.
- CAJ conversion never uses `shell=True`.

Do not expose the server on a public interface unless an appropriate
authentication and authorization layer has been added.
