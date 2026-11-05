"""im-korean 설치기. Claude Code, Codex CLI, OpenCode 에 스킬·에이전트·(선택) 출력 스타일을 복사한다.

사용법:
    python install.py                       # 설정 폴더가 있는 런타임을 찾아 설치
    python install.py --codex --opencode    # 런타임을 직접 고른다
    python install.py --style               # 늘 켜 둘 한국어 문체 지침도 설치
    python install.py --dry-run             # 할 일을 찍기만 하고 아무것도 바꾸지 않는다
    python install.py --uninstall           # 이 설치기가 넣은 것만 지운다
    python install.py --home DIR            # 홈 폴더를 바꾼다(시험용)

설치한 경로는 ~/.im-korean-install.json 에 적는다. 다시 돌리면 그 경로만 덮어쓴다.
목표 자리에 이 설치기가 넣지 않은 파일이 있으면 <경로>.bak-<시각> 으로 옮겨 둔다.
Python 3.8 이상, 표준 라이브러리만 쓴다.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST_NAME = ".im-korean-install.json"
BLOCK_START = "<!-- im-korean:fluent-korean:start -->"
BLOCK_END = "<!-- im-korean:fluent-korean:end -->"
STYLE_NAME = "fluent-korean.md"
IGNORED = shutil.ignore_patterns("__pycache__", "*.pyc")


class Installer:
    def __init__(self, home, codex_home, opencode_home, dry_run):
        self.home = home
        self.codex_home = codex_home
        self.opencode_home = opencode_home
        self.dry_run = dry_run
        self.manifest_path = home / MANIFEST_NAME
        self.entries = self._load_manifest()
        self.stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.done = set()

    def _load_manifest(self):
        if not self.manifest_path.is_file():
            return {"paths": [], "blocks": []}
        return json.loads(self.manifest_path.read_text(encoding="utf-8"))

    def save_manifest(self):
        if self.dry_run:
            return
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        text = json.dumps(self.entries, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        with open(self.manifest_path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)

    def say(self, message):
        print(("[dry-run] " if self.dry_run else "") + message)

    def owned(self, target):
        return str(target) in self.entries["paths"]

    def remember(self, target):
        if str(target) not in self.entries["paths"]:
            self.entries["paths"].append(str(target))

    def clear_target(self, target):
        if not (target.exists() or target.is_symlink()):
            return
        if self.owned(target):
            self.say(f"덮어쓰기: {target}")
            if not self.dry_run:
                remove_path(target)
            return
        backup = backup_name(target, self.stamp)
        self.say(f"백업: {target} -> {backup}")
        if not self.dry_run:
            target.rename(backup)

    def copy_dir(self, source, target):
        if target in self.done:
            return
        self.done.add(target)
        self.clear_target(target)
        self.say(f"복사: {source.relative_to(ROOT)} -> {target}")
        if not self.dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(source, target, ignore=IGNORED)
        self.remember(target)

    def copy_file(self, source, target):
        if target in self.done:
            return
        self.done.add(target)
        self.clear_target(target)
        self.say(f"복사: {source.relative_to(ROOT)} -> {target}")
        if not self.dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        self.remember(target)

    def put_block(self, target, body):
        self.say(f"지침 블록 넣기: {target}")
        if not self.dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            existing = target.read_text(encoding="utf-8") if target.is_file() else ""
            write_text(target, with_block(existing, body))
        if str(target) not in self.entries["blocks"]:
            self.entries["blocks"].append(str(target))

    def uninstall(self):
        if not self.entries["paths"] and not self.entries["blocks"]:
            self.say("지울 것이 없다. 설치 기록이 비어 있다.")
            return
        for name in self.entries["paths"]:
            target = Path(name)
            if target.exists() or target.is_symlink():
                self.say(f"삭제: {target}")
                if not self.dry_run:
                    remove_path(target)
                    prune_empty_parent(target)
        for name in self.entries["blocks"]:
            self.remove_block(Path(name))
        if not self.dry_run and self.manifest_path.is_file():
            self.manifest_path.unlink()
        self.say(f"설치 기록 삭제: {self.manifest_path}")

    def remove_block(self, target):
        if not target.is_file():
            return
        self.say(f"지침 블록 빼기: {target}")
        if self.dry_run:
            return
        rest = without_block(target.read_text(encoding="utf-8"))
        if rest.strip():
            write_text(target, rest)
        else:
            target.unlink()

    def home_relative(self, path):
        try:
            return "~/" + path.relative_to(self.home).as_posix()
        except ValueError:
            return path.as_posix()

    def install_runtime(self, name, with_style):
        {"claude": self.install_claude, "codex": self.install_codex, "opencode": self.install_opencode}[name](with_style)

    def install_skills(self, destination):
        for source in sorted((ROOT / "skills").iterdir()):
            if source.is_dir():
                self.copy_dir(source, destination / source.name)

    def install_claude(self, with_style):
        base = self.home / ".claude"
        self.install_skills(base / "skills")
        for source in sorted((ROOT / "agents").glob("*.md")):
            self.copy_file(source, base / "agents" / source.name)
        if with_style:
            self.copy_file(ROOT / "output-styles" / STYLE_NAME, base / "output-styles" / STYLE_NAME)
            self.say('출력 스타일을 켜려면 Claude Code 에서 /config 로 fluent-korean 을 고르거나 settings.json 에 "outputStyle": "fluent-korean" 을 적는다. 이 설치기는 settings.json 을 건드리지 않는다.')

    def install_codex(self, with_style):
        self.install_skills(self.home / ".agents" / "skills")
        for source in sorted((ROOT / "codex" / "agents").glob("*.toml")):
            self.copy_file(source, self.codex_home / "agents" / source.name)
        if with_style:
            body = (ROOT / "instructions" / STYLE_NAME).read_text(encoding="utf-8")
            self.put_block(self.codex_home / "AGENTS.md", body)

    def install_opencode(self, with_style):
        self.install_skills(self.home / ".agents" / "skills")
        for source in sorted((ROOT / "opencode" / "agents").glob("*.md")):
            self.copy_file(source, self.opencode_home / "agents" / source.name)
        if with_style:
            target = self.opencode_home / "im-korean" / STYLE_NAME
            self.copy_file(ROOT / "instructions" / STYLE_NAME, target)
            self.say(f'opencode.json 의 "instructions" 배열에 {json.dumps(self.home_relative(target))} 를 더한다. 이 설치기는 opencode.json 을 건드리지 않는다.')


def remove_path(target):
    if target.is_dir() and not target.is_symlink():
        shutil.rmtree(target)
    else:
        target.unlink()


def prune_empty_parent(target):
    parent = target.parent
    if parent.name == "im-korean" and parent.is_dir() and not any(parent.iterdir()):
        parent.rmdir()


def backup_name(target, stamp):
    candidate = target.with_name(f"{target.name}.bak-{stamp}")
    counter = 1
    while candidate.exists():
        counter += 1
        candidate = target.with_name(f"{target.name}.bak-{stamp}-{counter}")
    return candidate


def write_text(target, text):
    with open(target, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


BLOCK_RE = re.compile(re.escape(BLOCK_START) + r".*?" + re.escape(BLOCK_END) + r"\n?", re.DOTALL)


def with_block(existing, body):
    block = f"{BLOCK_START}\n{body.strip()}\n{BLOCK_END}\n"
    if BLOCK_RE.search(existing):
        return BLOCK_RE.sub(lambda _: block, existing, count=1)
    if not existing.strip():
        return block
    return existing.rstrip("\n") + "\n\n" + block


def without_block(existing):
    rest = BLOCK_RE.sub("", existing, count=1)
    return rest.rstrip("\n") + "\n" if rest.strip() else ""


def resolve_homes(args):
    if args.home:
        home = Path(args.home).expanduser().resolve()
        return home, home / ".codex", home / ".config" / "opencode"
    home = Path.home()
    codex_home = Path(os.environ.get("CODEX_HOME") or home / ".codex")
    xdg = os.environ.get("XDG_CONFIG_HOME")
    opencode_home = Path(xdg) / "opencode" if xdg else home / ".config" / "opencode"
    return home, codex_home, opencode_home


def pick_runtimes(args, home, codex_home, opencode_home):
    chosen = [name for name in ("claude", "codex", "opencode") if getattr(args, name)]
    if chosen:
        return chosen
    found = {"claude": home / ".claude", "codex": codex_home, "opencode": opencode_home}
    return [name for name, path in found.items() if path.is_dir()]


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for name in ("claude", "codex", "opencode"):
        parser.add_argument(f"--{name}", action="store_true", help=f"{name} 에 설치")
    parser.add_argument("--style", action="store_true", help="늘 켜 둘 한국어 문체 지침도 설치")
    parser.add_argument("--dry-run", action="store_true", help="할 일을 찍기만 한다")
    parser.add_argument("--uninstall", action="store_true", help="이 설치기가 넣은 것을 지운다")
    parser.add_argument("--home", help="홈 폴더를 바꾼다(시험용)")
    return parser.parse_args()


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    args = parse_args()
    home, codex_home, opencode_home = resolve_homes(args)
    installer = Installer(home, codex_home, opencode_home, args.dry_run)
    if args.uninstall:
        installer.uninstall()
        return 0
    runtimes = pick_runtimes(args, home, codex_home, opencode_home)
    if not runtimes:
        print("설치할 런타임을 못 찾았다. --claude, --codex, --opencode 중에서 고른다.", file=sys.stderr)
        return 2
    installer.say("대상 런타임: " + ", ".join(runtimes))
    for name in runtimes:
        installer.install_runtime(name, args.style)
    installer.save_manifest()
    return 0


if __name__ == "__main__":
    sys.exit(main())
