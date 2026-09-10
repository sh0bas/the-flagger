---
name: scoring-anticheat
description: Flagger's server-authoritative scoring formula, grading path, and the invariants that stop a tampered payload from inflating a score. Use when changing how points/streaks are calculated, editing the save-result endpoint or FlagQuizResult schema, touching answer normalization, adjusting rate limits, or reviewing anything that affects what score a player can claim.
---

# Flagger scoring & anti-cheat

There is **no leaderboard, no ranking, and no tie-breaking** in this codebase — scores are per-user history only (`GET /api/games/history`). A `schemas/leaderboard.py` once existed as unused response shapes and was deleted in `2c62389`. If you're asked about ranking rules, they don't exist yet; don't invent them.

What does exist is a server-authoritative scoring path, and it's the security-sensitive part of the app.

## The core design

**The client's numbers are not on the wire.** `FlagQuizResult` (`backend/app/schemas/game.py`) deliberately carries no `score`, `correct_count`, `questions_count`, `max_streak`, or `avg_response_ms`. It carries only what the player did:

```python
game_mode: Literal['practice', 'endless', 'gauntlet']
regions / entity_types / difficulties: list[str]
answers: list[FlagQuizAnswer]      # country_id, user_answer, response_ms
```

Everything else is derived server-side by `grade()` in `backend/app/api/routes/games.py`. This is why there's no score-validation branch and no tolerance policy anywhere: **there is no client-supplied number to disagree with.** Preserve that property. Adding a client-sent derived field re-opens the hole the whole design closes.

`frontend/src/hooks/useQuizReducer.ts`'s `calcScore()` is a **display-only mirror** so the player sees a running total. `Summary.tsx` overwrites it with the server's score once `save-result` responds — that swap is also the drift detector.

## The formula

`_points(response_ms, streak)` — `backend/app/api/routes/games.py`. `streak` is the count *including* the current answer.

| Component | Rule |
|---|---|
| Base | `100` per correct answer |
| Speed | `+50` if `response_ms < 5_000`; else `+25` if `< 10_000`; else nothing |
| Streak | `+10 * min(streak, 20)` once `streak >= 3` |

Constants: `FAST_MS = 5_000`, `MEDIUM_MS = 10_000`, `STREAK_THRESHOLD = 3`, `MAX_STREAK_BONUS = 20`. Wrong answers score nothing and reset `streak` to 0; `max_streak` keeps the high-water mark.

The cap exists so a long correct run can't grow per-answer score without bound. `MAX_STREAK_BONUS` is duplicated in `useQuizReducer.ts` — **change both together or the displayed score silently diverges from the saved one.**

## Invariants that must hold

1. **No client-supplied derived value is ever persisted.** `save-result` writes only what `grade()` returned.
2. **`answers` must be non-empty and must not repeat a `country_id`.** Enforced by `Field(..., min_length=1, max_length=1000)` and the `_no_repeated_countries` model validator. Repeating one easy flag is how a crafted payload would farm the streak bonus — and note the field is *required*, not defaulted, because **Pydantic does not validate defaults**: with `default_factory=list` the `min_length=1` check silently passes when the field is omitted entirely.
3. **An unknown `country_id` can never be correct.** `grade()` looks names up in `names_by_id` with `.get(id, ())`, so an id absent from the DB matches nothing.
4. **Per-answer inputs are bounded at the schema**: `user_answer` `max_length=100`, `response_ms` `ge=0, le=600_000`. A negative or absurd `response_ms` must not buy a speed bonus.
5. **Grading is pure.** `grade(answers, names_by_id)` touches no DB and no clock, which is what makes the anti-cheat path testable without fixtures. Keep it that way — do the I/O in the route.
6. **One query, not N.** The route collects `{a.country_id for a in result.answers}` and issues a single `select(Country).where(Country.id.in_(ids))`. A full gauntlet is ~290 answers; per-answer lookups would be 290 sequential round trips.
7. **Client and server must normalize identically.** `normalize_str()` (`app/services/country_service.py`) and `normalizeForComparison()` (`useQuizReducer.ts`) decide, respectively, what scores and what the player was told was correct. Divergence marks correct answers wrong.

## Normalization, specifically

Both sides: NFD-decompose → strip combining marks `[̀-ͯ]` → lowercase → fold `'`/`'`/`` ` `` to `'` → trim.

**Never reintroduce `.encode("ascii", "ignore")`.** It doesn't just drop accents — it deletes every character NFD doesn't decompose (`ß`, `ø`, and *entire* non-Latin scripts). Two different Cyrillic names both normalize to `""` and compare **equal**, which is a false positive, not merely a missed match. This was a real bug, not a hypothetical — see `22423af` for the fix and the evidence behind it.

Also note `.lower()` does not fold `ß` → `ss`. Verify actual output before asserting on it.

## Rate limiting

`deps.rate_limit` (`backend/app/api/deps.py`) — in-process sliding window, 10 requests / 60s per client IP, applied via `dependencies=[Depends(deps.rate_limit)]` on `/register`, `/login`, `/token`. It sweeps fully-expired entries on each call so `_hits` stays bounded.

Two documented ceilings, both marked with `ponytail:` comments — respect them rather than rediscovering:
- **Single-worker only.** Behind a load balancer each worker gets its own budget; needs a shared store if it ever runs replicated.
- **Raw peer address, no `X-Forwarded-For`.** Behind a proxy that doesn't forward the real client IP, every request collapses onto one key. Any fix must trust only a known proxy hop.

`save-result` is **not** rate-limited — it requires a valid JWT.

## When changing this code, verify

- [ ] `cd backend && .venv/bin/python -m pytest tests/ -q` — `test_scoring.py` is the file that matters here
- [ ] If you touched `_points`, `MAX_STREAK_BONUS`, or the bonus tiers: update `calcScore()` in `frontend/src/hooks/useQuizReducer.ts` in the same change, and test each threshold at its exact boundary (`4_999` / `5_000` / `9_999` / `10_000`, streak `2` / `3`, cap at `20` / `21` / absurd)
- [ ] If you touched `normalize_str`: update `normalizeForComparison()` to match, and assert non-Latin scripts survive *and* stay distinct from each other — not just that diacritics strip
- [ ] If you touched `FlagQuizResult`: test the omitted case and the empty case separately (defaults bypass validation), plus duplicate `country_id` rejection
- [ ] Confirm no derived field crept into the request schema, and that `save-result` still persists only `grade()` output
- [ ] Adversarial check, not just the happy path: POST a hand-crafted payload with garbage answers and confirm the persisted score is 0
