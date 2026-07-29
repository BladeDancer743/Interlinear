from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from interlinear_web.app import create_app
from interlinear_web.store import DocumentStore
from tests.test_web_store import make_pdf

ROOT = Path(__file__).resolve().parents[1]


class WebApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        root = Path(self.temporary.name)
        self.store = DocumentStore(root / "library")
        self.sample = root / "sample.pdf"
        make_pdf(self.sample)
        self.client = TestClient(create_app(self.store))

    def tearDown(self) -> None:
        self.client.close()
        self.temporary.cleanup()

    def test_health_and_empty_library(self) -> None:
        health = self.client.get("/api/health")
        self.assertEqual(health.status_code, 200)
        self.assertTrue(health.json()["local_only"])
        self.assertEqual(health.json()["surface"], "web")
        self.assertTrue(health.json()["pdf"]["available"])

        documents = self.client.get("/api/documents")
        self.assertEqual(documents.json(), {"items": [], "count": 0})

    def test_importing_app_does_not_create_a_web_library(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            environment = os.environ.copy()
            environment.pop("INTERLINEAR_LIBRARY", None)
            environment["PYTHONPATH"] = os.pathsep.join(
                [str(ROOT), environment.get("PYTHONPATH", "")]
            )
            subprocess.run(
                [sys.executable, "-c", "import interlinear_web.app"],
                cwd=directory,
                env=environment,
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertFalse((Path(directory) / ".interlinear-web").exists())

    def test_pdf_import_page_image_and_search(self) -> None:
        with self.sample.open("rb") as stream:
            response = self.client.post(
                "/api/documents/import",
                files={"file": ("paper.pdf", stream, "application/pdf")},
            )
        self.assertEqual(response.status_code, 201)
        item = response.json()["document"]

        page = self.client.get(f"/api/documents/{item['id']}/pages/1")
        self.assertIn("searchable phrase", page.json()["page"]["text"])

        image = self.client.get(f"/api/documents/{item['id']}/pages/1/image?dpi=120")
        self.assertEqual(image.status_code, 200)
        self.assertEqual(image.headers["content-type"], "image/png")
        self.assertTrue(image.content.startswith(b"\x89PNG"))

        search = self.client.get(
            f"/api/documents/{item['id']}/search",
            params={"q": "searchable phrase"},
        )
        self.assertEqual(search.json()["count"], 1)

    def test_unsupported_format_is_rejected(self) -> None:
        response = self.client.post(
            "/api/documents/import",
            files={"file": ("notes.txt", b"hello", "text/plain")},
        )
        self.assertEqual(response.status_code, 415)
        self.assertEqual(response.json()["detail"]["code"], "UNSUPPORTED_FORMAT")

    def test_annotation_crud_and_pdf_export(self) -> None:
        with self.sample.open("rb") as stream:
            imported = self.client.post(
                "/api/documents/import",
                files={"file": ("paper.pdf", stream, "application/pdf")},
            ).json()["document"]
        document_id = imported["id"]

        created = self.client.post(
            f"/api/documents/{document_id}/annotations",
            json={
                "page": 1,
                "quote": "searchable phrase",
                "note": "可检索短语：用于验证注释接口。",
                "confidence": "verified",
            },
        )
        self.assertEqual(created.status_code, 201)
        item = created.json()["annotation"]
        self.assertTrue(item["rects"])

        listed = self.client.get(
            f"/api/documents/{document_id}/annotations",
            params={"page": 1},
        ).json()
        self.assertEqual(listed["count"], 1)
        self.assertEqual(listed["total"], 1)

        updated = self.client.patch(
            f"/api/documents/{document_id}/annotations/{item['id']}",
            json={"note": "更新后的注释。", "confidence": "pending"},
        )
        self.assertEqual(updated.json()["annotation"]["confidence"], "pending")

        exported = self.client.get(f"/api/documents/{document_id}/annotations.pdf")
        self.assertEqual(exported.status_code, 200)
        self.assertEqual(exported.headers["content-type"], "application/pdf")
        self.assertTrue(exported.content.startswith(b"%PDF-"))

        deleted = self.client.delete(
            f"/api/documents/{document_id}/annotations/{item['id']}"
        )
        self.assertEqual(deleted.status_code, 204)
        self.assertEqual(
            self.client.get(f"/api/documents/{document_id}/annotations").json()[
                "count"
            ],
            0,
        )


if __name__ == "__main__":
    unittest.main()
