FROM node:22-alpine AS builder

WORKDIR /app

COPY package.json pnpm-lock.yaml* ./
RUN corepack enable pnpm && pnpm install --frozen-lockfile

COPY src ./src
COPY public ./public
COPY scripts ./scripts
COPY index.html .
COPY vite.config.ts .
COPY tsconfig.json .
COPY tsconfig.app.json .
COPY tsconfig.node.json .

RUN pnpm build

FROM node:22-alpine

WORKDIR /app

COPY --from=builder /app/dist ./dist
COPY --from=builder /app/admin-path.json ./
COPY package.json pnpm-lock.yaml* ./
RUN corepack enable pnpm && pnpm install --prod --frozen-lockfile

COPY src/server.mjs ./server.mjs
COPY src/flag.txt /flag.txt

ENV FLAG_FILE=/flag.txt
EXPOSE 3000

CMD ["node", "server.mjs"]
