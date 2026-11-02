---
project: Example - Weather Bot
type: status
status: active
updated: 2026-01-18
model: kimi
next: Add a 3-day forecast command
---

# Status: Example - Weather Bot

> A short snapshot as of today. Details are in sessions/, reasons for decisions in DECISIONS.md.

## Now
The bot is deployed and sends morning messages. The forecast command is next.

## Done
- `/weather <city>` and the saved city per user (SQLite).
- Morning broadcast at 8:00 in each user's time zone.
- Deployed as a systemd service; restarts on failure.

## In progress
- 

## Next steps
1. Add `/forecast` — a 3-day forecast (Open-Meteo `daily` endpoint).
2. Cache geocoding results so repeated city names don't hit the API.

## Open questions and blockers
- Should the morning message include the forecast, or stay short?
