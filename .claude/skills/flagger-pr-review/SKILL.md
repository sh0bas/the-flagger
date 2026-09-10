---
name: flagger-pr-review
description: Review a GitHub PR in the Flagger repo and post findings as a single batched inline review, and/or write a PR description grounded in tests actually run. Use when the user asks to review a PR, post/leave a review on GitHub, write or update a PR description, or open a PR for the current branch. Covers determining the real base branch, the review checklist for this repo (React/TS + FastAPI), and the exact gh commands that work. Deliberately named flagger-pr-review, not pr-review, to avoid being shadowed by the global pr-review skill.
---

# PR review & description writing — Flagger

Repo: `sh0bas/the-flagger`. Frontend `frontend/` (React 18 + TS + MUI v5 + Vite), backend `backend/` (FastAPI + async SQLAlchemy + Postgres).

## 1. Determine PR context — never assume the base branch

```bash
gh pr view <number> --json number,baseRefName,headRefName,headRefOid,commits,url
gh pr status              # if no number given and you need to find the current branch's PR
```

Diff against the branch `baseRefName` actually reports. It is usually `main` here, but read it, don't assume.

**Known trap — a stale base makes the diff lie.** The PR object's `base.sha` does *not* automatically advance when you push new commits to the base branch. A commit already merged into `main` can keep showing up in `gh pr diff` (and on the Files-changed tab) for a while afterward. Before reporting "this PR touches X", cross-check against local refs:

```bash
git fetch origin
git diff origin/<baseRefName>...origin/<headRefName> --stat
```

If the two disagree, the local diff is the truth and GitHub is catching up. Say so rather than reviewing a file the PR doesn't really change.

## 2. Inline review

### Gather

```bash
gh pr diff <number> > /tmp/pr.diff
gh pr view <number> --json headRefOid --jq .headRefOid    # every comment anchors to this SHA
```

Review **only the changed code**, not the whole repo.

### Checklist

**Hallucinated APIs / imports.** Verify against what's *installed*, not what looks plausible. Declared ranges and installed versions differ here:

