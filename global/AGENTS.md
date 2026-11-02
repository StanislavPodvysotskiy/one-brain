## One Brain — shared project memory

The user keeps the shared memory of all their projects in an Obsidian vault: `{{VAULT}}`.
You don't remember past conversations, and other models may already have worked on the same
project. So:

- **When you start working on a project** (code, a document, any multi-step task), use the
  `one-brain` skill: find the project and read its status, decisions and latest sessions.
  Quick way: `python3 "{{VAULT}}/scripts/brain.py" context` in the working folder.
- **When the user says "close the session"**, "save progress" or "write it to the brain"
  (in any language), save the session summary and update the project STATUS following the
  `one-brain` skill. If a noticeable step is done and the user is wrapping up, offer it yourself.
- If the skill is unavailable, the rules are in `{{VAULT}}/AGENTS.md`.
- One-off questions without a project (a lookup, a translation, a single command) need no memory.
- Secrets and personal data of third parties never go into the vault.
