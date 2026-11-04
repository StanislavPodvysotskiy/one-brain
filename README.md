# One Brain

[Русская версия](README.ru.md)

**Shared project memory for all your AI assistants — plain Markdown files you own.**

You use Claude, Kimi, Qwen, a local model, a web chat. Each one keeps its own history, and each
time you switch, the context is gone: what was done, what was decided, what's next. Lose access to
a provider and the history goes with it.

One Brain moves that memory out of the models and into an Obsidian vault on your disk. Every model
reads the project's state before it starts and writes the outcome when it finishes. Switch models
mid-task, or connect a new one, and it picks up where the last one stopped.

```
 Claude Code ─┐                                   ┌─ 10_Projects/Weather Bot/
 Kimi CLI ────┤  global rule: "use One Brain"     │    README.md     goal, context, stack
 Hermes+Qwen ─┼─ skill: how to read & write  ───► │    STATUS.md     done / in progress / next
 Codex, … ────┤  brain.py: one-command helper     │    DECISIONS.md  what was decided and why
 web chats ───┘  (copy/paste scripts)             │    sessions/     one summary per session
                                                  └─ 00_Home.md      all projects at a glance
```

- **No lock-in.** Markdown files and the [AGENTS.md](https://agents.md) convention. No MCP server,
  no database, no cloud. If a model disappears tomorrow, your memory stays.
- **Several models, one memory.** A handoff protocol tested across Claude Code, Kimi Code CLI and
  a local Qwen 3.5 9B (via Hermes Agent): each one found the project from an unrelated folder and
  summarized its state correctly.
- **Works with small local models.** `brain.py context` gives the whole project context in one
  command; `brain.py save-session` picks the file name and front matter. A 9B model doesn't have
  to follow a multi-step protocol.
- **Projects are found by folder.** Link a project to its code folders once (`repo:` field); a
  model working in that folder finds the project by itself.
- **Bring your history.** A prompt that makes any model export what it knows about your projects
  from its chat history — merged into existing cards, not duplicated.
- **Append-only and versioned.** Sessions and decisions are only appended; the vault is a Git
  repository, so any note a model breaks can be restored.

## Quick start

Requirements: Python 3.8+ (standard library only), Git (recommended), Obsidian (optional — it's
just Markdown). Tested on macOS; Linux should work; on Windows use WSL.

```bash
git clone https://github.com/StanislavPodvysotskiy/one-brain.git
cd one-brain
python3 install.py ~/OneBrain
```

This creates the vault in `~/OneBrain` (with a sample project) and connects the AI tools found on
your machine — see [What the installer changes](#what-the-installer-changes).

Then:

1. Open `~/OneBrain` in Obsidian as a vault. Recommended community plugins: **Git**
   by Vinzent (auto-commit) and **Dataview** (the summary tables on the home page).
2. Fill in `20_Knowledge/User Profile.md` — who you are and how you like to work.
3. Ask any connected model: *"What projects do I have in One Brain?"*

> **Keep your vault private.** This repository is the tool; your vault is your data. Don't push
> the vault to a public repository.

## Daily use

| You want to… | Do this |
|---|---|
| Start working on a project | Just start in its folder, or say *"let's continue the Weather Bot project"*. The model reads README, STATUS, DECISIONS and the latest sessions and tells you where things stand. |
| Save what was done | Say *"close the session"* (or *"save progress"*, in any language). The model writes a session summary and updates STATUS. |
| Add a project | `python3 ~/OneBrain/scripts/brain.py new-project "Name" --repo ~/code/name` — or ask a model to do it. Several folders: `--repo "~/code/app, ~/docs/app"`. |
| Use a web chat (no file access) | `~/OneBrain/scripts/context-pack.sh "Name"` copies the context to the clipboard; paste it into the chat. At the end copy the model's summary and run `scripts/save-session.sh "Name" kimi "topic"`. If the chat made decisions, copy them and run `scripts/save-session.sh "Name" decisions`. Then copy the new STATUS and run `scripts/save-session.sh "Name" status`. |
| Import a model's chat history | `~/OneBrain/scripts/import-prompt.sh kimi` copies a prompt listing the projects you already have. Paste it into that model's chat, save the answer to `00_Inbox/`, then ask a model with file access: *"distribute 00_Inbox/<file> across One Brain projects"*. |

The full protocol the models follow is in [`template/AGENTS.md`](template/AGENTS.md); the
condensed version they load as a skill is [`skills/one-brain/SKILL.md`](skills/one-brain/SKILL.md).

### `brain.py` commands

```
list                                   projects, status and next step
find [FOLDER]                          which project a folder belongs to
context [PROJECT|FOLDER] [-n N] [--web] README + STATUS + DECISIONS + latest N sessions
save-session PROJECT MODEL TOPIC       session summary from stdin into sessions/
save-status PROJECT                    replace STATUS.md with stdin (history stays in Git)
save-decisions PROJECT                 new DECISIONS.md entries from stdin, put on top
new-project PROJECT [--repo FOLDERS]   project from templates + a row on the home page
import-prompt [--model NAME]           web-chat prompt to export a model's projects
```

## Supported tools

Three layers make a model use the vault anywhere, not only inside it: a short **global rule**
loaded into every conversation, the **`one-brain` skill** with the procedure, and **`brain.py`**
doing the mechanical work.

| Tool | Global rule | Skill | Status |
|---|---|---|---|
| Claude Code | `~/.claude/CLAUDE.md` | `~/.claude/skills/one-brain` | tested |
| Kimi Code CLI | `~/.agents/AGENTS.md` | `~/.agents/skills/one-brain` | tested |
| Hermes Agent (any model, e.g. local Qwen) | `~/.hermes/SOUL.md` | `~/.agents/skills` via `skills.external_dirs` | tested with Qwen 3.5 9B |
| Codex CLI | `~/.codex/AGENTS.md` | — (rule only) | configured, untested |
| Gemini CLI | `~/.gemini/GEMINI.md` | — (rule only) | configured, untested |
| Qwen Code | `~/.qwen/QWEN.md` | — (rule only) | configured, untested |
| Any web chat | clipboard scripts | — | works with any model |

Inside the vault, `CLAUDE.md`, `QWEN.md` and `GEMINI.md` just import `AGENTS.md`, so the rules
live in one file. A tool that reads `AGENTS.md` needs nothing else. A tool not in the list: point
its global instructions to `~/OneBrain/global/AGENTS.md`.

## What the installer changes

Outside the vault, only for tools it finds:

- appends a block between `<!-- one-brain:start -->` and `<!-- one-brain:end -->` to the global
  instruction files in the table above (your own content in those files is kept);
- copies the skill to `~/.agents/skills/one-brain` and `~/.claude/skills/one-brain`;
- adds `~/.agents/skills` to `skills.external_dirs` in `~/.hermes/config.yaml`.

Every existing file is backed up once as `<file>.one-brain-backup`. Symlinked paths and skills it
didn't install are left alone and reported. Running the installer again is safe: it updates the
block and the skill copies instead of duplicating them.

**Update:** `git pull && python3 install.py ~/OneBrain`. In an existing vault this refreshes only
the files One Brain manages — `scripts/`, `skills/one-brain/`, `global/AGENTS.md` — and never
touches your notes.

**Uninstall:** `python3 install.py --uninstall` removes the blocks, the skill copies and the
Hermes entry. The vault is never deleted.

## Vault layout

```
AGENTS.md            rules for every model (edit them to taste)
00_Home.md           all projects: status and next step
00_Inbox/            raw notes and chat exports to sort
10_Projects/<Name>/  README.md, STATUS.md, DECISIONS.md, sessions/, artifacts/
20_Knowledge/        knowledge not tied to one project, your profile
90_Templates/        templates for project files, sessions and history imports
99_Archive/          finished projects
skills/, global/, scripts/   managed by the installer
```

A project's `status` (in the `STATUS.md` front matter) is one of `active`, `paused` or `done`.
`save-status` refuses any other value, so the summary on the home page stays consistent.

The sample project `10_Projects/Example - Weather Bot` shows a filled-in card with sessions from
two different models. Delete it (and its row in `00_Home.md`) when you no longer need it.

## Design choices

- **Files, not a server.** Every agent can read and write files; not every agent speaks MCP, and a
  server is one more thing to keep running. Obsidian gives a UI for free.
- **One source of rules.** Rules live in `AGENTS.md`; tool-specific files only point to it, so they
  don't drift apart.
- **The helper does the mechanics.** Small models are fine at summarizing and bad at multi-step
  bookkeeping, so finding the project, naming files and adding front matter is code, not prompt.
- **STATUS is short, sessions are long.** STATUS fits on one screen and is rewritten; sessions and
  decisions are append-only history.

## Limitations

- Models follow the rules most of the time, not always. If a model didn't save, say
  *"close the session"*.
- Small local models are slow: Qwen 3.5 9B took about 3.5 minutes to answer "where did we stop".
- Two models writing the same project at the same time can overwrite each other's STATUS. Work on a
  project with one model at a time; Git keeps the history either way.
- It's memory, not search: there is no RAG or embeddings. For a large knowledge base, look at
  [Karpathy's LLM Wiki pattern](https://gist.github.com/karpathy) instead — or alongside.

## Related ideas

- [AGENTS.md](https://agents.md) — the shared instructions file this builds on.
- Cline's *Memory Bank* — per-project memory files for one agent.
- [basic-memory](https://github.com/basicmachines-co/basic-memory) — Markdown memory over MCP.

## License

[MIT](LICENSE)
