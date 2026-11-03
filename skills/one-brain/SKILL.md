---
name: one-brain
description: Shared project memory of the user in the "One Brain" Obsidian vault. Use it at the start of work on any project (code, document, research, any multi-step task) to learn what was already done, which decisions were made and what to do next; when an important decision is made; and at the end of a session when the user says "close the session", "save progress" or "write it to the brain" (in any language). Also when the user asks "what's the status of the project", "where did we stop", "what's next".
---

# One Brain — shared project memory

The user works with several AI models (Claude, Kimi, Qwen and others). None of them remembers past
conversations. The shared memory is Markdown files in the vault:

**`{{VAULT}}`**

Full vault rules: `{{VAULT}}/AGENTS.md`. Below is the short version, enough to work.

## The helper

Almost everything is a single command (Python 3, no dependencies). Quote the path:

```bash
B="{{VAULT}}/scripts/brain.py"
python3 "$B" list                                # all projects, status, next step
python3 "$B" find                                # which project the current folder belongs to
python3 "$B" context                             # context of the current folder's project
python3 "$B" context "Project name"              # context of a project by name
python3 "$B" save-session "Project name" qwen "topic" <<'EOF'
...summary text...
EOF
python3 "$B" save-status "Project name" <<'EOF'
...the whole new STATUS.md...
EOF
python3 "$B" new-project "Project name" --repo ~/code/folder
```

## 1. Starting work

1. Find the project: `python3 "$B" find` in the working folder. If none is found, run
   `python3 "$B" list` and ask the user which project this work belongs to. If it is a new
   project, offer to create it (`new-project`, with `--repo` if the code lives in its own folder).
2. Get the context: `python3 "$B" context "Project name"`. It contains README (goal), STATUS
   (where the project is now), DECISIONS (accepted and rejected decisions) and the latest sessions.
3. Tell the user in 5–10 lines where the project stands and what the next step is.
   Don't propose what DECISIONS already rejected unless the user brings it up again.

One-off questions without a project (a lookup, a translation, a single command) need no memory —
don't spend time on them.

## 2. During the work

An important decision was made (an approach or technology chosen, an option rejected) — add an
entry at the top of the list in `10_Projects/<Project>/DECISIONS.md` following the sample in that
file: what was decided, why, what was rejected. Never delete old entries.

## 3. Ending the session

When the user says "close the session", "save progress", "write it to the brain" — or when you
reached a noticeable milestone and the user is about to finish — offer to save the outcome, and
after they agree:

1. **Session summary** — `save-session` with the text on stdin. `MODEL` is your name in lower case
   (`claude`, `kimi`, `qwen`…), the topic is 2–5 words. Sections of the text:

   ```markdown
   # Session YYYY-MM-DD: topic
   ## Goal of the session
   ## Done
   ## What failed and why
   ## Decisions made
   ## Changed files and artifacts
   ## Next steps
   ## Notes for the next model
   ```

2. **STATUS.md** — read the current `10_Projects/<Project>/STATUS.md` and write the whole updated
   file with `save-status`. Keep the `---…---` front matter and update `updated` (today), `model`
   (you) and `next` (the main next step in one phrase). `status` is one of `active` (in work),
   `paused` (on hold) or `done` (finished); `save-status` rejects anything else. Keep "Done" short.
3. If the status or next step changed, update the project row in the table in
   `{{VAULT}}/00_Home.md`.
4. Tell the user which files changed.

Write facts, not a retelling of the conversation: another model reads the summary and needs to
know what was done, what failed and why, and what to do next.

## 4. Importing projects from your own history

When the user asks "import your projects into One Brain" (a new model is joining, or a model has
chat history outside the vault). Some projects are already there — don't create duplicates.

1. `python3 "$B" list` — which projects exist and which folders they are linked to.
2. For each project from your history, find its match in the vault:
   - it has a working folder — `python3 "$B" find "<folder>"`;
   - no folder — compare by meaning with the names and goals from `list` (the same topic under a
     different name is the same project). If unsure, ask the user; don't create.
3. **The project exists:**
   - read its `context` and record only what's missing as a session with the topic
     "history import" (`save-session … <model> "history import"`): what you did, results,
     decisions, where you stopped, dates if possible;
   - append new decisions to `DECISIONS.md`;
   - in `STATUS.md` add the new items to "Done" and "Next steps" without deleting anything. If your
     data contradicts the card, don't pick a side — record the discrepancy under
     "Open questions and blockers".
4. **The project doesn't exist:** `new-project "Name" --repo <folder>` (no `--repo` if there is no
   folder), fill in README and STATUS, save a "history import" session.
5. At the end show a table: project → "enriched" / "created" / "skipped (why)".

Without file access (a web chat) — output everything as one Markdown document following
`90_Templates/History import.md`; the user puts it into `00_Inbox/`, and a model with file access
distributes it by the same rules.

## Never

- No secrets (passwords, tokens, API keys) and no personal data of third parties
  (names, phone numbers) — only anonymized.
- Don't delete or rewrite other entries in `sessions/` and `DECISIONS.md`.
- Don't change the vault layout, `AGENTS.md` or this skill unless the user asks.
