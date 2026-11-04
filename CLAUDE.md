# CLAUDE.md

Notes for developing One Brain itself (the tool, not a user's vault).

## Layout

- `template/` — the vault skeleton copied on first install (rules `AGENTS.md`, note templates,
  home page, sample project). User data starts here, so the installer never overwrites it later.
- `skills/one-brain/SKILL.md`, `global/AGENTS.md` — contain `{{VAULT}}`; the installer renders the
  real vault path into them. These, plus `scripts/`, are the *managed* files refreshed on every
  install.
- `scripts/brain.py` — all the logic models call. Python standard library only, keep it that way.
  The wrappers (`*.sh`) only add the clipboard; `clipboard.sh` is sourced, not executed.
- `install.py` — install / update / `--uninstall`. Uses `Path.home()`, so it can be tested
  against a fake `HOME`.

## Keep in sync

A change in one of these usually needs the others: `brain.py` commands ↔ `SKILL.md` (helper and
sections) ↔ `template/AGENTS.md` (protocol) ↔ `README.md` (commands, tools table). Template
section headings (`## Goal`) are parsed by `brain.py` (`project_goal`) — rename both together.
The allowed `status` values live in `brain.py` (`STATUSES`, checked by `save-status`) and are
listed in `template/AGENTS.md`, `SKILL.md` and `README.md` — change all four together.
The table of phrases for the user lives in `template/AGENTS.md` and is copied to `README.md`,
`README.ru.md` and `template/00_Home.md`; the skill description lists the same triggers.
`README.ru.md` is the Russian translation of `README.md`: change them together.
Every change updates the READMEs and this file in the same commit.

## Testing

Never test the installer against the real home directory:

```bash
T=$(mktemp -d); mkdir -p "$T/home/.claude" "$T/home/.hermes"
HOME="$T/home" python3 install.py "$T/home/OneBrain"     # install, then run it again: no duplicates
HOME="$T/home" python3 "$T/home/OneBrain/scripts/brain.py" list
HOME="$T/home" python3 install.py --uninstall            # files back to their original content
```

Check: blocks appear once, user content around them survives, backups are made once, symlinked
targets are skipped, the Hermes config is restored byte for byte after uninstall.

## Gotchas

- macOS `pbcopy`/`pbpaste` without a UTF-8 locale (empty `LANG`, typical for non-login shells) use
  a legacy encoding and garble non-ASCII text in the clipboard — hence `LANG=en_US.UTF-8` in
  `clipboard.sh`. Verify with `osascript -e 'the clipboard as «class utf8»'`: `pbpaste` is wrong
  in the same way, so a pbcopy→pbpaste round trip hides the bug.
- In zsh `$CMD args` is not word-split; call `python3 "$B" …` or use a function.
- Skills are copied, not symlinked: some tools skip symlinked skill folders when scanning.
- The Obsidian plugin for auto-commits is listed in the catalog as **Git** (id `obsidian-git`, by
  Vinzent), not "Obsidian Git" — searching for the old name in Obsidian may not find it.
- A project name never contains `/`: `context` treats a value with `/` as a folder path.
- `save-decisions` inserts entries right after the `# ` title and its `> ` note (`decisions_top`),
  so a DECISIONS.md template must keep that shape. It ignores HTML comments when checking numbers:
  the entry template inside `<!-- -->` contains `## D-001.` and is not a real entry.
- A web chat can't write files, so every file it changes needs its own clipboard step in
  `save-session.sh` (summary, decisions, status) — otherwise its decisions live only in the summary.
