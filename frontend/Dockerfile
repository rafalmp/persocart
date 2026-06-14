# syntax=docker/dockerfile:1
# ============================================
# Base (Bun)
# ============================================
FROM oven/bun:1 AS base
WORKDIR /app

# ============================================
# Dependencies
# ============================================
FROM base AS deps
COPY package.json bun.lock* ./
RUN bun install

# ============================================
# Dev — Vite dev server (compose mounts source)
# ============================================
FROM deps AS dev
COPY . .
EXPOSE 5173
CMD ["bun", "run", "dev"]

# ============================================
# Build — produce static SPA assets
# ============================================
FROM deps AS build
COPY . .
RUN bun run build

# ============================================
# Runtime — static assets served by Caddy (production draft, Phase 5)
# ============================================
FROM caddy:2-alpine AS runtime
COPY --from=build /app/dist /srv
EXPOSE 80
