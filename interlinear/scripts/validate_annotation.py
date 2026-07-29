#!/usr/bin/env python3
"""Validate Interlinear annotations against an unchanged source passage."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

SOURCE_START = "<!-- interlinear-source:start -->"
SOURCE_END = "<!-- interlinear-source:end -->"
SUMMARY_PATTERN = re.compile(
    r"本节：(?P<new>\d+) 个新术语 · "
    r"(?P<repeat>\d+) 个复现简注 · "
    r"(?P<pending>\d+) 个待核项"
)
BLOCKQUOTE_PREFIX = re.compile(r"(?m)^[ \t]{0,3}> ?")
WHITESPACE = re.compile(r"\s+")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})")


@dataclass(frozen=True)
class Issue:
    code: str
    message: str
    line: int | None = None


@dataclass(frozen=True)
class Annotation:
    content: str
    line: int
    start: int
    end: int


@dataclass
class Report:
    source_mode: str
    source_matches: bool
    annotations: int
    new_terms: int
    repeat_notes: int
    pending_items: int
    inferred_items: int
    errors: list[Issue] = field(default_factory=list)
    warnings: list[Issue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["ok"] = self.ok
        return payload


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def extract_source_region(
    annotated: str,
) -> tuple[str, str, list[Issue], list[Issue]]:
    """Extract the annotated source unit from markers, blockquotes, or the file."""
    errors: list[Issue] = []
    warnings: list[Issue] = []
    starts = [
        match.start() for match in re.finditer(re.escape(SOURCE_START), annotated)
    ]
    ends = [match.start() for match in re.finditer(re.escape(SOURCE_END), annotated)]

    if starts or ends:
        if len(starts) != 1 or len(ends) != 1:
            errors.append(
                Issue(
                    "source-markers",
                    "expected exactly one source start marker and one source end marker",
                )
            )
            return annotated, "invalid-markers", errors, warnings
        start = starts[0] + len(SOURCE_START)
        end = ends[0]
        if start >= end:
            errors.append(
                Issue(
                    "source-markers", "source end marker must follow the start marker"
                )
            )
            return annotated, "invalid-markers", errors, warnings
        return annotated[start:end], "markers", errors, warnings

    quoted = [
        line for line in annotated.splitlines() if re.match(r"^[ \t]{0,3}>", line)
    ]
    if quoted:
        warnings.append(
            Issue(
                "implicit-source-region",
                "using all Markdown blockquote lines as the source region; "
                "explicit markers are safer",
            )
        )
        return "\n".join(quoted), "blockquotes", errors, warnings

    warnings.append(
        Issue(
            "whole-document-source",
            "using the whole annotated document as the source region; "
            "add source markers when the file contains headings or a glossary",
        )
    )
    return annotated, "whole-document", errors, warnings


def parse_annotations(text: str) -> tuple[list[Annotation], list[Issue]]:
    annotations: list[Annotation] = []
    errors: list[Issue] = []
    index = 0

    while index < len(text):
        char = text[index]
        if char == "】":
            errors.append(
                Issue(
                    "unmatched-close",
                    "found a closing annotation delimiter without an opening delimiter",
                    line_number(text, index),
                )
            )
            index += 1
            continue
        if char != "【":
            index += 1
            continue

        close = text.find("】", index + 1)
        nested = text.find("【", index + 1, close if close != -1 else len(text))
        if close == -1:
            errors.append(
                Issue(
                    "unmatched-open",
                    "annotation is missing its closing delimiter",
                    line_number(text, index),
                )
            )
            break
        if nested != -1:
            errors.append(
                Issue(
                    "nested-annotation",
                    "nested annotation delimiters are not allowed",
                    line_number(text, nested),
                )
            )

        content = text[index + 1 : close].strip()
        annotation = Annotation(
            content=content,
            line=line_number(text, index),
            start=index,
            end=close + 1,
        )
        annotations.append(annotation)
        index = close + 1

    return annotations, errors


def strip_annotations(text: str, annotations: list[Annotation]) -> str:
    result = text
    for annotation in reversed(annotations):
        result = result[: annotation.start] + result[annotation.end :]
    return result


def normalize_source(text: str) -> str:
    text = text.replace(SOURCE_START, "").replace(SOURCE_END, "")
    text = BLOCKQUOTE_PREFIX.sub("", text)
    return WHITESPACE.sub(" ", text).strip()


def protected_lines(text: str) -> set[int]:
    protected: set[int] = set()
    fence_token: str | None = None
    display_math = False

    for number, line in enumerate(text.splitlines(), start=1):
        fence_match = FENCE.match(line)
        if fence_match:
            token = fence_match.group(1)
            protected.add(number)
            if fence_token is None:
                fence_token = token[0]
            elif token[0] == fence_token:
                fence_token = None
            continue

        if fence_token is not None:
            protected.add(number)
            continue

        if line.strip() == "$$":
            protected.add(number)
            display_math = not display_math
            continue
        if display_math:
            protected.add(number)

    return protected


def inside_inline_protected_span(line: str, column: int) -> bool:
    prefix = line[:column]
    unescaped_backticks = len(re.findall(r"(?<!\\)`", prefix))
    if unescaped_backticks % 2:
        return True

    dollars = [
        match.start()
        for match in re.finditer(r"(?<!\\)\$", prefix)
        if not (
            (match.start() > 0 and prefix[match.start() - 1] == "$")
            or (match.start() + 1 < len(prefix) and prefix[match.start() + 1] == "$")
        )
    ]
    if len(dollars) % 2:
        return True

    if prefix.rfind(r"\(") > prefix.rfind(r"\)"):
        return True
    return prefix.rfind("[") > prefix.rfind("]")


def validate_annotation_shapes(
    text: str, annotations: list[Annotation]
) -> tuple[list[Issue], list[Issue]]:
    errors: list[Issue] = []
    warnings: list[Issue] = []
    fenced = protected_lines(text)
    lines = text.splitlines()

    for annotation in annotations:
        content = annotation.content
        if not content:
            errors.append(
                Issue(
                    "empty-annotation",
                    "annotation content cannot be empty",
                    annotation.line,
                )
            )
            continue

        if annotation.line in fenced:
            errors.append(
                Issue(
                    "protected-block",
                    "annotations cannot be inserted inside fenced code or display math",
                    annotation.line,
                )
            )

        line_start = text.rfind("\n", 0, annotation.start) + 1
        column = annotation.start - line_start
        current_line = (
            lines[annotation.line - 1] if annotation.line <= len(lines) else ""
        )
        if inside_inline_protected_span(current_line, column):
            errors.append(
                Issue(
                    "protected-inline",
                    "annotation appears inside inline code, math, or a citation",
                    annotation.line,
                )
            )

        if content.startswith("⤴"):
            if len(content) == 1:
                errors.append(
                    Issue(
                        "repeat-shape",
                        "repeat annotations need a concise Chinese label after ⤴",
                        annotation.line,
                    )
                )
        elif content.startswith("🔍待核"):
            if not re.fullmatch(r"🔍待核：\S.*", content):
                errors.append(
                    Issue(
                        "pending-shape",
                        "pending annotations must use 【🔍待核：…】",
                        annotation.line,
                    )
                )
        elif content.startswith("⚠️推断"):
            if not re.fullmatch(r"⚠️推断：\S.*", content):
                errors.append(
                    Issue(
                        "inference-shape",
                        "inferred annotations must use 【⚠️推断：…】",
                        annotation.line,
                    )
                )
        else:
            label, separator, explanation = content.partition("：")
            if not separator or not label.strip() or not explanation.strip():
                errors.append(
                    Issue(
                        "annotation-shape",
                        "first annotations must use 【中文翻译：语境解释】",
                        annotation.line,
                    )
                )

        if len(content) > 80:
            warnings.append(
                Issue(
                    "long-annotation",
                    f"annotation contains {len(content)} characters; consider shortening it",
                    annotation.line,
                )
            )

    return errors, warnings


def density_issues(
    text: str, annotations: list[Annotation], maximum: int
) -> list[Issue]:
    by_start = {annotation.start: annotation for annotation in annotations}
    errors: list[Issue] = []
    sentence_count = 0
    sentence_start = 0
    index = 0

    def finish_sentence(end: int) -> None:
        nonlocal sentence_count, sentence_start
        if sentence_count > maximum:
            preview = normalize_source(text[sentence_start:end])[:80]
            errors.append(
                Issue(
                    "annotation-density",
                    f"sentence has {sentence_count} annotations; maximum is {maximum}: "
                    f"{preview}",
                    line_number(text, sentence_start),
                )
            )
        sentence_count = 0
        sentence_start = end

    while index < len(text):
        annotation = by_start.get(index)
        if annotation is not None:
            sentence_count += 1
            index = annotation.end
            continue

        char = text[index]
        next_char = text[index + 1] if index + 1 < len(text) else ""
        if (
            char in "。！？"
            or (char in ".!?" and (not next_char or next_char.isspace()))
            or (char == "\n" and next_char == "\n")
        ):
            finish_sentence(index + 1)
        index += 1

    finish_sentence(len(text))
    return errors


def validate_summary(
    annotated: str,
    *,
    new_terms: int,
    repeat_notes: int,
    pending_items: int,
    require_summary: bool,
) -> tuple[list[Issue], list[Issue]]:
    errors: list[Issue] = []
    warnings: list[Issue] = []
    summaries = list(SUMMARY_PATTERN.finditer(annotated))

    if not summaries:
        issue = Issue(
            "missing-summary",
            "missing section summary: 本节：N 个新术语 · M 个复现简注 · K 个待核项",
        )
        (errors if require_summary else warnings).append(issue)
        return errors, warnings

    if len(summaries) > 1:
        errors.append(
            Issue(
                "multiple-summaries",
                "validate one source unit at a time; found multiple section summaries",
            )
        )
        return errors, warnings

    summary = summaries[0]
    reported = tuple(int(summary.group(key)) for key in ("new", "repeat", "pending"))
    actual = (new_terms, repeat_notes, pending_items)
    if reported != actual:
        errors.append(
            Issue(
                "summary-counts",
                f"summary reports {reported}, but annotations contain {actual} "
                "(new, repeat, pending)",
                line_number(annotated, summary.start()),
            )
        )
    return errors, warnings


def validate(
    source: str,
    annotated: str,
    *,
    maximum_notes_per_sentence: int = 3,
    require_summary: bool = False,
) -> Report:
    region, mode, region_errors, region_warnings = extract_source_region(annotated)
    annotations, parse_errors = parse_annotations(region)
    shape_errors, shape_warnings = validate_annotation_shapes(region, annotations)

    repeat_notes = sum(item.content.startswith("⤴") for item in annotations)
    pending_items = sum(
        not item.content.startswith("⤴") and "🔍待核" in item.content
        for item in annotations
    )
    inferred_items = sum(item.content.startswith("⚠️推断") for item in annotations)
    new_terms = len(annotations) - pending_items - repeat_notes

    stripped = strip_annotations(region, annotations)
    source_matches = normalize_source(source) == normalize_source(stripped)
    fidelity_errors: list[Issue] = []
    if not source_matches:
        fidelity_errors.append(
            Issue(
                "source-fidelity",
                "annotated source differs from the original after annotations are removed",
            )
        )

    summary_errors, summary_warnings = validate_summary(
        annotated,
        new_terms=new_terms,
        repeat_notes=repeat_notes,
        pending_items=pending_items,
        require_summary=require_summary,
    )
    warnings = region_warnings + shape_warnings + summary_warnings
    if not annotations:
        warnings.append(Issue("no-annotations", "source unit contains no annotations"))

    return Report(
        source_mode=mode,
        source_matches=source_matches,
        annotations=len(annotations),
        new_terms=new_terms,
        repeat_notes=repeat_notes,
        pending_items=pending_items,
        inferred_items=inferred_items,
        errors=(
            region_errors
            + parse_errors
            + shape_errors
            + density_issues(region, annotations, maximum_notes_per_sentence)
            + fidelity_errors
            + summary_errors
        ),
        warnings=warnings,
    )


def print_human(report: Report) -> None:
    status = "OK" if report.ok else "FAILED"
    fidelity = "pass" if report.source_matches else "fail"
    print(
        f"{status}: fidelity={fidelity}, annotations={report.annotations}, "
        f"new={report.new_terms}, repeat={report.repeat_notes}, "
        f"pending={report.pending_items}, inferred={report.inferred_items}, "
        f"source_mode={report.source_mode}"
    )
    for issue in report.errors:
        location = f" line {issue.line}" if issue.line is not None else ""
        print(f"ERROR [{issue.code}]{location}: {issue.message}")
    for issue in report.warnings:
        location = f" line {issue.line}" if issue.line is not None else ""
        print(f"WARN  [{issue.code}]{location}: {issue.message}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Check that an Interlinear annotation preserves its source and follows "
            "the output contract."
        )
    )
    parser.add_argument("source", type=Path, help="UTF-8 file containing exact source")
    parser.add_argument(
        "annotated", type=Path, help="UTF-8 Markdown file containing annotations"
    )
    parser.add_argument(
        "--max-notes-per-sentence",
        type=int,
        default=3,
        metavar="N",
        help="maximum inline notes allowed in one sentence (default: 3)",
    )
    parser.add_argument(
        "--require-summary",
        action="store_true",
        help="fail when the section summary is missing",
    )
    parser.add_argument(
        "--json", action="store_true", help="emit a machine-readable JSON report"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.max_notes_per_sentence < 1:
        print("--max-notes-per-sentence must be at least 1", file=sys.stderr)
        return 2

    try:
        source = args.source.read_text(encoding="utf-8")
        annotated = args.annotated.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        print(f"cannot read input: {exc}", file=sys.stderr)
        return 2

    report = validate(
        source,
        annotated,
        maximum_notes_per_sentence=args.max_notes_per_sentence,
        require_summary=args.require_summary,
    )
    if args.json:
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    else:
        print_human(report)
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())
