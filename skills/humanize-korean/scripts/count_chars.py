"""본문 글자 수를 센다. `<!-- HUMANIZE-SUMMARY` 블록은 뺀다.

사용법:
    python3 count_chars.py _workspace/{run_id}/final.md

출력: `공백포함 공백제외` (공백으로 구분한 정수 둘)
한글이 NFC(완성형)일 때 한 음절이 한 글자로 세어진다.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import console

_SUMMARY_RE = re.compile(r"<!--\s*HUMANIZE-SUMMARY\b.*", re.DOTALL)


def count_chars(text: str) -> tuple[int, int]:
    body = _SUMMARY_RE.sub("", text).strip()
    return len(body), len(re.sub(r"\s", "", body))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("file")
    args = parser.parse_args()
    text = Path(args.file).read_text(encoding="utf-8")
    with_space, without_space = count_chars(text)
    print(with_space, without_space)
    return 0


if __name__ == "__main__":
    console.force_utf8_console()
    sys.exit(main())
