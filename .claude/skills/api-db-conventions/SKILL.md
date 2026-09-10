---
name: api-db-conventions
description: Conventions for Flagger's FastAPI routes, Pydantic schemas, SQLAlchemy models, and Alembic migrations. Use when adding or changing an API endpoint, adding/altering a request or response schema, adding a DB column or table, writing a migration, or when you need to know which files must be touched together for a backend change.
---

# Flagger backend: API & DB conventions

Backend lives in `backend/`. Async SQLAlchemy 2.0 + asyncpg + Postgres, Pydantic v2, Alembic.

## Layout

| Concern | Location |
|---|---|
| Routes | `backend/app/api/routes/{auth,users,games,countries}.py` |
| Router mounting | `backend/app/main.py` |
| Shared deps (auth, rate limit) | `backend/app/api/deps.py` |
| Schemas | `backend/app/schemas/` |
| Models | `backend/app/models/` |
| Business logic | `backend/app/services/` |
| Migrations | `backend/alembic/versions/` |

Services exist only where logic is non-trivial (`auth_service`, `user_service`, `country_service`). `games.py` and `countries.py` keep their logic in the route module — don't create a service layer for a new endpoint unless there's real logic to move.

## Adding an endpoint: what to touch together

1. **Schema** in `app/schemas/<domain>.py` — request and/or response model.
2. **Route** in `app/api/routes/<domain>.py`, with `response_model=`.
3. **Model + migration** only if it needs new persistence (see below).
4. **Test** in `backend/tests/` — see the `testing-conventions` skill.
5. **Frontend client fn** in `frontend/src/api/flagQuiz.ts` (or a sibling), plus the matching TS interface. `frontend/src/api/client.ts` already handles auth headers and 401→refresh; use the exported `apiClient`, never bare `axios`.

New router? Register it in `app/main.py` with `app.include_router(x.router, prefix="/api/<domain>", tags=["<domain>"])`.

## Route conventions

Dependencies are injected via `Annotated`:

```python
@router.get("/history", response_model=List[GameSessionResponse])
async def get_game_history(
    current_user: Annotated[User, Depends(deps.get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(10, ge=1, le=100, description="Maximum results"),
):
```

- **Auth**: `Annotated[User, Depends(deps.get_current_user)]`. Bearer JWT; `deps.get_current_user` already rejects wrong token `type`, malformed UUIDs, and deleted users.
- **Rate limiting**: declared at the decorator, not as a parameter — `dependencies=[Depends(deps.rate_limit)]`. Currently on `/register`, `/login`, `/token` only. Add it to any new unauthenticated endpoint that touches credentials.
- **Query params**: always bounded — `Query(10, ge=1, le=100)`. Never accept an unbounded `limit`.
- **Errors**: raise `HTTPException(status_code=status.HTTP_*, detail="...")` directly, from routes *or* services. There are no custom exception classes and no global handlers. 401s carry `headers={"WWW-Authenticate": "Bearer"}`.
- **Commits are explicit.** `get_db` deliberately does not commit (`app/core/database.py`) — any write path must `await db.commit()` itself.

Two known inconsistencies — match the *majority* style in new code, don't copy these:
- `countries.py` declares its own `APIRouter(prefix="/countries")` and is mounted at `/api`; every other router takes its full prefix from `main.py`.
- `countries.py` uses the old `db: AsyncSession = Depends(get_db)` default-arg style instead of `Annotated`.

## Schema conventions

Naming: `XxxRequest` / `XxxResponse` (`RegisterRequest`, `TokenResponse`, `GameSessionResponse`). Fields are `snake_case` and match DB column names, so the frontend TS interfaces are snake_case too.

