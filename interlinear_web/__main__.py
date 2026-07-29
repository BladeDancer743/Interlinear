"""Run the Interlinear local web workbench."""

from __future__ import annotations

import argparse
import os
import threading
import webbrowser
from pathlib import Path

import uvicorn


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Launch the local Interlinear paper workbench."
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8765, type=int)
    parser.add_argument("--library", type=Path)
    parser.add_argument("--open", action="store_true", dest="open_browser")
    args = parser.parse_args()

    if args.library:
        os.environ["INTERLINEAR_LIBRARY"] = str(args.library.resolve())

    url = f"http://{args.host}:{args.port}"
    print(f"Interlinear Paper Workbench: {url}")
    print("All document processing stays on this machine.")
    if args.open_browser:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    uvicorn.run(
        "interlinear_web.app:app",
        host=args.host,
        port=args.port,
        log_level="info",
    )


if __name__ == "__main__":
    main()
