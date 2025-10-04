FROM node:20-alpine AS base

WORKDIR /app

COPY package.json package-lock.json* yarn.lock* pnpm-lock.yaml* ./
RUN \
    if [ -f yarn.lock ]; then yarn --frozen-lockfile; \
    elif [ -f package-lock.json ]; then npm ci --omit=dev; \
    elif [ -f pnpm-lock.yaml ]; then npm i -g pnpm && pnpm i --frozen-lockfile --prod; \
    else npm i --omit=dev; fi

COPY . .

EXPOSE 4000

RUN npx --yes mesh build || true

CMD ["sh", "-lc", "npx mesh start || npx mesh dev -p 4000"]


