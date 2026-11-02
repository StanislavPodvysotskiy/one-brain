---
project: Example - Weather Bot
type: session
date: 2026-01-18
model: kimi
topic: "morning broadcast"
---

# Session 2026-01-18: morning broadcast

## Goal of the session
Send every user the weather at 8:00 local time and deploy the bot.

## Done
- Per-user time zone from the city's coordinates; the broadcast runs every minute and picks users
  whose local time is 08:00.
- systemd unit with `Restart=on-failure`; deployed to the VPS.

## What failed and why
- First attempt used the server time zone for everyone — users in other zones got the message at night.

## Decisions made
- D-002: per-user time zone.

## Changed files and artifacts
- `~/code/weather-bot`: `scheduler.py`, `deploy/weather-bot.service`.

## Next steps
1. `/forecast` — 3-day forecast.

## Notes for the next model
- Claude built the first version (see the 2026-01-10 session); the code style there is the reference.
