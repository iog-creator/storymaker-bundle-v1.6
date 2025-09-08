
# StoryMaker — Unified Bundle (v1.6 FINAL, no optionals)

**Postgres 17 is REQUIRED.** `make api.up` auto-runs DB migration.

## Quickstart
```bash
make setup
docker compose up -d db redis minio
export POSTGRES_DSN=postgresql://story:story@localhost:5432/storymaker
make api.up
make seed.world
make test
```
