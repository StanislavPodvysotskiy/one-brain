#!/usr/bin/env python3
"""Installs One Brain: creates (or updates) the vault and connects AI tools to it.

  python3 install.py [VAULT]          default vault: ~/OneBrain
  python3 install.py --vault-only     create/update the vault, don't touch tool configs
  python3 install.py --uninstall      disconnect the tools (the vault itself is never deleted)

What it changes outside the vault (each existing file is backed up once as *.one-brain-backup):
  - a marked block with the global rule in ~/.agents/AGENTS.md (Kimi Code CLI and other tools
    that read ~/.agents) and, when the tool is present, in ~/.claude/CLAUDE.md, ~/.codex/AGENTS.md,
    ~/.gemini/GEMINI.md, ~/.qwen/QWEN.md, ~/.hermes/SOUL.md;
  - a copy of the one-brain skill in ~/.agents/skills/ and ~/.claude/skills/;
  - ~/.agents/skills in skills.external_dirs of ~/.hermes/config.yaml.
Python 3 standard library only.
"""
import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
HOME = Path.home()
START, END = "<!-- one-brain:start -->", "<!-- one-brain:end -->"
SKILL = "one-brain"
SKILL_MARKER = ".installed-by-one-brain"
YAML_TAG = "# one-brain"
AGENTS_SKILLS = "~/.agents/skills"

# Global instruction files: (file, folder that must exist for the tool to count as installed)
GLOBAL_FILES = [
    (HOME / ".agents" / "AGENTS.md", None),  # always: Kimi Code CLI reads ~/.agents
    (HOME / ".claude" / "CLAUDE.md", HOME / ".claude"),
    (HOME / ".codex" / "AGENTS.md", HOME / ".codex"),
    (HOME / ".gemini" / "GEMINI.md", HOME / ".gemini"),
    (HOME / ".qwen" / "QWEN.md", HOME / ".qwen"),
    (HOME / ".hermes" / "SOUL.md", HOME / ".hermes"),
]
SKILL_DIRS = [
    (HOME / ".agents" / "skills", None),
    (HOME / ".claude" / "skills", HOME / ".claude"),
]
HERMES_CONFIG = HOME / ".hermes" / "config.yaml"


def say(msg):
    print(msg)


def tilde(path):
    path = Path(path)
    return "~/" + str(path.relative_to(HOME)) if path == HOME or HOME in path.parents else str(path)


def render(src, vault):
    return src.read_text(encoding="utf-8").replace("{{VAULT}}", str(vault))


def backup_once(path):
    b = path.with_name(path.name + ".one-brain-backup")
    if path.is_file() and not b.exists():
        shutil.copy2(path, b)


def has_symlink(path):
    """True if the path or any of its parents under HOME is a symlink — we don't write through those."""
    p = path
    while p != HOME and p != p.parent:
        if p.is_symlink():
            return True
        p = p.parent
    return False


# ---------- vault ----------

def setup_vault(vault):
    if vault.exists() and any(vault.iterdir()) and not (vault / "AGENTS.md").exists():
        sys.exit(f"{vault} exists, is not empty and is not a One Brain vault (no AGENTS.md). "
                 "Pick another folder.")
    fresh = not (vault / "AGENTS.md").exists()
    if fresh:
        shutil.copytree(REPO / "template", vault, dirs_exist_ok=True)
        say(f"Created the vault: {vault}")
    else:
        say(f"Updating the existing vault: {vault} (notes are not touched)")

    # Managed files: always refreshed from the repository
    shutil.copytree(REPO / "scripts", vault / "scripts", dirs_exist_ok=True)
    (vault / "skills" / SKILL).mkdir(parents=True, exist_ok=True)
    (vault / "skills" / SKILL / "SKILL.md").write_text(
        render(REPO / "skills" / SKILL / "SKILL.md", vault), encoding="utf-8")
    (vault / "global").mkdir(exist_ok=True)
    (vault / "global" / "AGENTS.md").write_text(render(REPO / "global" / "AGENTS.md", vault), encoding="utf-8")
    say("  scripts/, skills/one-brain/, global/AGENTS.md — up to date")

    if fresh and shutil.which("git") and not (vault / ".git").exists():
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=vault, check=True)
        subprocess.run(["git", "add", "-A"], cwd=vault, check=True)
        r = subprocess.run(["git", "commit", "-q", "-m", "One Brain vault"], cwd=vault,
                           capture_output=True, text=True)
        say("  Git repository initialized" + ("" if r.returncode == 0 else
            " (first commit skipped: set git user.name/user.email and commit yourself)"))


# ---------- tools ----------

BLOCK_RE = re.compile(re.escape(START) + r".*?" + re.escape(END) + r"\n?", re.S)