| Package | Declared | Actually installed | Consequence |
|---|---|---|---|
| `@mui/material` | `^5.14.18` | **5.18.0 (v5)** | v6/v7 APIs don't exist — no `Grid` v2 props (`size={{xs:6}}`), no `theme.applyStyles`. Use v5 `Grid item xs={6}`. |
| `react` | `^18.2.0` | **18.3.1** | No `use()`, no React 19 form actions, no `ref` as a prop. |
| `react-router-dom` | `^6.20.0` | **6.30.3** | v6. And the app mounts plain `<Routes>`, not a data router — `errorElement`/loaders are unavailable (that's why `components/ErrorBoundary.tsx` is a class component). |
| `fastapi` | `==0.104.1` | 0.104.1 | Old. Features from 0.11x+ don't exist. |
| `pydantic` | `==2.5.0` | 2.5.0 | Early v2 — things added in 2.6+ (e.g. `Field(deprecated=...)`) are not available. |
| `sqlalchemy` | `==2.0.23` | 2.0.23 | 2.0 available, but this codebase uses legacy `Column(...)`, not `Mapped[]`. |
| `httpx` | `==0.25.2` | 0.25.2 | `AsyncClient(app=...)` still works here; the 0.28-style `ASGITransport`-only form is the newer API. |
| `pytest` | `==7.4.3` | **9.1.1 in `backend/.venv`, 7.4.3 in the container** | The venv has drifted from the pin; `backend/Dockerfile` installs `requirements.txt`, so `docker-compose exec backend pytest` runs 7.4.3 while `.venv/bin/python -m pytest` runs 9.x. Check behavior against whichever you're actually invoking. |

Check a symbol before trusting it: `node -e "console.log(require('./node_modules/<pkg>/package.json').version)"` from `frontend/`, or `cd backend && .venv/bin/python -c "import x; print(x.__version__)"`.

**Tautological / weak tests.** For every new or changed test, ask: *would this fail if the implementation were wrong?* Repo-specific traps:
- There is **no `pytest-asyncio`, `pytest-mock`, or `pytest-cov`** installed. An `async def` test fails loudly with "async def functions are not natively supported" — it does not silently pass, but it also doesn't test anything. Tests here are sync and pure by design.
- The suite has no DB and no HTTP client. A "test" that constructs a mock returning `{"score": 500}` and asserts `score == 500` verifies the mock. The real tests assert against `grade()` / `_points()` / `normalize_str()` directly — keep new ones in that shape.
- Boundary tests must sit *on* the boundary: `4_999`/`5_000`, streak `2`/`3`, cap at `20`/`21`. A test at `1_000` and `50_000` proves almost nothing.

**Pattern consistency.** Match this repo, don't import conventions from elsewhere:
- Backend errors: raise `HTTPException(status_code=status.HTTP_*, detail="...")` from route *or* service. No custom exception classes, no global handlers.
- Deps: `Annotated[AsyncSession, Depends(get_db)]`, `Annotated[User, Depends(deps.get_current_user)]`.
- `get_db` does **not** commit — writers commit explicitly.
- Schemas: `XxxRequest`/`XxxResponse`, snake_case fields, `class Config: from_attributes = True`.
- Frontend API calls go through the `apiClient` in `src/api/client.ts` (it handles the auth header and 401→refresh), never bare `axios`.
- Frontend error text comes from `errorMessage(err, fallback)` — FastAPI returns `detail` as a string for `HTTPException` but as an array of objects for 422s, and rendering that array raw gives `[object Object]`.
- Styling: MUI `sx` props, shared `gradientTextSx`/`gradientButtonSx`/`BRAND` from `src/theme.ts`. Flag new hardcoded brand hex literals — they belong in `theme.ts`.
- See the `api-db-conventions` and `testing-conventions` skills for the full picture.

**Over-engineering.** Single-user hobby app. Flag speculative abstraction: an interface with one implementation, a factory for one product, a config value that never changes, a service layer for logic with no logic. Deliberate simplifications are marked with `ponytail:` comments naming their ceiling — don't flag those as oversights; they're documented decisions.

**Missing edge cases.** Null/undefined inputs, empty result vs. error (an empty `answers` list is rejected at the schema, not silently scored 0), network failure paths, races (in-flight request guards, `useEffect` timers restarted by re-render), partial failures.

**Business logic correctness — scoring/anti-cheat especially.** This is the highest-value area. Check operation order and `>=` vs `>` against intent, not compilation: streak increments *before* `_points()` is called; the streak bonus starts at `>= 3`; `MAX_STREAK_BONUS` caps at 20; a wrong answer resets `streak` but not `max_streak`. Confirm no client-supplied derived field crept into `FlagQuizResult`, that duplicate `country_id`s are still rejected, and that `normalize_str` still matches `normalizeForComparison()` on the client. Full detail in the `scoring-anticheat` skill.

**Stale patterns / deps.** Flag deprecated APIs *introduced* by the diff. Pre-existing ones (the `class Config` Pydantic style, `datetime.utcnow()`) are consistent across the codebase — mention at most once, as a nit, not per-occurrence.

### Post as a single batched review

Build one JSON file and submit once — not one API call per comment.

```bash
cat > /tmp/review.json <<'EOF'
{
  "commit_id": "<headRefOid>",
  "event": "COMMENT",
  "body": "<summary of what the PR does — see 'Writing the body' below>",
  "comments": [
    { "path": "backend/app/api/routes/games.py", "line": 42, "side": "RIGHT",
      "body": "🟠 Important — <finding>" }
  ]
}
EOF
gh api -X POST repos/sh0bas/the-flagger/pulls/<number>/reviews --input /tmp/review.json
```

Always `--input <file>`. **Never** `-f body=@file` — that shortcut does not read the file, it posts the literal string `@file` as the comment body. (This actually happened on PR #1 and every comment had to be PATCHed afterward.) `--input` also sidesteps all shell-quoting problems with backticks and emoji in bodies.

**One bad line kills the whole review.** GitHub only accepts a comment on a line inside the diff's hunks (changed lines plus a few lines of context). With a batched review, a single off-diff `line` 422s the *entire* submission — nothing posts. So before submitting:

- Anchor every comment to a line you can actually see in `/tmp/pr.diff` with a `+` or context prefix in that file's hunks.
- For a finding whose *cause* is in the diff but whose *symptom* is in an untouched file, anchor to the causing line and name the other file in the text.
- For anything that genuinely can't anchor, put it in the review `body` instead of dropping it.

Then verify it landed: `gh api repos/sh0bas/the-flagger/pulls/<number>/comments --jq '.[].body' | head` — confirm real prose, not a filename.

To fix the body after submitting, the verb is **`PUT`**, not `PATCH` (`PATCH` returns a bare `404`):

```bash
gh api --method PUT repos/sh0bas/the-flagger/pulls/<number>/reviews/<review_id> --input -   # {"body": "..."}
```

### Writing the body

**Everything posts under the repo owner's GitHub account** — `gh` is authenticated as them, so there is no bot identity and no "reviewed by" attribution. Write the body in the voice of the person whose name is on it.

That means the body is a **summary of what the PR does**, not a report on the review. Never narrate your own process:

> ~~"Reviewed the four skill files against the live repo rather than for code bugs. Most claims check out. One real problem: …"~~

Reading that under your own name is jarring — it sounds like the author reviewing their own PR in the third person. Write this instead:

> Adds four project-scoped Claude Code skills under `.claude/skills/`, capturing conventions that were previously only discoverable by reading the whole codebase:
>
> - **`api-db-conventions`** — route/schema/model patterns, which files change together for a new endpoint, and the policy that downgrades refuse rather than silently delete data.
> - **`scoring-anticheat`** — the `_points` formula and the invariants that keep `save-result` server-authoritative.
>
> Also loosens `.gitignore`: the blanket `*.md` rule existed to keep personal notes out of the repo, but it hid every doc worth committing — including these skills. Personal notes now live in `local-docs/` instead.

The shape that works:

1. **One opening sentence** — what the PR adds or changes, and where. No preamble.
2. **A bullet per component** — `**\`name\`**` in bold, em-dash, then what it actually covers. Concrete nouns, not "improvements to X".
3. **A closing paragraph for anything non-obvious** — and give the *why*, especially when a change looks unrelated or overreaching. "Loosens `.gitignore`" invites a question; "the blanket rule hid every doc worth committing" answers it.

Keep the findings themselves in the inline comments where they're anchored to code. The body carries the change, not the critique — a reader scanning the PR list should learn what this branch is for.

### Priority labels

Prefix every comment. Keep nits rare — a review of 12 nits and one real bug buries the bug.

- 🔴 **Critical** — data loss, security, silently wrong scores
- 🟠 **Important** — real bug or missing edge case
- 🟡 **Suggestion** — worth doing, not blocking
- 🔵 **Nit** — style/naming; skip most of these

## 3. PR description

```markdown
## What
<opening sentence, then a bullet per component — same shape and voice as
"Writing the body" above, which applies verbatim here>

## Why
<the motivating reason or issue — skip this heading if the What already
carries it; don't pad it with a restatement>

## Testing
- Backend: `cd backend && .venv/bin/python -m pytest tests/ -q` — <N passed / failed>
- Frontend: `npx tsc --noEmit`, `npm run lint`, `npm run build` — <result>
```

Same voice rules as the review body: it publishes under the owner's account, so describe the change, never the process that produced it. If you already wrote a review body for this PR, reuse it here rather than composing a second, differently-worded summary.

**Run the commands before writing the results.** Never state a pass/fail you didn't observe.

**There is no frontend test suite.** `frontend/package.json` has no `test` script — no vitest, no jest, no RTL. Do not write "frontend tests pass". The honest frontend line is type-check + lint + build, and for UI changes, say explicitly whether you actually ran the app and looked at it. If a change is visual and unverified in a browser, say that.

The backend suite runs in well under a second and emits one expected `PydanticDeprecatedSince20` warning that is not a failure. Report the counts pytest actually printed rather than a number carried over from a previous run.

Post it:

```bash
gh pr edit <number> --body-file /tmp/pr-body.md     # PR exists
gh pr create --base <baseRefName> --body-file /tmp/pr-body.md --title "<title>"
```

`--body-file` reads the file correctly — unlike the `-f field=@file` trick above, this one is safe.

If the user asked for the description *in chat* to copy-paste themselves, print it in a fenced markdown block and post nothing.

## Before posting anything

Posting a review is public and awkward to undo. Unless the user already said to post, confirm first — and when they only asked for a review, showing findings in chat is the default, not posting.
