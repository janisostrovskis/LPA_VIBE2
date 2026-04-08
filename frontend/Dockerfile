# syntax=docker/dockerfile:1.7
FROM node:20-alpine

WORKDIR /app

# Copy lockfile first for layer cache.
COPY package.json package-lock.json ./
RUN npm ci

# Source comes in via the bind mount in docker-compose.yml for hot reload.
# The COPY below is what the image ships with when built outside compose.
COPY . .

ENV NEXT_TELEMETRY_DISABLED=1
EXPOSE 3000

# Dev server, bound to 0.0.0.0 so the host port mapping works.
# Phase 1 will replace this with a multi-stage `node server.js` (standalone build).
CMD ["npm", "run", "dev", "--", "--hostname", "0.0.0.0"]
