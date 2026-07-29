"""FastAPI application for the local Interlinear document workbench."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, HTTPException, Query, Response, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import __version__, caj
from .store import DocumentError, DocumentNotFound, DocumentStore

STATIC_DIR = Path(__file__).resolve().parent / "static"
MAX_UPLOAD_BYTES = int(os.environ.get("INTERLINEAR_MAX_UPLOAD_MB", "512")) * 1024 * 1024


class AnnotationCreate(BaseModel):
    page: int = Field(ge=1)
    quote: str = Field(min_length=1, max_length=5000)
    note: str = Field(min_length=1, max_length=10000)
    confidence: str = Field(default="verified", max_length=20)


class AnnotationUpdate(BaseModel):
    note: str = Field(min_length=1, max_length=10000)
    confidence: str = Field(default="verified", max_length=20)


def create_app(store: DocumentStore | None = None) -> FastAPI:
    document_store = store or DocumentStore()
    application = FastAPI(
        title="Interlinear Web Workbench",
        version=__version__,
        docs_url="/api/docs",
        redoc_url=None,
    )
    application.state.store = document_store
    application.mount("/assets", StaticFiles(directory=STATIC_DIR), name="assets")

    @application.exception_handler(DocumentNotFound)
    async def not_found_handler(_request, exc: DocumentNotFound):
        return _error_response(404, "NOT_FOUND", str(exc))

    @application.exception_handler(DocumentError)
    async def document_error_handler(_request, exc: DocumentError):
        return _error_response(422, "DOCUMENT_ERROR", str(exc))

    @application.exception_handler(caj.CajConversionError)
    async def caj_error_handler(_request, exc: caj.CajConversionError):
        return _error_response(503, "CAJ_CONVERTER_ERROR", str(exc))

    @application.get("/", include_in_schema=False)
    async def index() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    @application.get("/api/health")
    async def health() -> dict[str, object]:
        return {
            "status": "ok",
            "surface": "web",
            "version": __version__,
            "local_only": True,
            "pdf": {"available": True, "engine": "PyMuPDF"},
            "caj": caj.capability().as_dict(),
            "library": str(document_store.root),
            "max_upload_mb": MAX_UPLOAD_BYTES // (1024 * 1024),
        }

    @application.get("/api/documents")
    async def documents() -> dict[str, object]:
        items = document_store.list()
        return {"items": items, "count": len(items)}

    @application.post("/api/documents/import", status_code=201)
    async def import_document(
        file: Annotated[UploadFile, File(...)],
    ) -> dict[str, object]:
        name = document_store.safe_name(file.filename or "document.pdf")
        suffix = Path(name).suffix.lower()
        if suffix not in {".pdf", ".caj"}:
            raise HTTPException(
                status_code=415,
                detail={
                    "code": "UNSUPPORTED_FORMAT",
                    "message": "仅支持 PDF 与 CAJ 文件。",
                },
            )
        incoming = document_store.create_incoming_path(name)
        size = 0
        try:
            with incoming.open("wb") as destination:
                while chunk := await file.read(1024 * 1024):
                    size += len(chunk)
                    if size > MAX_UPLOAD_BYTES:
                        raise HTTPException(
                            status_code=413,
                            detail={
                                "code": "FILE_TOO_LARGE",
                                "message": "文件超过本地导入大小限制。",
                            },
                        )
                    destination.write(chunk)
            item = document_store.import_path(incoming, name)
            return {"document": item}
        finally:
            incoming.unlink(missing_ok=True)
            await file.close()

    @application.get("/api/documents/{document_id}")
    async def document(document_id: str) -> dict[str, object]:
        return {"document": document_store.get(document_id)}

    @application.get("/api/documents/{document_id}/pages/{page_number}")
    async def page(document_id: str, page_number: int) -> dict[str, object]:
        return {"page": document_store.page(document_id, page_number)}

    @application.get(
        "/api/documents/{document_id}/pages/{page_number}/image",
        response_class=FileResponse,
    )
    async def page_image(
        document_id: str,
        page_number: int,
        dpi: int = Query(default=160, ge=72, le=300),
    ) -> FileResponse:
        path = document_store.render_page(document_id, page_number, dpi)
        return FileResponse(
            path,
            media_type="image/png",
            headers={"Cache-Control": "private, max-age=31536000, immutable"},
        )

    @application.get("/api/documents/{document_id}/search")
    async def search(
        document_id: str,
        q: str = Query(min_length=1, max_length=200),
    ) -> dict[str, object]:
        results = document_store.search(document_id, q)
        return {"query": q, "results": results, "count": len(results)}

    @application.get("/api/documents/{document_id}/annotations")
    async def annotations(
        document_id: str,
        page: int | None = Query(default=None, ge=1),
    ) -> dict[str, object]:
        items = document_store.list_annotations(document_id, page)
        total = (
            len(document_store.list_annotations(document_id))
            if page is not None
            else len(items)
        )
        return {"items": items, "count": len(items), "total": total}

    @application.post(
        "/api/documents/{document_id}/annotations",
        status_code=201,
    )
    async def create_annotation(
        document_id: str,
        payload: AnnotationCreate,
    ) -> dict[str, object]:
        item = document_store.create_annotation(
            document_id,
            page_number=payload.page,
            quote=payload.quote,
            note=payload.note,
            confidence=payload.confidence,
        )
        return {"annotation": item}

    @application.patch("/api/documents/{document_id}/annotations/{annotation_id}")
    async def update_annotation(
        document_id: str,
        annotation_id: str,
        payload: AnnotationUpdate,
    ) -> dict[str, object]:
        item = document_store.update_annotation(
            document_id,
            annotation_id,
            note=payload.note,
            confidence=payload.confidence,
        )
        return {"annotation": item}

    @application.delete(
        "/api/documents/{document_id}/annotations/{annotation_id}",
        status_code=204,
    )
    async def delete_annotation(
        document_id: str,
        annotation_id: str,
    ) -> Response:
        document_store.delete_annotation(document_id, annotation_id)
        return Response(status_code=204)

    @application.get(
        "/api/documents/{document_id}/annotations.pdf",
        response_class=FileResponse,
    )
    async def annotated_pdf(document_id: str) -> FileResponse:
        metadata = document_store.get(document_id)
        path = document_store.export_annotated_pdf(document_id)
        stem = Path(str(metadata["original_name"])).stem
        return FileResponse(
            path,
            media_type="application/pdf",
            filename=f"{stem}-interlinear.pdf",
        )

    @application.get(
        "/api/documents/{document_id}/source",
        response_class=FileResponse,
    )
    async def source_file(document_id: str) -> FileResponse:
        metadata = document_store.get(document_id)
        return FileResponse(
            document_store.source_path(document_id),
            filename=str(metadata["original_name"]),
        )

    @application.get(
        "/api/documents/{document_id}/pdf",
        response_class=FileResponse,
    )
    async def pdf_file(document_id: str) -> FileResponse:
        metadata = document_store.get(document_id)
        return FileResponse(
            document_store.pdf_path(document_id),
            media_type="application/pdf",
            filename=f"{Path(str(metadata['original_name'])).stem}.pdf",
            content_disposition_type="inline",
        )

    return application


def _error_response(status: int, code: str, message: str):
    from fastapi.responses import JSONResponse

    return JSONResponse(
        status_code=status,
        content={"detail": {"code": code, "message": message}},
    )
