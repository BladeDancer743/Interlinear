from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from interlinear_web.app import create_app
from interlinear_web.store import DocumentStore
from tests.test_web_store import make_pdf


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
        self.assertTrue(health.json()["pdf"]["available"])

        documents = self.client.get("/api/documents")
        self.assertEqual(documents.json(), {"items": [], "count": 0})

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

        image = self.client.get(
            f"/api/documents/{item['id']}/pages/1/image?dpi=120"
        )
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


if __name__ == "__main__":
    unittest.main()
