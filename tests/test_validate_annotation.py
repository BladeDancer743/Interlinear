from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "interlinear"
    / "scripts"
    / "validate_annotation.py"
)
SPEC = importlib.util.spec_from_file_location("validate_annotation", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
validator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)


class ValidateAnnotationTests(unittest.TestCase):
    def test_valid_annotation_preserves_source_and_counts_summary(self) -> None:
        source = "Noise limits circuits. QEC helps."
        annotated = """\
<!-- interlinear-source:start -->
> Noise【噪声：使实际操作偏离目标变换】 limits circuits.
> QEC【量子纠错：用冗余编码检测并修正错误】 helps.
<!-- interlinear-source:end -->

本节：2 个新术语 · 0 个复现简注 · 0 个待核项
"""
        report = validator.validate(source, annotated, require_summary=True)
        self.assertTrue(report.ok, report.errors)
        self.assertTrue(report.source_matches)
        self.assertEqual(report.annotations, 2)
        self.assertEqual(report.new_terms, 2)

    def test_source_mutation_is_rejected(self) -> None:
        source = "Noise limits circuits."
        annotated = "Noise【噪声：使操作偏离目标】 improves circuits."
        report = validator.validate(source, annotated)
        self.assertFalse(report.ok)
        self.assertIn("source-fidelity", {issue.code for issue in report.errors})

    def test_unbalanced_delimiter_is_rejected(self) -> None:
        report = validator.validate("QEC helps.", "QEC【量子纠错：修正错误 helps.")
        self.assertFalse(report.ok)
        self.assertIn("unmatched-open", {issue.code for issue in report.errors})

    def test_summary_mismatch_is_rejected(self) -> None:
        source = "QEC helps."
        annotated = """\
<!-- interlinear-source:start -->
> QEC【量子纠错：用冗余编码修正错误】 helps.
<!-- interlinear-source:end -->
本节：2 个新术语 · 0 个复现简注 · 0 个待核项
"""
        report = validator.validate(source, annotated, require_summary=True)
        self.assertFalse(report.ok)
        self.assertIn("summary-counts", {issue.code for issue in report.errors})

    def test_density_limit_is_enforced(self) -> None:
        source = "A B C D."
        annotated = "A【甲：概念甲】 B【乙：概念乙】 C【丙：概念丙】 D【丁：概念丁】."
        report = validator.validate(source, annotated)
        self.assertFalse(report.ok)
        self.assertIn("annotation-density", {issue.code for issue in report.errors})

    def test_annotation_inside_inline_math_is_rejected(self) -> None:
        source = r"The state is \( |\psi\rangle \)."
        annotated = (
            r"The state is \( |\psi\rangle"
            "【量子态：描述量子系统的信息载体】"
            r" \)."
        )
        report = validator.validate(source, annotated)
        self.assertFalse(report.ok)
        self.assertIn("protected-inline", {issue.code for issue in report.errors})

    def test_pending_and_inferred_annotations_are_counted(self) -> None:
        source = "A B."
        annotated = """\
<!-- interlinear-source:start -->
> A【⚠️推断：这里可能表示假设 A】 B【🔍待核：需查原论文定义】.
<!-- interlinear-source:end -->
本节：1 个新术语 · 0 个复现简注 · 1 个待核项
"""
        report = validator.validate(source, annotated, require_summary=True)
        self.assertTrue(report.ok, report.errors)
        self.assertEqual(report.inferred_items, 1)
        self.assertEqual(report.pending_items, 1)
        self.assertEqual(report.new_terms, 1)

    def test_cli_emits_json_report(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.txt"
            annotated = root / "annotated.md"
            source.write_text("QEC helps.", encoding="utf-8")
            annotated.write_text(
                """\
<!-- interlinear-source:start -->
> QEC【量子纠错：用冗余编码修正错误】 helps.
<!-- interlinear-source:end -->
本节：1 个新术语 · 0 个复现简注 · 0 个待核项
""",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(MODULE_PATH),
                    str(source),
                    str(annotated),
                    "--require-summary",
                    "--json",
                ],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["source_matches"])
        self.assertEqual(payload["annotations"], 1)


if __name__ == "__main__":
    unittest.main()
