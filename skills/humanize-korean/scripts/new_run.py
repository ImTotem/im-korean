"""run 디렉터리 `_workspace/YYYY-MM-DD-NNN-TAG/` 를 cwd 아래에 만들고 경로를 찍는다.

확인과 생성을 mkdir 한 번으로 끝낸다. 여러 세션이 동시에 돌아도 같은 번호를
둘이 잡지 못한다. TAG 는 세션 구분자라 `--tag` 가 없으면 여기서 무작위로 만든다.

사용법:
    python3 new_run.py                 # TAG 를 스스로 만든다
    python3 new_run.py --tag a3f9      # 같은 run 에서 TAG 를 재사용할 때

종료 코드: 0 성공 / 2 자리가 없음 또는 TAG 형식 오류
"""

import argparse
import re
import secrets
import sys
from datetime import date
from pathlib import Path

import console

_TAG_RE = re.compile(r"^[0-9a-z]{1,16}$")
_MAX_SEQ = 999


def create_run_dir(workspace: Path, tag: str) -> Path:
    workspace.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    for n in range(1, _MAX_SEQ + 1):
        candidate = workspace / f"{today}-{n:03d}-{tag}"
        try:
            candidate.mkdir(exist_ok=False)
            return candidate
        except FileExistsError:
            continue
    raise SystemExit(f"run dir 자리를 못 찾았다: {workspace}/{today}-NNN-{tag} 가 {_MAX_SEQ}개까지 찼다")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--tag", help="세션 구분자(소문자·숫자 1~16자). 없으면 새로 만든다.")
    args = parser.parse_args()
    tag = args.tag if args.tag else secrets.token_hex(2)
    if not _TAG_RE.match(tag):
        print(f"TAG 형식 오류: {tag!r} (소문자·숫자 1~16자)", file=sys.stderr)
        return 2
    print(create_run_dir(Path.cwd() / "_workspace", tag))
    return 0


if __name__ == "__main__":
    console.force_utf8_console()
    sys.exit(main())
