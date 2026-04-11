# /dev — Start LPA dev environment

Start the full local development stack (PostgreSQL + FastAPI backend + Next.js frontend) using Docker Compose.

## Steps

1. **Pre-flight checks** — Verify Docker daemon is running (`docker info`). If not, tell the user to start Docker Desktop and stop.

2. **Ensure .env exists** — Check if `.env` exists in the project root. If not, copy `.env.example` to `.env` and inform the user.

3. **Port conflict check** — Before building, verify that the ports used by Docker Compose are free:
   ```bash
   lsof -i :5432 | head -3   # PostgreSQL
   lsof -i :3000 | head -3   # Frontend
   lsof -i :8001 | head -3   # Backend API
   ```
   If any port is already in use (e.g., a local PostgreSQL instance on 5432, or another dev server on 3000), remap the **host-side** port in `docker-compose.yml` to a free port (e.g., `5433:5432`, `3001:3000`) before continuing. Do NOT remap the container-side port. Inform the user of the remapped ports.

4. **Build and start** — Run `docker compose up --build -d` to build images and start all services in detached mode.

5. **Wait for health** — Poll `docker compose ps` until all three containers (lpa-db, lpa-backend, lpa-frontend) are running/healthy. Timeout after 90 seconds.

6. **Run migrations** — Execute `docker compose exec backend alembic upgrade head` to apply any pending database migrations.

7. **Smoke test** — Hit the backend health endpoint: `curl -sf http://localhost:8001/health`. Report success or failure.

8. **Report** — Print a summary using the actual (possibly remapped) host ports:
   - Database: `localhost:<db_host_port>`
   - Backend API: `http://localhost:8001` (docs at `/docs`)
   - Frontend: `http://localhost:<frontend_host_port>`
   - Logs: `docker compose logs -f`
   - Stop: `docker compose down`

If any step fails, show the relevant `docker compose logs <service>` output and suggest fixes.

## Arguments

- `$ARGUMENTS` — Optional flags passed through. Examples:
  - `--no-build` — skip the build step (use existing images)
  - `--fresh` — tear down volumes first (`docker compose down -v`) for a clean slate
  - `--logs` — stay attached to logs after startup instead of detaching
