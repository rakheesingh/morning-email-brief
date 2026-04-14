import logging
import sys
import tty
import termios
from pathlib import Path
from typing import List


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
