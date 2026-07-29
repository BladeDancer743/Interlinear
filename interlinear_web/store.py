"""Private on-disk document library and PDF inspection primitives."""

from __future__ import annotations

import hashlib
import json
import os
import re
import secrets
import shutil
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pymupdf

from . import caj

DOCUMENT_ID = re.compile(r"^[0-9a-f]{20}$")
ANNOTATION_ID = re.compile(r"^[0-9a-f]{16}$")
MAX_SEARCH_RESULTS = 100
ANNOTATION_CONFIDENCE = {"verified", "inferred", "pending"}


class DocumentError(RuntimeError):
    """Base error for invalid or unavailable documents."""


class DocumentNotFound(DocumentError):
    """Raised when a document ID is absent."""


def default_library_root() -> Path:
    configured = os.environ.get("INTERLINEAR_LIBRARY", "").strip()
    return (
        Path(configured).expanduser().resolve()
        if configured
        else (Path.cwd() / ".interlinear-web").resolve()
    )


class DocumentStore:
    def __init__(self, root: Path | None = None) -> None:
        self.root = (root or default_library_root()).resolve()
        self.documents_dir = self.root / "documents"
        self.cache_dir = self.root / "cache"
        self.incoming_dir = self.root / "incoming"
        for directory in (self.documents_dir, self.cache_dir, self.incoming_dir):
            directory.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def safe_name(name: str) -> str:
        candidate = Path(name.replace("\\", "/")).name.strip()
        candidate = re.sub(r"[\x00-\x1f<>:\"/\\|?*]", "_", candidate)
        return candidate[:180] or "document.pdf"

    @staticmethod
    def _digest(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            while chunk := stream.read(1024 * 1024):
                digest.update(chunk)
        return digest.hexdigest()

    def _document_dir(self, document_id: str) -> Path:
        if not DOCUMENT_ID.fullmatch(document_id):
            raise DocumentNotFound("文档不存在。")
        path = (self.documents_dir / document_id).resolve()
        if path.parent != self.documents_dir:
            raise DocumentNotFound("文档不存在。")
        return path

    def _metadata_path(self, document_id: str) -> Path:
        return self._document_dir(document_id) / "metadata.json"

    def _annotations_path(self, document_id: str) -> Path:
        return self._document_dir(document_id) / "annotations.json"

    def get(self, document_id: str) -> dict[str, Any]:
        metadata_path = self._metadata_path(document_id)
        if not metadata_path.is_file():
            raise DocumentNotFound("文档不存在。")
        return json.loads(metadata_path.read_text(encoding="utf-8"))

    def list(self) -> list[dict[str, Any]]:
        documents: list[dict[str, Any]] = []
        for metadata_path in self.documents_dir.glob("*/metadata.json"):
            try:
                documents.append(json.loads(metadata_path.read_text(encoding="utf-8")))
            except (OSError, json.JSONDecodeError):
                continue
        return sorted(
            documents,
            key=lambda item: str(item.get("imported_at", "")),
            reverse=True,
        )

    def create_incoming_path(self, filename: str) -> Path:
        suffix = Path(filename).suffix.lower()
        handle, raw_path = tempfile.mkstemp(suffix=suffix, dir=self.incoming_dir)
        os.close(handle)
        return Path(raw_path)

    def import_path(
        self,
        incoming: Path,
        original_name: str,
        *,
        remove_source: bool = True,
    ) -> dict[str, Any]:
        original_name = self.safe_name(original_name)
        suffix = Path(original_name).suffix.lower()
        if suffix not in {".pdf", ".caj"}:
            raise DocumentError("仅支持 .pdf 与 .caj 文件。")
        if not incoming.is_file() or incoming.stat().st_size == 0:
            raise DocumentError("文件为空或无法读取。")

        full_digest = self._digest(incoming)
        document_id = full_digest[:20]
        final_dir = self._document_dir(document_id)
        existing = final_dir / "metadata.json"
        if existing.is_file():
            if remove_source:
                incoming.unlink(missing_ok=True)
            return self.get(document_id)

        stage_dir = Path(
            tempfile.mkdtemp(prefix=f"{document_id}-", dir=self.incoming_dir)
        )
        source_path = stage_dir / f"source{suffix}"
        try:
            if remove_source:
                incoming.replace(source_path)
            else:
                shutil.copy2(incoming, source_path)

            if suffix == ".caj":
                pdf_path = stage_dir / "normalized.pdf"
                caj.convert(source_path, pdf_path)
                pdf_file = pdf_path.name
            else:
                pdf_path = source_path
                pdf_file = source_path.name

            metadata = self._inspect_pdf(
                pdf_path,
                document_id=document_id,
                digest=full_digest,
                original_name=original_name,
                source_format=suffix[1:],
                source_size=source_path.stat().st_size,
                pdf_file=pdf_file,
            )
            (stage_dir / "metadata.json").write_text(
                json.dumps(metadata, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            try:
                stage_dir.replace(final_dir)
            except FileExistsError:
                shutil.rmtree(stage_dir, ignore_errors=True)
            return self.get(document_id)
        except Exception:
            shutil.rmtree(stage_dir, ignore_errors=True)
            raise

    @staticmethod
    def _inspect_pdf(
        pdf_path: Path,
        *,
        document_id: str,
        digest: str,
        original_name: str,
        source_format: str,
        source_size: int,
        pdf_file: str,
    ) -> dict[str, Any]:
        try:
            with pymupdf.open(pdf_path) as document:
                if not document.is_pdf or document.page_count < 1:
                    raise DocumentError("文件不是有效的非空 PDF。")
                raw_metadata = document.metadata or {}
                toc = [
                    {"level": int(row[0]), "title": str(row[1]), "page": int(row[2])}
                    for row in document.get_toc(simple=True)
                    if len(row) >= 3
                ]
                first_page = document[0]
                title = str(raw_metadata.get("title") or "").strip()
                if not title:
                    title = Path(original_name).stem
                metadata = {
                    "id": document_id,
                    "sha256": digest,
                    "original_name": original_name,
                    "source_format": source_format,
                    "source_size": source_size,
                    "pdf_file": pdf_file,
                    "title": title,
                    "author": str(raw_metadata.get("author") or "").strip(),
                    "subject": str(raw_metadata.get("subject") or "").strip(),
                    "keywords": str(raw_metadata.get("keywords") or "").strip(),
                    "page_count": document.page_count,
                    "first_page": {
                        "width": round(first_page.rect.width, 2),
                        "height": round(first_page.rect.height, 2),
                    },
                    "outline": toc,
                    "imported_at": datetime.now(UTC).isoformat(),
                }
        except DocumentError:
            raise
        except Exception as exc:
            raise DocumentError(f"无法解析 PDF：{exc}") from exc
        return metadata

    def _pdf_path(self, document_id: str) -> Path:
        metadata = self.get(document_id)
        path = self._document_dir(document_id) / str(metadata["pdf_file"])
        if not path.is_file():
            raise DocumentNotFound("标准化 PDF 已丢失。")
        return path

    def source_path(self, document_id: str) -> Path:
        metadata = self.get(document_id)
        path = (
            self._document_dir(document_id)
            / f"source.{str(metadata['source_format']).lower()}"
        )
        if not path.is_file():
            raise DocumentNotFound("原始文件已丢失。")
        return path

    def pdf_path(self, document_id: str) -> Path:
        return self._pdf_path(document_id)

    def page(self, document_id: str, page_number: int) -> dict[str, Any]:
        pdf_path = self._pdf_path(document_id)
        try:
            with pymupdf.open(pdf_path) as document:
                if not 1 <= page_number <= document.page_count:
                    raise DocumentNotFound("页码超出范围。")
                page = document[page_number - 1]
                images = []
                for index, info in enumerate(page.get_image_info(xrefs=True), start=1):
                    bbox = info.get("bbox", ())
                    images.append(
                        {
                            "index": index,
                            "xref": int(info.get("xref") or 0),
                            "width": int(info.get("width") or 0),
                            "height": int(info.get("height") or 0),
                            "colorspace": int(info.get("colorspace") or 0),
                            "bits_per_component": int(info.get("bpc") or 0),
                            "bbox": [round(float(value), 2) for value in bbox],
                        }
                    )
                drawings = page.get_drawings()
                drawing_bounds = pymupdf.Rect()
                for drawing in drawings:
                    drawing_bounds |= drawing["rect"]
                return {
                    "number": page_number,
                    "width": round(page.rect.width, 2),
                    "height": round(page.rect.height, 2),
                    "rotation": page.rotation,
                    "text": page.get_text("text", sort=True),
                    "images": images,
                    "vectors": {
                        "path_groups": len(drawings),
                        "bbox": (
                            [
                                round(drawing_bounds.x0, 2),
                                round(drawing_bounds.y0, 2),
                                round(drawing_bounds.x1, 2),
                                round(drawing_bounds.y1, 2),
                            ]
                            if drawings
                            else []
                        ),
                    },
                    "links": len(page.get_links()),
                }
        except DocumentError:
            raise
        except Exception as exc:
            raise DocumentError(f"无法读取第 {page_number} 页：{exc}") from exc

    def render_page(self, document_id: str, page_number: int, dpi: int) -> Path:
        dpi = max(72, min(dpi, 300))
        cache = self.cache_dir / document_id
        cache.mkdir(parents=True, exist_ok=True)
        target = cache / f"page-{page_number:05d}-{dpi}.png"
        if target.is_file():
            return target

        pdf_path = self._pdf_path(document_id)
        try:
            with pymupdf.open(pdf_path) as document:
                if not 1 <= page_number <= document.page_count:
                    raise DocumentNotFound("页码超出范围。")
                pixmap = document[page_number - 1].get_pixmap(
                    dpi=dpi,
                    alpha=False,
                    colorspace=pymupdf.csRGB,
                )
                temporary = target.with_suffix(".part.png")
                pixmap.save(temporary)
                temporary.replace(target)
        except DocumentError:
            raise
        except Exception as exc:
            raise DocumentError(f"无法渲染第 {page_number} 页：{exc}") from exc
        return target

    def search(
        self, document_id: str, query: str, limit: int = MAX_SEARCH_RESULTS
    ) -> list[dict[str, Any]]:
        needle = query.strip()
        if not needle:
            return []
        folded = needle.casefold()
        results: list[dict[str, Any]] = []
        pdf_path = self._pdf_path(document_id)
        try:
            with pymupdf.open(pdf_path) as document:
                for index, page in enumerate(document):
                    text = page.get_text("text", sort=True)
                    location = text.casefold().find(folded)
                    if location < 0:
                        continue
                    start = max(0, location - 90)
                    end = min(len(text), location + len(needle) + 150)
                    excerpt = " ".join(text[start:end].split())
                    results.append({"page": index + 1, "excerpt": excerpt})
                    if len(results) >= limit:
                        break
        except Exception as exc:
            raise DocumentError(f"文档搜索失败：{exc}") from exc
        return results

    def list_annotations(
        self,
        document_id: str,
        page_number: int | None = None,
    ) -> list[dict[str, Any]]:
        self.get(document_id)
        path = self._annotations_path(document_id)
        if not path.is_file():
            return []
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            items = payload.get("items", [])
        except (OSError, json.JSONDecodeError) as exc:
            raise DocumentError(f"无法读取注释：{exc}") from exc
        if not isinstance(items, list):
            raise DocumentError("注释存储格式无效。")
        selected = [
            item
            for item in items
            if isinstance(item, dict)
            and (page_number is None or item.get("page") == page_number)
        ]
        return sorted(
            selected,
            key=lambda item: (
                int(item.get("page", 0)),
                self._annotation_anchor_y(item),
                str(item.get("created_at", "")),
            ),
        )

    def create_annotation(
        self,
        document_id: str,
        *,
        page_number: int,
        quote: str,
        note: str,
        confidence: str = "verified",
    ) -> dict[str, Any]:
        clean_quote = self._clean_annotation_text(quote, "原文", 5000)
        clean_note = self._clean_annotation_text(note, "注释", 10000)
        clean_confidence = confidence.strip().lower()
        if clean_confidence not in ANNOTATION_CONFIDENCE:
            raise DocumentError("注释置信状态无效。")

        pdf_path = self._pdf_path(document_id)
        try:
            with pymupdf.open(pdf_path) as document:
                if not 1 <= page_number <= document.page_count:
                    raise DocumentNotFound("页码超出范围。")
                rects = self._find_quote_rects(document[page_number - 1], clean_quote)
        except DocumentError:
            raise
        except Exception as exc:
            raise DocumentError(f"无法定位注释原文：{exc}") from exc
        if not rects:
            raise DocumentError(
                "当前页没有定位到这段原文。请从右侧正文中重新选择一段连续文字。"
            )

        timestamp = datetime.now(UTC).isoformat()
        item = {
            "id": secrets.token_hex(8),
            "page": page_number,
            "quote": clean_quote,
            "note": clean_note,
            "confidence": clean_confidence,
            "rects": rects,
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        items = self.list_annotations(document_id)
        items.append(item)
        self._write_annotations(document_id, items)
        return item

    def update_annotation(
        self,
        document_id: str,
        annotation_id: str,
        *,
        note: str,
        confidence: str,
    ) -> dict[str, Any]:
        self._validate_annotation_id(annotation_id)
        clean_note = self._clean_annotation_text(note, "注释", 10000)
        clean_confidence = confidence.strip().lower()
        if clean_confidence not in ANNOTATION_CONFIDENCE:
            raise DocumentError("注释置信状态无效。")
        items = self.list_annotations(document_id)
        for item in items:
            if item.get("id") != annotation_id:
                continue
            item["note"] = clean_note
            item["confidence"] = clean_confidence
            item["updated_at"] = datetime.now(UTC).isoformat()
            self._write_annotations(document_id, items)
            return item
        raise DocumentNotFound("注释不存在。")

    def delete_annotation(self, document_id: str, annotation_id: str) -> None:
        self._validate_annotation_id(annotation_id)
        items = self.list_annotations(document_id)
        remaining = [item for item in items if item.get("id") != annotation_id]
        if len(remaining) == len(items):
            raise DocumentNotFound("注释不存在。")
        self._write_annotations(document_id, remaining)

    def export_annotated_pdf(self, document_id: str) -> Path:
        source = self._pdf_path(document_id)
        items = self.list_annotations(document_id)
        payload = json.dumps(items, ensure_ascii=False, sort_keys=True).encode("utf-8")
        revision = hashlib.sha256(payload).hexdigest()[:12]
        cache = self.cache_dir / document_id
        cache.mkdir(parents=True, exist_ok=True)
        target = cache / f"annotated-{revision}.pdf"
        if target.is_file():
            return target

        temporary = target.with_suffix(".part.pdf")
        try:
            with pymupdf.open(source) as document:
                for item in items:
                    page_number = int(item["page"])
                    if not 1 <= page_number <= document.page_count:
                        continue
                    page = document[page_number - 1]
                    rects = [
                        pymupdf.Rect(*values)
                        for values in item.get("rects", [])
                        if isinstance(values, list) and len(values) == 4
                    ]
                    if not rects:
                        continue
                    confidence = str(item.get("confidence", "verified"))
                    prefix = {
                        "inferred": "⚠️推断：",
                        "pending": "🔍待核：",
                    }.get(confidence, "")
                    comment_text = f"{prefix}{item.get('note', '')}"
                    highlight = page.add_highlight_annot(rects)
                    highlight.set_colors(stroke=(0.8, 0.95, 0.28))
                    highlight.set_info(
                        title="Interlinear",
                        subject=str(item.get("quote", ""))[:120],
                        content=comment_text,
                    )
                    highlight.update(opacity=0.32)
                    first = rects[0]
                    pin = pymupdf.Point(
                        min(page.rect.width - 20, first.x1 + 8),
                        max(16, first.y0),
                    )
                    popup = page.add_text_annot(
                        pin,
                        comment_text,
                        icon="Comment",
                    )
                    popup.set_info(
                        title="Interlinear",
                        subject=str(item.get("quote", ""))[:120],
                    )
                    popup.update()
                document.save(temporary, garbage=4, deflate=True)
            temporary.replace(target)
        except Exception as exc:
            temporary.unlink(missing_ok=True)
            raise DocumentError(f"无法导出带注释 PDF：{exc}") from exc
        return target

    @staticmethod
    def _clean_annotation_text(value: str, label: str, limit: int) -> str:
        cleaned = value.replace("\x00", "").strip()
        if not cleaned:
            raise DocumentError(f"{label}不能为空。")
        if len(cleaned) > limit:
            raise DocumentError(f"{label}过长。")
        return cleaned

    @staticmethod
    def _validate_annotation_id(annotation_id: str) -> None:
        if ANNOTATION_ID.fullmatch(annotation_id) is None:
            raise DocumentNotFound("注释不存在。")

    @staticmethod
    def _annotation_anchor_y(item: dict[str, Any]) -> float:
        rects = item.get("rects", [])
        if not rects or not isinstance(rects[0], list) or len(rects[0]) != 4:
            return 0
        return float(rects[0][1])

    @staticmethod
    def _word_key(value: str) -> str:
        return re.sub(r"[^\w]+", "", value.casefold(), flags=re.UNICODE)

    @classmethod
    def _find_quote_rects(
        cls,
        page: pymupdf.Page,
        quote: str,
    ) -> list[list[float]]:
        direct = page.search_for(quote)
        if direct:
            return [
                [
                    round(rect.x0, 2),
                    round(rect.y0, 2),
                    round(rect.x1, 2),
                    round(rect.y1, 2),
                ]
                for rect in direct
            ]

        needle = [cls._word_key(token) for token in quote.split()]
        needle = [token for token in needle if token]
        words = page.get_text("words", sort=True)
        haystack = [cls._word_key(str(word[4])) for word in words]
        if not needle:
            return []

        start = -1
        for index in range(len(haystack) - len(needle) + 1):
            if haystack[index : index + len(needle)] == needle:
                start = index
                break
        if start < 0:
            return []

        matched = words[start : start + len(needle)]
        grouped: list[pymupdf.Rect] = []
        group_keys: list[tuple[int, int]] = []
        for word in matched:
            key = (int(word[5]), int(word[6]))
            rect = pymupdf.Rect(word[:4])
            if group_keys and key == group_keys[-1]:
                grouped[-1] |= rect
            else:
                group_keys.append(key)
                grouped.append(rect)
        return [
            [round(rect.x0, 2), round(rect.y0, 2), round(rect.x1, 2), round(rect.y1, 2)]
            for rect in grouped
        ]

    def _write_annotations(
        self,
        document_id: str,
        items: list[dict[str, Any]],
    ) -> None:
        path = self._annotations_path(document_id)
        payload = {
            "version": 1,
            "updated_at": datetime.now(UTC).isoformat(),
            "items": items,
        }
        temporary = path.with_suffix(".part.json")
        temporary.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temporary.replace(path)
