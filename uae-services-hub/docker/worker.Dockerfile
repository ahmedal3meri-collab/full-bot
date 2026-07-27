# UAE Services Hub — worker (مهام خلفية، BullMQ/سويب مجدول)
FROM node:22-alpine
WORKDIR /app
RUN apk add --no-cache openssl
COPY package.json package-lock.json ./
RUN npm ci
COPY prisma ./prisma
COPY worker ./worker
COPY tsconfig.json ./
RUN npx prisma generate
CMD ["npx", "tsx", "worker/index.ts"]
