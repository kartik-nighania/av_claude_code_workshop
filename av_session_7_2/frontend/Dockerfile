# syntax=docker/dockerfile:1
# ---------------------------------------------------------------------------
# OrderTrack frontend — build the Vite app, serve static files via nginx.
# ---------------------------------------------------------------------------

# ---- Stage 1: build the static bundle -------------------------------------
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci || npm install
COPY . .
RUN npm run build

# ---- Stage 2: serve with nginx (unprivileged) -----------------------------
FROM nginxinc/nginx-unprivileged:1.27-alpine AS runtime
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD wget -qO- http://localhost:8080/ >/dev/null 2>&1 || exit 1
