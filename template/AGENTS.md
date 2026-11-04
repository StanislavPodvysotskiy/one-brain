# One Brain — rules for every AI model

This is a shared knowledge vault (an Obsidian vault, plain Markdown). It holds the context of all
the user's projects: goals, current status, decisions and session history. Several AI models work
with it (Claude, Kimi, Qwen, and others). None of them remembers past conversations, so
**the memory is these files**. Your job: read the context before you start and write the outcome
when you finish.

Reply in the user's language. User profile: [[20_Knowledge/User Profile]].

## Layout

```
AGENTS.md                ← this file, rules for all models
00_Home.md               ← home page: projects and their status
00_Inbox/                ← raw notes and chat exports not yet sorted
10_Projects/<Project>/
    README.md            ← goal, context, constraints, stack (rarely changes)
    STATUS.md            ← done, in progress, next steps (the key file)
    DECISIONS.md         ← decision log: what was decided, why, what was rejected
    sessions/            ← one file per work session
    artifacts/           ← code, diagrams, documents of the project
20_Knowledge/            ← general knowledge not tied to one project
90_Templates/            ← note templates (use them for new files)
99_Archive/              ← finished and frozen projects
skills/one-brain/        ← the shared skill, installed into every tool
global/AGENTS.md         ← the global rule, installed into every tool
scripts/brain.py         ← helper: list, find, context, save-session, save-status, save-decisions, new-project
```

A project is linked to its code or document folders through the `repo:` field in its `README.md`
front matter (several paths separated by commas). Run `python3 scripts/brain.py find` inside such
a folder to get the project name, and `context` to get its context.

## Protocol

### 1. Session start

When the user names a project (or says "start a session on <project>"):

1. Read `10_Projects/<Project>/README.md`.
2. Read `STATUS.md` — the current state.
3. Read `DECISIONS.md` so you don't propose what was already considered and rejected.
4. Read the 2–3 latest files in `sessions/` (sorted by name = sorted by date).
5. Tell the user in 5–10 lines where the project stands and what the next step is.
   Point out contradictions or stale data if you see any.

`python3 scripts/brain.py context "<Project>"` prints all of the above in one go.

If no project is named, look at `00_Home.md` and ask which project to work on.
If the project doesn't exist yet, create it:
`python3 scripts/brain.py new-project "<Name>" --repo <code folder>`.

### 2. During the work

- A decision was made (an approach or technology chosen, an option rejected) — add it to
  `DECISIONS.md` right away using the template. Include the reason and the rejected alternatives.
- Put work results (code, documents, diagrams) into `artifacts/` or wherever the user says. If the
  work lives in a separate repository, record its path in `repo:` in `README.md`.

### 3. Session end

When the user says "close the session" (or "save progress", "write it to the brain"):

1. Create `sessions/YYYY-MM-DD_<model>_<short-topic>.md` from `90_Templates/Session.md`.
   `<model>` is your name in lower case: `claude`, `kimi`, `qwen`… The easiest way is
   `brain.py save-session`: it picks a free file name and adds the front matter.
2. Update `STATUS.md`: move finished items to "Done", update "In progress" and "Next steps", set
   `updated`, `model`, `next` and `status` in the front matter. Keep STATUS short (one screen): compress
   old "Done" items, the details are in the sessions.
3. If new decisions appeared, make sure they are in `DECISIONS.md`.
4. Update the project row in `00_Home.md` if the status or next step changed.
5. Show the user which files you changed.

Without file access (a web chat) — output Markdown blocks: the session summary, the new
`DECISIONS.md` entries if decisions were made (numbered after the last entry), and the new
STATUS.md. The user saves each of them with `scripts/save-session.sh`.

### 4. Importing projects from a model's history

A new model, or a model with chat history outside the vault, imports its projects following the
`one-brain` skill, section 4: run `brain.py list` first, enrich matching projects (a "history
import" session, never deleting anything), create the missing ones. A web chat without file access
gets the prompt from `scripts/import-prompt.sh <model>`; its answer goes to `00_Inbox/` and a
model with file access distributes it.

## What the user can say

The user asks in plain words, in any language. Treat these phrases and their synonyms as requests:

| Say | The model will |
|---|---|
| "Where did we stop?" | read the project and tell you its status and next step |
| "Close the session" | save the summary and new decisions, update STATUS |
| "Record a decision: …" | add an entry to `DECISIONS.md` |
| "Create a project X" | create the project and link it to the current folder |
| "What projects do I have?" | list the projects with their status and next step |
| "Import your projects into One Brain" | bring in what it knows from its chat history, without duplicates |

## Rules

- **Never delete or rewrite other entries** in `sessions/` and `DECISIONS.md` — only append.
  If a decision is revised, add a new entry linking to the old one and mark the old one
  `Status: superseded`.
- **No secrets**: passwords, tokens, API keys, card numbers never go here. No personal data of
  third parties (names, phone numbers of colleagues or clients) either — only anonymized.
- Write facts, not a retelling of the conversation. Another model reads the summary: it needs to
  know what was done, what failed and why, and what to do next.
- Dates are `YYYY-MM-DD`. Links between notes use Obsidian syntax `[[Note name]]`.
- Keep the front matter (the `---` block at the top of a file): `00_Home.md` is built from it.
- `status` in `STATUS.md` is one of three values, nothing else:
  `active` — the project is being worked on; `paused` — on hold, will be resumed;
  `done` — finished (the user may later move its folder to `99_Archive/`).
  `brain.py save-status` rejects any other value.
- Don't change the vault layout or this file unless the user asks.
