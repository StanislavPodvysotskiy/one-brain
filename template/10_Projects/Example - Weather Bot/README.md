---
project: Example - Weather Bot
type: readme
repo: ~/code/weather-bot
status: active
created: 2026-01-10
---

# Example - Weather Bot

> This is a sample project that shows what a filled-in card looks like. Delete it whenever you like
> (and its row in `00_Home.md`).

## Goal
A Telegram bot that sends the current weather for a saved city every morning at 8:00
and answers `/weather <city>` on demand.

## Context
- Personal project, a few dozen friends and family members use it.
- Weather data comes from the Open-Meteo API (free, no key required).

## Constraints and requirements
- Runs on a small VPS next to other services, so memory use must stay under 128 MB.
- The bot token lives only in `.env` on the server, never in the repository or this vault.

## Stack and resources
- Python 3.12, aiogram 3, SQLite, systemd.
- Code: `~/code/weather-bot`.

## Definition of done
- Morning messages arrive reliably for a month without manual restarts.
- `/weather` and `/forecast` work for any city name in English or Russian.
