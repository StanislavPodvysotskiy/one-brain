#!/usr/bin/env python3
"""One Brain vault helper. Python 3 standard library only.

Built mainly for models: find a project and get its context in one call, save a session summary
with the right file name and front matter in one call. Especially useful for small local models
that struggle to follow a multi-step protocol.

Commands:
  brain.py list                                   projects, status and next step
  brain.py find [FOLDER]                          which project a folder belongs to (by the repo: field)
  brain.py context [PROJECT|FOLDER] [-n N] [--web] project context: README, STATUS, DECISIONS, N sessions
  brain.py save-session PROJECT MODEL TOPIC       session summary from stdin (or an empty template) into sessions/
  brain.py save-status PROJECT                    STATUS.md from stdin (the old version stays in Git)
  brain.py new-project PROJECT [--repo FOLDER]    project folder from templates + a row in 00_Home.md
  brain.py import-prompt [--model NAME]           web-chat prompt: export your projects without duplicates
"""
import argparse
import datetime
import os
import re
import sys
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
PROJECTS = VAULT / "10_Projects"
TEMPLATES = VAULT / "90_Templates"
HOME_NOTE = VAULT / "00_Home.md"
PROFILE = VAULT / "20_Knowledge" / "User Profile.md"
HOME_MARKER = "\n<!-- Models: update your project's row"

WEB_HEADER = """# Context of the project "{name}" from the One Brain vault

You are continuing work on this project. Below are the vault rules, the user profile and the
current state of the project. You have no file access, so:
1. First, tell the user in 5–10 lines where the project stands and what the next step is.
2. When the user says "close the session", output TWO Markdown blocks:
   the session summary following the "Session" template and the whole updated STATUS.md.
"""

IMPORT_HEADER = """# Import your projects into the One Brain shared memory

I (the user) keep the shared memory of my projects in a vault called One Brain. Several AI models
work with it. Transfer everything you know about my projects from our history into it.

Some projects are already there (list below) — don't create duplicates:
- if your project matches one from the list (by working folder or by meaning, even under a
  different name), give its name from the list and write only what its description lacks;
- if there is no match, mark it NEW;
- if unsure, mark it NOT SURE and explain what it might match.

Write facts, not a retelling of conversations: what was done, which decisions were made and why,
where we stopped, what's next. Dates if you remember them. No passwords, tokens or personal data
(names, phone numbers, client names). If you know little about a project, say so; don't make it up.

Output ONE Markdown document strictly following the template at the end (one "Project" block per
project). Model: {model}.
"""


def fail(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)


def frontmatter(path):
    """Minimal YAML front matter parser: only `key: value` lines."""
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {}
    m = re.match(r"---\n(.*?)\n---", text, re.S)
    if not m:
        return {}
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith((" ", "-", "#")):
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip().strip("\"'")
    return meta


def projects():
    return sorted(p for p in PROJECTS.iterdir() if p.is_dir()) if PROJECTS.is_dir() else []


def project_dir(name):
    d = PROJECTS / name
    if not d.is_dir():
        known = ", ".join(p.name for p in projects()) or "none"
        fail(f'No project "{name}". Existing: {known}')
    return d


def resolve(path):
    return Path(os.path.expanduser(path)).resolve()


def find_project(folder):
    """The project whose repo: contains the folder (longest match wins), or the folder is inside a project."""
    folder = resolve(folder)
    try:
        rel = folder.relative_to(PROJECTS)
        if rel.parts:
            return rel.parts[0]
    except ValueError:
        pass
    best, best_len = None, -1
    for p in projects():
        # repo: may list several paths separated by commas
        for repo in filter(None, (r.strip() for r in frontmatter(p / "README.md").get("repo", "").split(","))):
            r = resolve(repo)
            if (folder == r or r in folder.parents) and len(r.parts) > best_len:
                best, best_len = p.name, len(r.parts)
    return best


def sessions(d):
    s = d / "sessions"
    # File names start with the date, so sorting by name is sorting by time
    return sorted(s.glob("*.md")) if s.is_dir() else []


def slug(text):
    text = re.sub(r"[\\/:*?\"<>|#^\[\]]", "", text.lower())
    return re.sub(r"\s+", "-", text).strip("-") or "session"


def fill(template, name, today):
    return (TEMPLATES / template).read_text(encoding="utf-8") \
        .replace("{{project}}", name).replace("{{date}}", today)


def read_stdin():
    if sys.stdin.isatty():
        return ""
    text = sys.stdin.read().strip("\n")
    # Models often wrap the summary in ```markdown … ``` — strip it
    lines = text.splitlines()
    if lines and lines[0].startswith("```") and lines[-1].strip() == "```":
        text = "\n".join(lines[1:-1])
    return text.strip("\n")


def project_goal(d):
    """The "Goal" paragraph of README — used to match projects by meaning."""
    text = (d / "README.md").read_text(encoding="utf-8") if (d / "README.md").is_file() else ""
    m = re.search(r"^## Goal\n+(?!<!--)((?:.+\n?)+)", text, re.M)
    return " ".join(m.group(1).split()) if m else ""


def cmd_list(_):
    for p in projects():
        st = frontmatter(p / "STATUS.md")
        repo = frontmatter(p / "README.md").get("repo", "")
        print(f"- {p.name} [{st.get('status', '?')}, updated {st.get('updated', '?')}]"
              + (f" repo: {repo}" if repo else ""))
        if st.get("next"):
            print(f"    next: {st['next']}")


def cmd_find(a):
    name = find_project(a.folder or os.getcwd())
    if not name:
        fail("No project found for this folder. Run `brain.py list` or ask the user.")
    print(name)


