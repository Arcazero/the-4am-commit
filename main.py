#!/usr/bin/env python3
"""The 4AM Commit: Funniest Agent Bug-Fix Message — make.fun entry.

Reads the single one-line commit message from commit.txt (kept beside
this script), validates it, and writes it to /output/entry.txt: the
line plus one trailing newline, byte-identical to commit.txt.
"""

import argparse
import os
import sys

# Resolve commit.txt against this script's own directory, not the process
# working directory: the grader runs the program with a different cwd,
# and a bare relative path would fail to find the file there.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
COMMIT_PATH = os.path.join(SCRIPT_DIR, "commit.txt")


def load_message() -> str:
    """Read and validate the commit message from commit.txt next to this script.

    The file must hold exactly one line plus one trailing newline, and
    the line must be 1-200 characters with no leading/trailing space.
    Error messages name the file and the offending value so a failed
    run says what to fix instead of just failing.
    """
    try:
        with open(COMMIT_PATH, "r", encoding="utf-8", newline="") as f:
            text = f.read()
    except FileNotFoundError:
        raise ValueError(f"commit file not found: {COMMIT_PATH}")
    except UnicodeDecodeError as exc:
        raise ValueError(f"commit.txt is not valid UTF-8: {exc}")
    if not text.endswith("\n"):
        raise ValueError("commit.txt must end with exactly one trailing newline")
    message = text[:-1]
    if not message:
        raise ValueError("commit message is empty")
    if message != message.strip():
        raise ValueError("commit message has leading or trailing whitespace")
    if "\n" in message or "\r" in message:
        raise ValueError(
            f"commit message must be a single line, found {text.count(chr(10))} lines"
        )
    if len(message) > 200:
        raise ValueError(
            f"commit message is {len(message)} characters, over the 200 limit"
        )
    if text != message + "\n":
        raise ValueError("commit.txt must be exactly one line plus one newline")
    return message


def verify_output(path: str) -> None:
    """Prove the written entry is byte-identical to commit.txt."""
    with open(path, "rb") as f:
        written = f.read()
    with open(COMMIT_PATH, "rb") as f:
        source = f.read()
    if written != source:
        raise ValueError(
            f"output {path} ({len(written)} bytes) is not byte-identical "
            f"to commit.txt ({len(source)} bytes)"
        )


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(
        description="Write the one-line commit message to /output/entry.txt."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate commit.txt only, without writing entry.txt",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="output directory for entry.txt "
        "(default: $MAKEFUN_OUTPUT_DIR or /output)",
    )
    args = parser.parse_args(argv)
    message = load_message()
    if args.check:
        print(f"ok: {len(message)} characters, one line")
        return
    output_dir = args.out or os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "entry.txt")
    # Atomic write: a crash mid-write must never leave a partial
    # entry.txt behind, so write a temp file in the same directory,
    # flush it to disk, then rename it over the destination.
    tmp_path = path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(message + "\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path, path)
    verify_output(path)
    print(message)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
