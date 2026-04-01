FROM node:22-alpine AS builder

WORKDIR /app

COPY package.json pnpm-lock.yaml* ./
RUN corepack enable pnpm && pnpm install --frozen-lockfile

COPY . .
RUN pnpm build

FROM node:22-alpine

WORKDIR /app

COPY --from=builder /app/dist ./dist
COPY --from=builder /app/admin-path.json ./
COPY package.json pnpm-lock.yaml* ./
RUN corepack enable pnpm && pnpm install --prod --frozen-lockfile

COPY server.mjs ./

ENV FLAG=HIT{r34ct_r0ut3_0bfusc4t10n}
EXPOSE 3000

CMD ["node", "server.mjs"]