def upsert_block(path, text):
    block = f"{START}\n{text.rstrip()}\n{END}\n"
    if has_symlink(path):
        say(f"  skip {tilde(path)}: it is a symlink, add the rule from global/AGENTS.md yourself")
        return
    old = path.read_text(encoding="utf-8") if path.is_file() else ""
    new = BLOCK_RE.sub(lambda _: block, old, count=1) if START in old else \
        (old.rstrip() + "\n\n" + block if old.strip() else block)
    if new != old:
        backup_once(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(new, encoding="utf-8")
    say(f"  rule → {tilde(path)}")


def remove_block(path):
    if not path.is_file() or has_symlink(path):
        return
    old = path.read_text(encoding="utf-8")
    if START not in old:
        return
    new = BLOCK_RE.sub("", old).rstrip()
    if new:
        path.write_text(new + "\n", encoding="utf-8")
    else:
        path.unlink()
    say(f"  rule removed from {tilde(path)}")


def install_skill(skills_dir, vault):
    target = skills_dir / SKILL
    if has_symlink(target):
        say(f"  skip {tilde(target)}: it is (or is inside) a symlink")
        return
    if target.exists():
        if not (target / SKILL_MARKER).exists():
            say(f"  skip {tilde(target)}: a skill with this name already exists and wasn't installed by One Brain")
            return
        shutil.rmtree(target)
    shutil.copytree(vault / "skills" / SKILL, target)
    (target / SKILL_MARKER).write_text(f"Installed from {vault}. Re-run install.py to update.\n", encoding="utf-8")
    say(f"  skill → {tilde(target)}")


def remove_skill(skills_dir):
    target = skills_dir / SKILL
    if (target / SKILL_MARKER).exists() and not has_symlink(target):
        shutil.rmtree(target)
        say(f"  skill removed from {tilde(target)}")


def hermes_add_skills_dir():
    if not HERMES_CONFIG.is_file():
        return
    text = HERMES_CONFIG.read_text(encoding="utf-8")
    live = [l for l in text.splitlines() if not l.lstrip().startswith("#")]
    if any(AGENTS_SKILLS in l for l in live):
        say("  Hermes: ~/.agents/skills already in skills.external_dirs")
        return
    item = f"    - {AGENTS_SKILLS}  {YAML_TAG}"
    if re.search(r"^  external_dirs:[ \t]*$", text, re.M):
        new = re.sub(r"^(  external_dirs:[ \t]*)$", r"\1\n" + item, text, count=1, flags=re.M)
    elif any(re.match(r"\s*external_dirs:\s*\S", l) for l in live):
        say(f"  Hermes: add {AGENTS_SKILLS} to skills.external_dirs in {tilde(HERMES_CONFIG)} yourself")
        return
    elif re.search(r"^skills:[ \t]*$", text, re.M):
        new = re.sub(r"^(skills:[ \t]*)$", r"\1\n  external_dirs:  " + YAML_TAG + "\n" + item,
                     text, count=1, flags=re.M)
    else:
        new = text.rstrip() + f"\n\nskills:  {YAML_TAG}\n  external_dirs:  {YAML_TAG}\n{item}\n"
    backup_once(HERMES_CONFIG)
    HERMES_CONFIG.write_text(new, encoding="utf-8")
    say(f"  Hermes: {AGENTS_SKILLS} added to skills.external_dirs")


def hermes_remove_skills_dir():
    if not HERMES_CONFIG.is_file():
        return
    lines = HERMES_CONFIG.read_text(encoding="utf-8").splitlines(keepends=True)
    kept = [l for l in lines if not l.rstrip().endswith(YAML_TAG)]
    if len(kept) != len(lines):
        HERMES_CONFIG.write_text("".join(kept), encoding="utf-8")
        say("  Hermes: One Brain lines removed from config.yaml")


def present(folder):
    return folder is None or folder.is_dir()


def install_tools(vault):
    rule = (vault / "global" / "AGENTS.md").read_text(encoding="utf-8")
    say("Connecting tools:")
    for path, folder in GLOBAL_FILES:
        if present(folder):
            upsert_block(path, rule)
    for skills_dir, folder in SKILL_DIRS:
        if present(folder):
            install_skill(skills_dir, vault)
    hermes_add_skills_dir()


def uninstall_tools():
    say("Disconnecting tools (the vault is left as is):")
    for path, _ in GLOBAL_FILES:
        remove_block(path)
    for skills_dir, _ in SKILL_DIRS:
        remove_skill(skills_dir)
    hermes_remove_skills_dir()


def main():
    ap = argparse.ArgumentParser(description="Install One Brain")
    ap.add_argument("vault", nargs="?", default=str(HOME / "OneBrain"), help="vault folder (default ~/OneBrain)")
    ap.add_argument("--vault-only", action="store_true", help="don't touch tool configs")
    ap.add_argument("--uninstall", action="store_true", help="disconnect the tools; the vault is kept")
    a = ap.parse_args()
    if a.uninstall:
        uninstall_tools()
        return
    vault = Path(a.vault).expanduser().resolve()
    setup_vault(vault)
    if not a.vault_only:
        install_tools(vault)
    say(f"\nDone. Open {vault} in Obsidian as a vault, then ask any connected model:\n"
        f'  "What projects do I have in One Brain?"')


if __name__ == "__main__":
    main()
