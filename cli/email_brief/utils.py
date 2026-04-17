import logging
import sys
import time
import tty
import termios
from pathlib import Path
from typing import List, Optional
import base64
import re


def get_logger(name: str, log_file: Path) -> logging.Logger:
    """Return a named logger that writes DEBUG+ to the given file."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler(log_file, encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
        logger.addHandler(handler)
    return logger


def select(prompt: str, options: List[str]) -> int:
    """Arrow-key interactive selector. Returns the chosen index."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    selected = 0
    total = len(options)

    def _render():
        sys.stdout.write(f"\033[{total}A")
        for i, opt in enumerate(options):
            marker = "▸" if i == selected else " "
            highlight = "\033[96m\033[1m" if i == selected else "\033[0m"
            sys.stdout.write(f"\r\033[K  {highlight}{marker} {opt}\033[0m\n")
        sys.stdout.flush()

    print(f"  {prompt}\n")
    for opt in options:
        print(f"    {opt}")
    print()
    sys.stdout.write(f"\033[{total + 1}A")
    for i, opt in enumerate(options):
        marker = "▸" if i == selected else " "
        highlight = "\033[96m\033[1m" if i == selected else "\033[0m"
        sys.stdout.write(f"\r\033[K  {highlight}{marker} {opt}\033[0m\n")
    sys.stdout.flush()

    try:
        tty.setraw(fd)
        while True:
            ch = sys.stdin.read(1)

            if ch == "\r" or ch == "\n":
                break

            if ch == "\x03":
                raise KeyboardInterrupt

            if ch == "\x1b":
                seq = sys.stdin.read(2)
                if seq == "[A":
                    selected = (selected - 1) % total
                elif seq == "[B":
                    selected = (selected + 1) % total
                _render()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    sys.stdout.write("\n")
    return selected


def _extract_body(payload: dict) -> str:
    if payload.get("body", {}).get("data"):
        return _decode_base64(payload["body"]["data"])

    parts = payload.get("parts", [])
    for mime in ["text/plain", "text/html"]:
        for part in parts:
            if part.get("mimeType") == mime and part.get("body", {}).get("data"):
                text = _decode_base64(part["body"]["data"])
                if mime == "text/html":
                    text = re.sub(r"<[^>]*>", " ", text)
                    text = re.sub(r"\s+", " ", text).strip()
                return text

    for part in parts:
        nested = _extract_body(part)
        if nested:
            return nested

    return ""

def _decode_base64(data: str) -> str:
    padded = data.replace("-", "+").replace("_", "/")
    return base64.b64decode(padded + "==").decode("utf-8", errors="replace")

def _count_images(payload: dict) -> tuple[int, bool]:
    """Count inline marketing <img> tags and detect real user attachments.
    Returns (inline_img_count, has_real_attachment).
    """
    inline = 0
    has_attachment = False
    mime = payload.get("mimeType", "")

    if mime.startswith("image/") and payload.get("filename"):
        has_attachment = True

    body_data = payload.get("body", {}).get("data", "")
    if body_data and "text/html" in mime:
        html = _decode_base64(body_data)
        inline += len(re.findall(r"<img\s", html, re.IGNORECASE))

    for part in payload.get("parts", []):
        child_inline, child_attach = _count_images(part)
        inline += child_inline
        if child_attach:
            has_attachment = True

    return inline, has_attachment


def get_last_run(last_run_file: Path) -> Optional[int]:
    """Return the last run epoch timestamp (seconds), or None if never run."""
    if not last_run_file.exists():
        return None
    try:
        return int(last_run_file.read_text().strip())
    except (ValueError, OSError):
        return None


def save_last_run(last_run_file: Path):
    """Save current epoch timestamp (seconds) as the last run time."""
    last_run_file.write_text(str(int(time.time())))

