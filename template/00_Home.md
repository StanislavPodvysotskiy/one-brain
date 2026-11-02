---
type: home
---

# One Brain

Protocol for AI models — [[AGENTS]]. Profile — [[User Profile]].

## Projects

| Project | Status | Next step |
|---|---|---|
| [[10_Projects/Example - Weather Bot/STATUS\|Example - Weather Bot]] | active | Add a 3-day forecast command |

<!-- Models: update your project's row when closing a session. -->

## Automatic summary (requires the Dataview plugin)

```dataview
TABLE status AS "Status", updated AS "Updated", model AS "Model", next AS "Next step"
FROM "10_Projects"
WHERE type = "status"
SORT updated DESC
```

## Latest sessions

```dataview
TABLE project AS "Project", model AS "Model", topic AS "Topic"
FROM "10_Projects"
WHERE type = "session"
SORT date DESC
LIMIT 10
```
