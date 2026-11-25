#!/usr/bin/env python3
"""Headless Chrome audit helper for Verilog Academy.

Uses the Chrome DevTools Protocol over a minimal WebSocket client, so the
project stays dependency-free. Run the preview server first, then:

    python tools/browser_audit.py --url http://127.0.0.1:8000/quizzes/index.html

The module is also imported by verify_phase8.py for the full browser pass.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import socket
import struct
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
DEFAULT_PORT = 9333


class CDPError(RuntimeError):
    pass


class WebSocket:
    def __init__(self, url: str, timeout: float = 20.0):
        if not url.startswith("ws://"):
            raise CDPError(f"Unsupported WebSocket URL: {url}")
        host_port, path = url[5:].split("/", 1)
        host, port = host_port.split(":")
        self.sock = socket.create_connection((host, int(port)), timeout=timeout)
        self.sock.settimeout(timeout)
        key = base64.b64encode(os.urandom(16)).decode("ascii")
        request = (
            f"GET /{path} HTTP/1.1\r\n"
            f"Host: {host}:{port}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            "Sec-WebSocket-Version: 13\r\n\r\n"
        )
        self.sock.sendall(request.encode("ascii"))
        response = b""
        while b"\r\n\r\n" not in response:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise CDPError("WebSocket handshake closed early")
            response += chunk
        status = response.split(b"\r\n", 1)[0]
        if b"101" not in status:
            raise CDPError(f"WebSocket handshake failed: {status!r}")

    def send_text(self, text: str) -> None:
        payload = text.encode("utf-8")
        mask = os.urandom(4)
        header = bytearray([0x81])
        length = len(payload)
        if length < 126:
            header.append(0x80 | length)
        elif length < 65536:
            header.append(0x80 | 126)
            header.extend(struct.pack("!H", length))
        else:
            header.append(0x80 | 127)
            header.extend(struct.pack("!Q", length))
        header.extend(mask)
        masked = bytes(byte ^ mask[index % 4] for index, byte in enumerate(payload))
        self.sock.sendall(bytes(header) + masked)

    def _read_exact(self, count: int) -> bytes:
        data = b""
        while len(data) < count:
            chunk = self.sock.recv(count - len(data))
            if not chunk:
                raise CDPError("WebSocket closed while reading")
            data += chunk
        return data

    def recv_text(self) -> str:
        fragments: list[bytes] = []
        while True:
            first, second = self._read_exact(2)
            fin = bool(first & 0x80)
            opcode = first & 0x0F
            masked = bool(second & 0x80)
            length = second & 0x7F
            if length == 126:
                length = struct.unpack("!H", self._read_exact(2))[0]
            elif length == 127:
                length = struct.unpack("!Q", self._read_exact(8))[0]
            mask = self._read_exact(4) if masked else None
            payload = self._read_exact(length)
            if mask:
                payload = bytes(byte ^ mask[index % 4] for index, byte in enumerate(payload))

            if opcode == 0x8:
                raise CDPError("WebSocket closed by Chrome")
            if opcode == 0x9:
                self._send_control(0xA, payload)
                continue
            if opcode == 0xA:
                continue
            if opcode in (0x1, 0x2, 0x0):
                fragments.append(payload)
                if fin:
                    return b"".join(fragments).decode("utf-8", errors="replace")

    def _send_control(self, opcode: int, payload: bytes) -> None:
        mask = os.urandom(4)
        header = bytearray([0x80 | opcode])
        length = len(payload)
        if length < 126:
            header.append(0x80 | length)
        else:
            header.append(0x80 | 126)
            header.extend(struct.pack("!H", length))
        header.extend(mask)
        masked = bytes(byte ^ mask[index % 4] for index, byte in enumerate(payload))
        self.sock.sendall(bytes(header) + masked)

    def close(self) -> None:
        try:
            self._send_control(0x8, b"")
        except OSError:
            pass
        try:
            self.sock.close()
        except OSError:
            pass


class Session:
    def __init__(self, ws_url: str):
        self.ws = WebSocket(ws_url)
        self.next_id = 0
        self.events: list[dict[str, Any]] = []
        for method in ("Page.enable", "Runtime.enable", "Log.enable", "Network.enable"):
            self.call(method)

    def call(self, method: str, **params: Any) -> dict[str, Any]:
        self.next_id += 1
        request_id = self.next_id
        self.ws.send_text(json.dumps({"id": request_id, "method": method, "params": params}))
        while True:
            message = json.loads(self.ws.recv_text())
            if message.get("id") == request_id:
                if "error" in message:
                    raise CDPError(f"{method}: {message['error']}")
                return message.get("result", {})
            self.events.append(message)

    def evaluate(self, expression: str, await_promise: bool = True) -> Any:
        result = self.call(
            "Runtime.evaluate",
            expression=expression,
            returnByValue=True,
            awaitPromise=await_promise,
            userGesture=True,
        )
        if result.get("exceptionDetails"):
            detail = result["exceptionDetails"]
            text = detail.get("exception", {}).get("description") or detail.get("text")
            raise CDPError(f"JavaScript error: {text}")
        return result.get("result", {}).get("value")

    def navigate(self, url: str, wait: float = 0.0) -> None:
        self.call("Page.navigate", url=url)
        deadline = time.time() + 15
        while time.time() < deadline:
            try:
                ready = self.evaluate("document.readyState", await_promise=False)
            except CDPError:
                ready = None
            if ready == "complete":
                break
            time.sleep(0.1)
        if wait:
            time.sleep(wait)

    def set_viewport(self, width: int, height: int, mobile: bool = False) -> None:
        self.call(
            "Emulation.setDeviceMetricsOverride",
            width=width,
            height=height,
            deviceScaleFactor=1,
            mobile=mobile,
        )

    def screenshot(self, path: Path, full_page: bool = False) -> None:
        if full_page:
            metrics = self.call("Page.getLayoutMetrics")
            size = metrics.get("cssContentSize") or metrics.get("contentSize")
            height = int(size["height"])
            self.call(
                "Emulation.setDeviceMetricsOverride",
                width=int(size["width"]),
                height=height,
                deviceScaleFactor=1,
                mobile=False,
            )
        data = self.call("Page.captureScreenshot", format="png", captureBeyondViewport=full_page)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(base64.b64decode(data["data"]))

    def drain_errors(self) -> list[str]:
        # Force a round trip so queued events are delivered.
        self.evaluate("1", await_promise=False)
        problems: list[str] = []
        for event in self.events:
            method = event.get("method")
            params = event.get("params", {})
            if method == "Runtime.exceptionThrown":
                detail = params.get("exceptionDetails", {})
                text = detail.get("exception", {}).get("description") or detail.get("text")
                problems.append(f"exception: {text}")
            elif method == "Runtime.consoleAPICalled" and params.get("type") == "error":
                args = params.get("args", [])
                text = " ".join(str(arg.get("value", arg.get("description", ""))) for arg in args)
                problems.append(f"console.error: {text}")
            elif method == "Log.entryAdded":
                entry = params.get("entry", {})
                if entry.get("level") == "error":
                    problems.append(f"log: {entry.get('text')}")
            elif method == "Network.loadingFailed":
                if not params.get("canceled"):
                    problems.append(f"network failed: {params.get('errorText')}")
            elif method == "Network.responseReceived":
                response = params.get("response", {})
                if int(response.get("status", 0)) >= 400:
                    problems.append(f"http {response.get('status')}: {response.get('url')}")
        self.events = []
        return problems


class Chrome:
    def __init__(self, port: int = DEFAULT_PORT, headless: bool = True):
        self.port = port
        self.headless = headless
        self.profile = Path(tempfile.mkdtemp(prefix="va-chrome-"))
        self.process: subprocess.Popen | None = None

    def __enter__(self) -> "Chrome":
        if not CHROME.is_file():
            raise RuntimeError(f"Chrome not found at {CHROME}")
        flags = [
            str(CHROME),
            f"--remote-debugging-port={self.port}",
            f"--user-data-dir={self.profile}",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-background-networking",
            "--disable-component-update",
            "--disable-sync",
            "--disable-extensions",
            "--disable-features=Translate,MediaRouter",
            "--remote-allow-origins=*",
            "about:blank",
        ]
        if self.headless:
            flags.insert(1, "--headless=new")
        self.process = subprocess.Popen(
            flags,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        deadline = time.time() + 20
        while time.time() < deadline:
            try:
                with urllib.request.urlopen(
                    f"http://127.0.0.1:{self.port}/json/version", timeout=1
                ) as response:
                    json.loads(response.read().decode("utf-8"))
                return self
            except Exception:
                time.sleep(0.2)
        raise RuntimeError("Chrome did not expose the DevTools endpoint")

    def new_page(self, url: str = "about:blank") -> Session:
        request = urllib.request.Request(
            f"http://127.0.0.1:{self.port}/json/new?{urllib.parse.quote(url, safe=':/?&=%')}",
            method="PUT",
        )
        with urllib.request.urlopen(request, timeout=10) as response:
            target = json.loads(response.read().decode("utf-8"))
        session = Session(target["webSocketDebuggerUrl"])
        if url != "about:blank":
            session.navigate(url, wait=0.4)
        return session

    def __exit__(self, exc_type, exc, tb) -> None:
        if self.process and self.process.poll() is None:
            try:
                urllib.request.urlopen(f"http://127.0.0.1:{self.port}/json/close", timeout=1)
            except Exception:
                pass
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
        # Chrome leaves locks behind; best-effort cleanup.
        import shutil

        shutil.rmtree(self.profile, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8000/index.html")
    parser.add_argument("--width", type=int, default=1440)
    parser.add_argument("--height", type=int, default=900)
    parser.add_argument("--mobile", action="store_true")
    parser.add_argument("--screenshot", type=Path)
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--eval", dest="expression")
    parser.add_argument("--wait", type=float, default=0.6)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args()

    with Chrome(port=args.port) as chrome:
        session = chrome.new_page("about:blank")
        session.set_viewport(args.width, args.height, mobile=args.mobile)
        session.navigate(args.url, wait=args.wait)
        if args.expression:
            print(json.dumps(session.evaluate(args.expression), indent=2))
        if args.screenshot:
            session.screenshot(args.screenshot, full_page=args.full)
            print(f"screenshot: {args.screenshot}")
        errors = session.drain_errors()
        print(f"errors: {len(errors)}")
        for problem in errors:
            print(f"  - {problem}")
        session.ws.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