Response schemas read off ORM objects with `class Config: from_attributes = True`. (This is deprecated Pydantic-v2 style and emits a `PydanticDeprecatedSince20` warning under pytest — it's consistent across the codebase, so leave it unless converting all of them at once.)

**Validate at the trust boundary, not in the database.** `game_mode` is `Literal['practice', 'endless', 'gauntlet']` in `FlagQuizResult` and plain `String(20)` in the DB — migration 005 exists precisely because a Postgres enum meant a migration every time a mode was added. Follow that: constrain in Pydantic, keep the column permissive.

**Gotcha — Pydantic does not validate field defaults.** `Field(default_factory=list, min_length=1)` silently accepts an omitted field. If a constraint must hold, the field has to be required:

```python
answers: list[FlagQuizAnswer] = Field(..., min_length=1, max_length=1000)
```

Every user-supplied string and int gets explicit bounds (`max_length=100`, `ge=0, le=600_000`). Cross-field rules go in `@model_validator(mode="after")` — see `_no_repeated_countries` in `app/schemas/game.py`.

## Model conventions

Old-style `Column(...)` declarations (not 2.0 `Mapped[]`), all inheriting `Base` from `app.core.database`.

- PKs: `UUID(as_uuid=True), primary_key=True, default=uuid.uuid4` for `users`/`game_sessions`; plain autoincrement `Integer` for `countries`.
- Postgres-specific types are used freely: `ARRAY(String)`, `JSONB` (`GameSession.answers`).
- `Country` uses real DB enums via `Enum(RegionEnum, values_callable=lambda obj: [e.value for e in obj])` — the `values_callable` matters, it stores lowercase values instead of the enum member names.
- FKs cascade: `ForeignKey("users.id", ondelete="CASCADE")` plus `cascade="all, delete-orphan"` on the relationship.
- Any column the app filters or sorts on gets `index=True`.

New model file? Import it in `app/models/__init__.py` **and** in `alembic/env.py`'s `from app.models import user, game, country` line, or it won't be registered.

## Migrations

Alembic, hand-written (not autogenerated). `alembic/env.py` strips `+asyncpg` from `DATABASE_URL` because migrations run sync.

Revision IDs are **zero-padded sequential strings**, not hashes: `'001'` … `'007'`. A new one is `'008'` with `down_revision = '007'`, in a file named `008_short_description.py`. Don't run `alembic revision --autogenerate` and keep its generated hash.

Run them:

```bash
docker-compose exec backend alembic upgrade head
docker-compose exec backend alembic downgrade -1   # always test this too
```

Locally against the containerized DB (note `localhost`, not the compose hostname `db`):

```bash
cd backend && DATABASE_URL=postgresql+asyncpg://flagger:flagger_dev_password@localhost:5432/flagger \
  .venv/bin/alembic upgrade head
```

**Downgrade policy: never silently destroy data.** If the old schema can't represent existing rows, count them and refuse:

```python
def downgrade() -> None:
    incompatible = op.get_bind().execute(sa.text("SELECT count(*) FROM ...")).scalar()
    if incompatible:
        raise RuntimeError(f"Refusing to downgrade: {incompatible} row(s) ...")
```

`005_game_mode_to_varchar.py` is the reference for refusing; `007_drop_friendships_and_blocks.py` is the reference for a downgrade that faithfully recreates what it dropped.

## Cross-cutting gotchas

- **`/api/countries/catalog` is cached in-process** via a module-level `_catalog_cache` in `countries.py`, and also sends `Cache-Control: public, max-age=3600`. If you ever add a write path for countries, that cache needs invalidating — today only a process restart picks up a re-seed.
- **`settings.DEBUG` drives SQLAlchemy `echo`.** It defaults to `False`; don't turn it on in anything shipped.
- **Config** is Pydantic Settings (`app/core/config.py`) reading `../.env` then `.env`; `DATABASE_URL` and `SECRET_KEY` are required with no default.
- **Password hashing blocks ~250ms.** `get_password_hash`/`verify_password` are sync bcrypt and must be called via `await run_in_threadpool(...)`, as `auth_service` does — calling them directly in an `async def` stalls the whole event loop.
