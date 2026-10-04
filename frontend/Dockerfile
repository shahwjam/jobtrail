# JobTrail frontend — multi-stage build
#
# Build:  docker build --build-arg VITE_API_URL=https://api.example.com -t jobtrail-frontend ./frontend
# Run:    docker run -p 8080:80 jobtrail-frontend

# ---- Stage 1: build the static bundle with Node ----
FROM node:22-alpine AS build
WORKDIR /app

# Lockfile first: `npm ci` is cached until dependencies actually change.
COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# Vite inlines import.meta.env.VITE_* at BUILD time — the API URL is baked
# into the JavaScript, so it's a build argument, not a runtime env var.
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

# ---- Stage 2: serve it with nginx ----
# Only the built files are copied over: no Node, no node_modules, no
# source. The final image is ~50 MB instead of ~500 MB.
FROM nginx:1.29-alpine

COPY nginx/default.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html

# Cloud hosts may assign a port via $PORT; nginx's template step fills it in.
ENV PORT=80
EXPOSE 80

HEALTHCHECK --interval=15s --timeout=3s --retries=3 \
    CMD wget -q -O /dev/null "http://127.0.0.1:${PORT}/" || exit 1
