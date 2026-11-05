"""런타임별 생성 파일을 만든다. 원본은 agents/*.md 와 output-styles/fluent-korean.md 다.

생성물(직접 편집 금지):
    codex/agents/<이름>.toml      Codex 에이전트 정의 (name, description, developer_instructions)
    opencode/agents/<이름>.md     OpenCode 에이전트 정의 (description, mode: subagent)
    instructions/fluent-korean.md 출력 스타일의 본문. Codex AGENTS.md 와 OpenCode instructions 가 쓴다.

사용법:
    python3 tools/build_runtime_files.py            # 생성
    python3 tools/build_runtime_files.py --check    # 최신 여부만 검사(CI용). 어긋나면 종료 코드 1
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skills" / "humanize-korean" / "scripts"))

import console  # noqa: E402  (Windows cp949 콘솔에서 한글 출력이 죽지 않게 한다)

AGENTS_DIR = ROOT / "agents"
STYLE_SRC = ROOT / "output-styles" / "fluent-korean.md"
CODEX_DIR = ROOT / "codex" / "agents"
OPENCODE_DIR = ROOT / "opencode" / "agents"
STYLE_OUT = ROOT / "instructions" / "fluent-korean.md"


class ParseError(Exception):
    pass


def split_frontmatter(text, source):
    lines = text.split("\n")
    if lines[0] != "---":
        raise ParseError(f"{source}: 첫 줄이 --- 가 아니다")
    try:
        end = lines.index("---", 1)
    except ValueError:
        raise ParseError(f"{source}: 앞머리를 닫는 --- 가 없다")
    meta = {}
    for line in lines[1:end]:
        key, sep, value = line.partition(": ")
        if not sep:
            raise ParseError(f"{source}: 한 줄 `키: 값` 형식이 아니다: {line!r}")
        meta[key.strip()] = value.strip()
    body = "\n".join(lines[end + 1:]).strip("\n") + "\n"
    return meta, body


def toml_basic(value):
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def toml_multiline(value):
    escaped = value.replace("\\", "\\\\").replace('"""', '""\\"')
    return '"""\n' + escaped + '"""'


def render_codex(name, description, body):
    return (
        f"name = {toml_basic(name)}\n"
        f"description = {toml_basic(description)}\n"
        f"developer_instructions = {toml_multiline(body)}\n"
    )


def render_opencode(description, body):
    return f"---\ndescription: {json.dumps(description, ensure_ascii=False)}\nmode: subagent\n---\n\n{body}"


def build():
    outputs = {}
    for src in sorted(AGENTS_DIR.glob("*.md")):
        meta, body = split_frontmatter(src.read_text(encoding="utf-8"), src.name)
        name, description = meta.get("name"), meta.get("description")
        if name != src.stem or not description:
            raise ParseError(f"{src.name}: name 이 파일 이름과 다르거나 description 이 없다")
        outputs[CODEX_DIR / f"{name}.toml"] = render_codex(name, description, body)
        outputs[OPENCODE_DIR / f"{name}.md"] = render_opencode(description, body)
    _, style_body = split_frontmatter(STYLE_SRC.read_text(encoding="utf-8"), STYLE_SRC.name)
    outputs[STYLE_OUT] = style_body
    return outputs


def stale_files(outputs):
    wanted = set(outputs)
    found = set()
    for directory in (CODEX_DIR, OPENCODE_DIR, STYLE_OUT.parent):
        found.update(p for p in directory.glob("*") if p.is_file())
    return sorted(found - wanted)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="쓰지 않고 최신 여부만 검사한다")
    args = parser.parse_args()
    outputs = build()
    drift = [p for p, text in outputs.items() if not p.is_file() or p.read_bytes() != text.encode("utf-8")]
    drift += stale_files(outputs)
    if args.check:
        for path in drift:
            print(f"어긋남: {path.relative_to(ROOT)}", file=sys.stderr)
        print("생성 파일 최신" if not drift else f"{len(drift)}개가 원본과 다르다. tools/build_runtime_files.py 로 다시 만든다.")
        return 1 if drift else 0
    for path, text in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
    for path in stale_files(outputs):
        path.unlink()
    print(f"생성 {len(outputs)}개")
    return 0


if __name__ == "__main__":
    console.force_utf8_console()
    sys.exit(main())
