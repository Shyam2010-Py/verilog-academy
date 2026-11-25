#!/usr/bin/env python3
"""Local preview server for Verilog Academy.

Usage:
    C:\\msys64\\ucrt64\\bin\\python.exe tools\\serve.py
    C:\\msys64\\ucrt64\\bin\\python.exe tools\\serve.py --port 8080
"""

from __future__ import annotations

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class PreviewHandler(SimpleHTTPRequestHandler):
    extensions_map = {
        **SimpleHTTPRequestHandler.extensions_map,
        ".html": "text/html; charset=utf-8",
        ".css": "text/css; charset=utf-8",
        ".js": "text/javascript; charset=utf-8",
        ".json": "application/json; charset=utf-8",
        ".svg": "image/svg+xml",
        ".woff2": "font/woff2",
        ".v": "text/plain; charset=utf-8",
        ".sv": "text/plain; charset=utf-8",
        ".vcd": "text/plain; charset=utf-8",
    }

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        super().end_headers()

    def log_message(self, format: str, *args) -> None:
        print(f"  {self.address_string()} — {format % args}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Preview the Verilog Academy static site.")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on (default: 8000)")
    parser.add_argument("--bind", default="127.0.0.1", help="Address to bind (default: 127.0.0.1)")
    args = parser.parse_args()

    handler = partial(PreviewHandler, directory=str(ROOT))
    server = ThreadingHTTPServer((args.bind, args.port), handler)

    print("Verilog Academy — local preview")
    print(f"  Root : {ROOT}")
    print(f"  URL  : http://{args.bind}:{args.port}/")
    print("  Stop : Ctrl+C")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping preview server.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
