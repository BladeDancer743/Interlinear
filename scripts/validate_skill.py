#!/usr/bin/env python3
"""Validate the installable Interlinear skill and repository claims."""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path
from urllib.parse import unquote

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "interlinear"
SKILL_FILE = SKILL_DIR / "SKILL.md"
README = ROOT / "README.md"
TERM_REFERENCE = SKILL_DIR / "references" / "quantum-terminology.md"
OPENAI_YAML = SKILL_DIR / "agents" / "openai.yaml"
ANNOTATION_VALIDATOR = SKILL_DIR / "scripts" / "validate_annotation.py"
ANNOTATION_TESTS = ROOT / "tests" / "test_validate_annotation.py"
WEB_LAYOUT = ROOT / "docs" / "annotation-layout.md"
WEB_PACKAGE = ROOT / "interlinear_web"
IGNORED_PARTS = {
    ".git",
    ".interlinear-web",
    ".venv",
    "node_modules",
    "papers",
    "venv",
}


def is_runtime_path(path: Path) -> bool:
    return any(part in IGNORED_PARTS for part in path.relative_to(ROOT).parts)


class Validation:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.checks = 0

    def require(self, condition: bool, message: str) -> None:
        self.checks += 1
        if not condition:
            self.errors.append(message)


def parse_frontmatter(
    path: Path, validation: Validation
) -> tuple[dict[str, object], str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\r?\n(.*?)\r?\n---\r?\n", text, re.DOTALL)
    validation.require(match is not None, f"{path}: missing YAML frontmatter")
    if match is None:
        return {}, text

    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        validation.errors.append(f"{path}: invalid YAML: {exc}")
        return {}, text

    validation.require(isinstance(data, dict), f"{path}: frontmatter must be a mapping")
    return data if isinstance(data, dict) else {}, text


def validate_skill(validation: Validation) -> None:
    validation.require(SKILL_FILE.is_file(), "interlinear/SKILL.md is required")
    validation.require(
        OPENAI_YAML.is_file(), "interlinear/agents/openai.yaml is required"
    )
    validation.require(
        ANNOTATION_VALIDATOR.is_file(),
        "interlinear/scripts/validate_annotation.py is required",
    )
    validation.require(
        ANNOTATION_TESTS.is_file(),
        "tests/test_validate_annotation.py is required",
    )
    if not SKILL_FILE.is_file():
        return

    metadata, text = parse_frontmatter(SKILL_FILE, validation)
    validation.require(
        set(metadata) == {"name", "description"},
        "SKILL.md frontmatter must contain only name and description",
    )

    name = metadata.get("name")
    description = metadata.get("description")
    validation.require(name == SKILL_DIR.name, "skill name must match its directory")
    validation.require(
        isinstance(name, str) and re.fullmatch(r"[a-z0-9-]{1,64}", name) is not None,
        "skill name must use lowercase letters, digits, and hyphens",
    )
    validation.require(
        isinstance(description, str) and len(description.strip()) >= 80,
        "skill description must explain capability and trigger contexts",
    )
    validation.require(
        len(text.splitlines()) < 500,
        "core SKILL.md must stay below 500 lines; move details to references",
    )

    for reference in (
        "annotation-policy.md",
        "geometric-intuition.md",
        "paper-acquisition.md",
        "quantum-terminology.md",
    ):
        validation.require(
            (SKILL_DIR / "references" / reference).is_file(),
            f"missing required reference: {reference}",
        )

    if OPENAI_YAML.is_file():
        try:
            agent_data = yaml.safe_load(OPENAI_YAML.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            validation.errors.append(f"{OPENAI_YAML}: invalid YAML: {exc}")
        else:
            interface = (
                agent_data.get("interface", {}) if isinstance(agent_data, dict) else {}
            )
            validation.require(
                isinstance(interface.get("display_name"), str),
                "agents/openai.yaml requires interface.display_name",
            )
            short = interface.get("short_description", "")
            validation.require(
                isinstance(short, str) and 25 <= len(short) <= 64,
                "short_description must contain 25–64 characters",
            )
            prompt = interface.get("default_prompt", "")
            validation.require(
                isinstance(prompt, str) and "$interlinear" in prompt,
                "default_prompt must explicitly mention $interlinear",
            )


def validate_surface_boundary(validation: Validation) -> None:
    skill_text = SKILL_FILE.read_text(encoding="utf-8")
    policy_text = (SKILL_DIR / "references" / "annotation-policy.md").read_text(
        encoding="utf-8"
    )
    validation.require(
        "Treat this Skill as the terminal/chat surface" in skill_text,
        "SKILL.md must declare the terminal/chat surface",
    )
    validation.require(
        "Do not start `interlinear_web`" in skill_text,
        "SKILL.md must prohibit implicit Web startup",
    )
    validation.require(
        "annotation-layout.md" not in skill_text + policy_text,
        "the terminal Skill must not load Web layout instructions",
    )
    validation.require(
        not (SKILL_DIR / "references" / "annotation-layout.md").exists(),
        "Web layout instructions must stay outside the installable Skill",
    )
    validation.require(
        WEB_LAYOUT.is_file(),
        "docs/annotation-layout.md is required for the Web surface",
    )
    validation.require(
        (WEB_PACKAGE / "static" / "layout.js").is_file(),
        "the Web layout engine must stay in interlinear_web",
    )
    validation.require(
        (WEB_PACKAGE / "__main__.py").is_file(),
        "the Web workbench requires its independent module entry point",
    )
    for python_file in WEB_PACKAGE.rglob("*.py"):
        source = python_file.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(python_file))
        imports_terminal_skill = any(
            (
                isinstance(node, ast.Import)
                and any(
                    alias.name == "interlinear" or alias.name.startswith("interlinear.")
                    for alias in node.names
                )
            )
            or (
                isinstance(node, ast.ImportFrom)
                and (
                    node.module == "interlinear"
                    or str(node.module).startswith("interlinear.")
                )
            )
            for node in ast.walk(tree)
        )
        dynamic_import = re.search(
            r"(?:import_module|__import__)\(\s*['\"]interlinear(?:[.'\"])",
            source,
        )
        validation.require(
            not imports_terminal_skill and dynamic_import is None,
            f"{python_file.relative_to(ROOT)} must not import the terminal Skill",
        )


def validate_links(validation: Validation) -> None:
    link_pattern = re.compile(r"!?\[[^\]]*]\(([^)]+)\)")
    for markdown in sorted(ROOT.rglob("*.md")):
        if is_runtime_path(markdown):
            continue
        text = markdown.read_text(encoding="utf-8")
        for raw_target in link_pattern.findall(text):
            target = raw_target.strip().split(maxsplit=1)[0].strip("<>")
            if not target or target.startswith(("#", "http://", "https://", "mailto:")):
                continue
            local = unquote(target.split("#", 1)[0])
            if not local:
                continue
            resolved = (markdown.parent / local).resolve()
            validation.require(
                resolved.exists(),
                f"{markdown.relative_to(ROOT)}: broken local link {target}",
            )


def validate_claims_and_privacy(validation: Validation) -> None:
    readme = README.read_text(encoding="utf-8")
    terms = TERM_REFERENCE.read_text(encoding="utf-8")
    term_count = len(re.findall(r"(?m)^- .+ → ", terms))
    metric = re.search(r"(\d+) 个量子术语族", readme)
    validation.require(metric is not None, "README must report the terminology metric")
    if metric is not None:
        validation.require(
            int(metric.group(1)) == term_count,
            f"README claims {metric.group(1)} term families, source contains {term_count}",
        )

    core_lines = len(SKILL_FILE.read_text(encoding="utf-8").splitlines())
    line_metric = re.search(r"(\d+) 行核心工作流", readme)
    validation.require(
        line_metric is not None, "README must report the core line metric"
    )
    if line_metric is not None:
        validation.require(
            int(line_metric.group(1)) == core_lines,
            f"README claims {line_metric.group(1)} core lines, source contains "
            f"{core_lines}",
        )

    private_path_patterns = (
        re.compile(r"(?i)[a-z]:\\users\\[^\\\s]+"),
        re.compile("/" + r"Users/[^/\s]+"),
        re.compile("/" + r"home/[^/\s]+"),
    )
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or is_runtime_path(path):
            continue
        if path.suffix.lower() not in {".md", ".py", ".yml", ".yaml", ".svg"}:
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in private_path_patterns:
            validation.require(
                pattern.search(text) is None,
                f"{path.relative_to(ROOT)} contains a hardcoded personal path",
            )

    active_svg = re.compile(r"(?i)<script|<foreignObject|javascript:")
    for svg in ROOT.rglob("*.svg"):
        if is_runtime_path(svg):
            continue
        validation.require(
            active_svg.search(svg.read_text(encoding="utf-8")) is None,
            f"{svg.relative_to(ROOT)} contains active SVG content",
        )


def main() -> int:
    validation = Validation()
    validate_skill(validation)
    validate_surface_boundary(validation)
    validate_links(validation)
    validate_claims_and_privacy(validation)

    if validation.errors:
        print(f"FAILED: {len(validation.errors)} error(s)")
        for error in validation.errors:
            print(f"  - {error}")
        return 1

    term_count = len(
        re.findall(
            r"(?m)^- .+ → ",
            TERM_REFERENCE.read_text(encoding="utf-8"),
        )
    )
    print(
        f"OK: {validation.checks} checks, "
        f"{len(SKILL_FILE.read_text(encoding='utf-8').splitlines())} core lines, "
        f"{term_count} term families"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