def cmd_context(a):
    target = a.target or os.getcwd()
    # An absolute path would swallow PROJECTS when joined, so a project name never contains "/"
    is_name = "/" not in target and (PROJECTS / target).is_dir()
    name = target if is_name else find_project(target)
    if not name:
        fail(f'Can\'t tell which project "{target}" is. Run `brain.py list`.')
    d = project_dir(name)
    out = []
    if a.web:
        out.append(WEB_HEADER.format(name=name))
        out.append(("RULES (AGENTS.md)", VAULT / "AGENTS.md"))
        out.append(("USER PROFILE", PROFILE))
    else:
        out.append(f'# Project "{name}" — {d}\n')
    for f in ("README.md", "STATUS.md", "DECISIONS.md"):
        out.append((f, d / f))
    for s in sessions(d)[-a.n:]:
        out.append((f"SESSION {s.name}", s))
    if a.web:
        out.append(("SESSION SUMMARY TEMPLATE", TEMPLATES / "Session.md"))
    for item in out:
        if isinstance(item, str):
            print(item)
        elif item[1].is_file():
            print(f"\n=============== {item[0]} ===============\n")
            print(item[1].read_text(encoding="utf-8").rstrip("\n"))


def cmd_save_session(a):
    d = project_dir(a.project)
    today = datetime.date.today().isoformat()
    model = a.model.lower()
    # Quoted: a colon in the topic would break the YAML front matter
    topic = '"' + a.topic.replace('"', "'") + '"'
    body = read_stdin()
    if not body:
        body = fill("Session.md", a.project, today).replace("model: \n", f"model: {model}\n") \
            .replace("topic: \n", f"topic: {topic}\n").replace("<topic>", a.topic)
    elif not body.startswith("---\n"):
        # Front matter feeds the summary on the home page (Dataview)
        body = (f"---\nproject: {a.project}\ntype: session\ndate: {today}\n"
                f"model: {model}\ntopic: {topic}\n---\n\n{body}")
    (d / "sessions").mkdir(exist_ok=True)
    base = d / "sessions" / f"{today}_{model}_{slug(a.topic)}"
    path, i = base.with_suffix(".md"), 2
    while path.exists():
        path, i = Path(f"{base}-{i}.md"), i + 1
    path.write_text(body.rstrip("\n") + "\n", encoding="utf-8")
    print(path.relative_to(VAULT))


def cmd_save_status(a):
    d = project_dir(a.project)
    body = read_stdin()
    if not body:
        fail("Pass the new STATUS.md on stdin.")
    (d / "STATUS.md").write_text(body.rstrip("\n") + "\n", encoding="utf-8")
    print((d / "STATUS.md").relative_to(VAULT))


def cmd_new_project(a):
    d = PROJECTS / a.project
    if d.exists():
        fail(f"The project already exists: {d}")
    today = datetime.date.today().isoformat()
    (d / "sessions").mkdir(parents=True)
    (d / "artifacts").mkdir()
    (d / "artifacts" / ".gitkeep").touch()
    for f in ("README.md", "STATUS.md", "DECISIONS.md"):
        text = fill(f, a.project, today)
        if f == "README.md" and a.repo:
            text = text.replace("repo: \n", f"repo: {a.repo}\n", 1)
        (d / f).write_text(text, encoding="utf-8")
    row = f"| [[10_Projects/{a.project}/STATUS\\|{a.project}]] | active | Fill in README and STATUS |\n"
    home = HOME_NOTE.read_text(encoding="utf-8")
    home = home.replace(HOME_MARKER, row + HOME_MARKER, 1) if HOME_MARKER in home else home + row
    HOME_NOTE.write_text(home, encoding="utf-8")
    print(f"Created project: {d.relative_to(VAULT)}")
    print("Next: fill in README.md (goal, context) and STATUS.md (next steps).")


def cmd_import_prompt(a):
    print(IMPORT_HEADER.format(model=a.model))
    print("=============== PROJECTS ALREADY IN ONE BRAIN ===============\n")
    for p in projects():
        repo = frontmatter(p / "README.md").get("repo", "")
        goal = project_goal(p)
        print(f"- **{p.name}**" + (f" — folders: {repo}" if repo else "") + (f"\n  {goal}" if goal else ""))
    print("\n=============== ANSWER TEMPLATE ===============\n")
    print((TEMPLATES / "History import.md").read_text(encoding="utf-8")
          .replace("{{date}}", datetime.date.today().isoformat())
          .replace("model: \n", f"model: {a.model}\n").replace("<model>", a.model).rstrip("\n"))


def main():
    ap = argparse.ArgumentParser(description="One Brain vault helper")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list").set_defaults(func=cmd_list)
    p = sub.add_parser("find")
    p.add_argument("folder", nargs="?")
    p.set_defaults(func=cmd_find)
    p = sub.add_parser("context")
    p.add_argument("target", nargs="?", help="project name or folder (default: current folder)")
    p.add_argument("-n", type=int, default=3, help="how many latest sessions (default 3)")
    p.add_argument("--web", action="store_true", help="pack for a web chat: with rules and profile")
    p.set_defaults(func=cmd_context)
    p = sub.add_parser("save-session")
    p.add_argument("project")
    p.add_argument("model")
    p.add_argument("topic")
    p.set_defaults(func=cmd_save_session)
    p = sub.add_parser("save-status")
    p.add_argument("project")
    p.set_defaults(func=cmd_save_status)
    p = sub.add_parser("new-project")
    p.add_argument("project")
    p.add_argument("--repo", help="folder(s) of the project's code, comma-separated, if outside the vault")
    p.set_defaults(func=cmd_new_project)
    p = sub.add_parser("import-prompt")
    p.add_argument("--model", default="<your name: kimi, qwen…>", help="model name for the export header")
    p.set_defaults(func=cmd_import_prompt)
    a = ap.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
