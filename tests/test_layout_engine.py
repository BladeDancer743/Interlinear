from __future__ import annotations

import json
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "interlinear_web" / "static" / "layout.js"


@unittest.skipUnless(shutil.which("node"), "Node.js is not available")
class LayoutEngineTests(unittest.TestCase):
    def run_engine(self, expression: str) -> object:
        script = (
            f"const engine = require({json.dumps(str(ENGINE))});"
            f"process.stdout.write(JSON.stringify({expression}));"
        )
        result = subprocess.run(
            ["node", "-e", script],
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(result.stdout)

    def test_auto_layout_uses_margin_only_when_space_and_density_allow(self) -> None:
        margin = self.run_engine(
            "engine.decideAnnotationLayout({"
            "viewportWidth:1400,pageWidth:800,pageHeight:1000,"
            "preferred:'auto',annotations:[{note:'short note'},{note:'second'}]})"
        )
        compact = self.run_engine(
            "engine.decideAnnotationLayout({"
            "viewportWidth:680,pageWidth:620,pageHeight:900,"
            "preferred:'auto',annotations:[{note:'short note'}]})"
        )
        crowded = self.run_engine(
            "engine.decideAnnotationLayout({"
            "viewportWidth:1050,pageWidth:800,pageHeight:1000,"
            "preferred:'auto',annotations:[{note:'short note'}]})"
        )

        self.assertEqual(margin["mode"], "margin")
        self.assertEqual(compact["mode"], "list")
        self.assertEqual(crowded["mode"], "focus")

    def test_manual_mode_and_collision_distribution_are_deterministic(self) -> None:
        manual = self.run_engine(
            "engine.decideAnnotationLayout({"
            "viewportWidth:600,pageWidth:580,pageHeight:900,"
            "preferred:'margin',annotations:[{note:'x'}]})"
        )
        placements = self.run_engine(
            "engine.distributeMarginItems(["
            "{id:'a',anchorY:40,height:100},"
            "{id:'b',anchorY:60,height:100}],300,12)"
        )

        self.assertEqual(manual["mode"], "margin")
        self.assertGreaterEqual(placements[1]["top"], placements[0]["top"] + 112)


if __name__ == "__main__":
    unittest.main()
