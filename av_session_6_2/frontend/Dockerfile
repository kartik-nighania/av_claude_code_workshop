# Stage 1: Builder — install deps and build the static bundle.
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Runtime — non-root nginx serving the static bundle + proxying /api.
FROM nginxinc/nginx-unprivileged:stable-alpine AS runtime
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 3000
# Use 127.0.0.1 (not localhost) — busybox wget would try IPv6 ::1 first, but
# nginx here listens on IPv4 only.
HEALTHCHECK CMD wget -q -O /dev/null http://127.0.0.1:3000/healthz || exit 1
