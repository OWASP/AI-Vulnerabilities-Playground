# Build static SPA, then serve via nginx + /api reverse proxy
FROM node:20-alpine AS build

WORKDIR /src

COPY package.json package-lock.json* ./
RUN npm ci

COPY . .

# Same-origin API in Docker Compose (nginx proxies /api -> api service)
ARG VITE_API_BASE=/api
ENV VITE_API_BASE=$VITE_API_BASE
ARG VITE_CONTACT_EMAIL=avinash.kumar@owasp.org
ENV VITE_CONTACT_EMAIL=$VITE_CONTACT_EMAIL

RUN npm run build

FROM nginx:1.27-alpine

COPY --from=build /src/dist /usr/share/nginx/html
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
