"""Optional CAJ-to-PDF conversion adapter.

CAJ is a proprietary container with several incompatible internal variants.
Interlinear therefore delegates conversion to a local, user-selected converter
and validates the resulting PDF instead of claiming native support.
"""

from __future__ import annotations

import os
import shlex
import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path


class CajConversionError(RuntimeError):
    """Raised when a CAJ converter is unavailable or conversion fails."""


@dataclass(frozen=True)
class CajCapability:
    available: bool
    provider: str
    detail: str

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def _configured_command() -> list[str] | None:
    template = os.environ.get("INTERLINEAR_CAJ_COMMAND", "").strip()
    if not template:
        return None
    if "{input}" not in template or "{output}" not in template:
        raise CajConversionError(
            "INTERLINEAR_CAJ_COMMAND 必须同时包含 {input} 和 {output} 占位符。"
        )
    parts = shlex.split(template, posix=os.name != "nt")
    if os.name == "nt":
        parts = [part.strip('"') for part in parts]
    return parts


def _detected_command() -> tuple[list[str] | None, CajCapability]:
    try:
        configured = _configured_command()
    except CajConversionError as exc:
        return None, CajCapability(False, "configured", str(exc))

    if configured:
        return configured, CajCapability(
            True,
            "configured",
            "使用 INTERLINEAR_CAJ_COMMAND 指定的本地转换器。",
        )

    executable = shutil.which("caj2pdf")
    if executable:
        return (
            [executable, "convert", "{input}", "-o", "{output}"],
            CajCapability(True, "caj2pdf", f"已检测到 {executable}"),
        )

    return None, CajCapability(
        False,
        "none",
        "未检测到 CAJ 转换器；PDF 可直接使用。可配置 "
        "INTERLINEAR_CAJ_COMMAND，或先在 CAJViewer 中打印为 PDF。",
    )


def capability() -> CajCapability:
    """Report whether a local CAJ converter can be invoked."""

    return _detected_command()[1]


def convert(source: Path, output: Path, timeout: int = 240) -> None:
    """Convert *source* to *output* using a shell-free local command."""

    template, status = _detected_command()
    if template is None:
        raise CajConversionError(status.detail)

    command = [
        token.replace("{input}", str(source)).replace("{output}", str(output))
        for token in template
    ]
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise CajConversionError(f"CAJ 转换器无法完成任务：{exc}") from exc

    if completed.returncode != 0:
        diagnostic = (completed.stderr or completed.stdout or "").strip()
        if len(diagnostic) > 800:
            diagnostic = diagnostic[-800:]
        raise CajConversionError(
            f"CAJ 转换失败（退出码 {completed.returncode}）。"
            + (f" {diagnostic}" if diagnostic else "")
        )
    if not output.is_file() or output.stat().st_size < 5:
        raise CajConversionError("CAJ 转换器未生成有效的 PDF 文件。")
    with output.open("rb") as stream:
        signature = stream.read(5)
    if signature != b"%PDF-":
        raise CajConversionError("CAJ 转换结果不是可识别的 PDF。")
