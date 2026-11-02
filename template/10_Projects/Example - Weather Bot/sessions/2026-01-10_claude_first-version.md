---
project: Example - Weather Bot
type: session
date: 2026-01-10
model: claude
topic: "first version"
---

# Session 2026-01-10: first version

## Goal of the session
Get a working bot that answers `/weather <city>`.

## Done
- Project skeleton on aiogram 3, `.env` for the token, SQLite for saved cities.
- `/weather <city>`: geocoding + current weather from Open-Meteo.

## What failed and why
- City names with typos return nothing — Open-Meteo geocoding has no fuzzy search.

## Decisions made
- D-001: Open-Meteo as the weather source.

## Changed files and artifacts
- `~/code/weather-bot`: `bot.py`, `weather.py`, `db.py`.

## Next steps
1. Morning broadcast.
2. Deploy to the VPS.

## Notes for the next model
- The free Open-Meteo tier allows 10,000 calls a day — plenty, but don't call it per message in a loop.
