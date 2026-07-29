from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pymupdf

from interlinear_web import caj
from interlinear_web.store import DocumentNotFound, DocumentStore


def make_pdf(path: Path) -> None:
    document = pymupdf.open()
    document.set_metadata(
        {
            "title": "A Local Paper",
            "author": "Interlinear Test",
            "subject": "Document workbench",
        }
    )
    page = document.new_page(width=420, height=595)
    page.insert_text((44, 55), "Interlinear local paper workbench")
    page.insert_text((44, 78), "A searchable phrase lives on page one.")
    page.draw_rect(pymupdf.Rect(40, 100, 210, 220), color=(0.2, 0.3, 0.2))
    pixmap = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 32, 20), False)
    pixmap.clear_with(0xCCF248)
    page.insert_image(pymupdf.Rect(44, 110, 204, 210), stream=pixmap.tobytes("png"))
    document.set_toc([[1, "Introduction", 1]])
    document.save(path)
    document.close()


class DocumentStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.store = DocumentStore(self.root / "library")
        self.source = self.root / "sample.pdf"
        make_pdf(self.source)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_import_inspect_render_and_search(self) -> None:
        metadata = self.store.import_path(
            self.source,
            "sample.pdf",
            remove_source=False,
        )

        self.assertEqual(metadata["title"], "A Local Paper")
        self.assertEqual(metadata["author"], "Interlinear Test")
        self.assertEqual(metadata["page_count"], 1)
        self.assertEqual(metadata["outline"][0]["title"], "Introduction")

        page = self.store.page(metadata["id"], 1)
        self.assertIn("searchable phrase", page["text"])
        self.assertEqual(len(page["images"]), 1)
        self.assertEqual(page["images"][0]["width"], 32)
        self.assertGreaterEqual(page["vectors"]["path_groups"], 1)

        rendered = self.store.render_page(metadata["id"], 1, 144)
        self.assertTrue(rendered.read_bytes().startswith(b"\x89PNG"))
        self.assertEqual(
            self.store.render_page(metadata["id"], 1, 144),
            rendered,
        )

        matches = self.store.search(metadata["id"], "searchable phrase")
        self.assertEqual(matches[0]["page"], 1)

    def test_duplicate_import_reuses_document(self) -> None:
        first = self.store.import_path(
            self.source,
            "sample.pdf",
            remove_source=False,
        )
        second = self.store.import_path(
            self.source,
            "renamed.pdf",
            remove_source=False,
        )
        self.assertEqual(first["id"], second["id"])
        self.assertEqual(len(self.store.list()), 1)

    def test_annotations_are_anchored_persisted_and_exported(self) -> None:
        metadata = self.store.import_path(
            self.source,
            "sample.pdf",
            remove_source=False,
        )
        item = self.store.create_annotation(
            metadata["id"],
            page_number=1,
            quote="searchable phrase lives on page one",
            note="可检索短语：用于验证跨行锚点。",
            confidence="verified",
        )

        self.assertEqual(item["page"], 1)
        self.assertTrue(item["rects"])
        self.assertEqual(
            self.store.list_annotations(metadata["id"], 1)[0]["id"],
            item["id"],
        )

        updated = self.store.update_annotation(
            metadata["id"],
            item["id"],
            note="更新后的中文注释。",
            confidence="inferred",
        )
        self.assertEqual(updated["confidence"], "inferred")

        exported = self.store.export_annotated_pdf(metadata["id"])
        with pymupdf.open(exported) as document:
            annotations = list(document[0].annots() or [])
            annotation_contents = [
                str(annotation.info.get("content", "")) for annotation in annotations
            ]
        self.assertGreaterEqual(len(annotations), 2)
        self.assertTrue(
            any(content.startswith("⚠️推断") for content in annotation_contents)
        )

        self.store.delete_annotation(metadata["id"], item["id"])
        self.assertEqual(self.store.list_annotations(metadata["id"]), [])

    def test_document_id_rejects_path_traversal(self) -> None:
        with self.assertRaises(DocumentNotFound):
            self.store.get("../../metadata")

    def test_caj_uses_conversion_adapter(self) -> None:
        caj_source = self.root / "sample.caj"
        caj_source.write_bytes(b"local caj fixture")

        def fake_convert(_source: Path, output: Path) -> None:
            shutil.copyfile(self.source, output)

        with patch("interlinear_web.store.caj.convert", side_effect=fake_convert):
            metadata = self.store.import_path(
                caj_source,
                "sample.caj",
                remove_source=False,
            )

        self.assertEqual(metadata["source_format"], "caj")
        self.assertTrue(self.store.pdf_path(metadata["id"]).is_file())

    def test_caj_adapter_executes_argument_template_without_shell(self) -> None:
        disguised_pdf = self.root / "converter-input.caj"
        shutil.copyfile(self.source, disguised_pdf)
        output = self.root / "converter-output.pdf"
        helper = self.root / "copy_converter.py"
        helper.write_text(
            "import shutil, sys\nshutil.copyfile(sys.argv[1], sys.argv[2])\n",
            encoding="utf-8",
        )
        command = [sys.executable, str(helper), "{input}", "{output}"]
        status = caj.CajCapability(True, "test", "local test converter")

        with patch(
            "interlinear_web.caj._detected_command",
            return_value=(command, status),
        ):
            caj.convert(disguised_pdf, output)

        self.assertTrue(output.read_bytes().startswith(b"%PDF-"))


if __name__ == "__main__":
    unittest.main()
