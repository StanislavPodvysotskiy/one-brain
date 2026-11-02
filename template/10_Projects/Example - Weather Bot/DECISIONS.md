---
project: Example - Weather Bot
type: decisions
---

# Decisions: Example - Weather Bot

> New entries go on top. Old ones are never deleted: if a decision is revised, add a new one
> linking to the old one and set the old one's status to "superseded".

## D-002. Per-user time zone for the morning message
- **Date:** 2026-01-18 · **Model:** kimi
- **Status:** accepted
- **Context:** friends live in different time zones; 8:00 server time woke some of them at night.
- **Decision:** store an IANA time zone per user, detected from the saved city's coordinates.
- **Why:** no extra question to the user; the city already gives the location.
- **Rejected options:** asking every user for their time zone — friction, people skip it.

## D-001. Open-Meteo as the weather source
- **Date:** 2026-01-10 · **Model:** claude
- **Status:** accepted
- **Context:** needed a free weather API for a small personal bot.
- **Decision:** Open-Meteo.
- **Why:** free, no API key, includes geocoding and daily forecasts.
- **Rejected options:** OpenWeatherMap — requires a key and has tighter free limits.

<!-- Entry template (copy above this line):

## D-001. Short decision title
- **Date:** YYYY-MM-DD · **Model:** claude / kimi / qwen / human
- **Status:** accepted | superseded by D-00N | cancelled
- **Context:** what problem or question there was.
- **Decision:** what was chosen.
- **Why:** the main reasons.
- **Rejected options:** what else was considered and why not.
-->
