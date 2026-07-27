# UAE Services Hub — realtime (Socket.IO)
FROM node:22-alpine
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY realtime ./realtime
COPY tsconfig.json ./
EXPOSE 4000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget -qO- http://localhost:4000/health || exit 1
CMD ["npx", "tsx", "realtime/index.ts"]
