# /dev — Start LPA dev environment

Start the full local development stack (PostgreSQL + FastAPI backend + Next.js frontend) using Docker Compose.

## Steps

1. **Pre-flight checks** — Verify Docker daemon is running (`docker info`). If not, tell the user to start Docker Desktop and stop.

2. **Ensure .env exists** — Check if `.env` exists in the project root. If not, copy `.env.example` to `.env` and inform the user.

3. **Build and start** — Run `docker compose up --build -d` to build images and start all services in detached mode.

4. **Wait for health** — Poll `docker compose ps` until all three containers (lpa-db, lpa-backend, lpa-frontend) are running/healthy. Timeout after 90 seconds.

5. **Run migrations** — Execute `docker compose exec backend alembic upgrade head` to apply any pending database migrations.

6. **Smoke test** — Hit the backend health endpoint: `curl -sf http://localhost:8001/health`. Report success or failure.

7. **Report** — Print a summary:
   - Database: `localhost:5432`
   - Backend API: `http://localhost:8001` (docs at `/docs`)
   - Frontend: `http://localhost:3000`
   - Logs: `docker compose logs -f`
   - Stop: `docker compose down`

If any step fails, show the relevant `docker compose logs <service>` output and suggest fixes.

## Arguments

- `$ARGUMENTS` — Optional flags passed through. Examples:
  - `--no-build` — skip the build step (use existing images)
  - `--fresh` — tear down volumes first (`docker compose down -v`) for a clean slate
  - `--logs` — stay attached to logs after startup instead of detaching
