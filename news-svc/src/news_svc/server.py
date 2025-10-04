import asyncio
import random
from datetime import datetime, timezone
from typing import AsyncGenerator, List

import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter


@strawberry.type
class NewsItem:
    id: int
    title: str
    summary: str
    source: str
    timestamp: str


from .examples import EXAMPLE_HEADLINES


def _build_news_pool() -> List[NewsItem]:
    pool: List[NewsItem] = []
    for i, item in enumerate(EXAMPLE_HEADLINES):
        pool.append(
            NewsItem(
                id=i + 1,
                title=item["title"],
                summary=item["summary"],
                source=item["source"],
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
        )
    return pool


NEWS_POOL: List[NewsItem] = _build_news_pool()


@strawberry.type
class Query:
    @strawberry.field
    def ping(self) -> str:
        return "pong"


def _random_news_batch(batch_size: int = 1) -> List[NewsItem]:
    return random.sample(NEWS_POOL, k=min(batch_size, len(NEWS_POOL)))


@strawberry.type
class Subscription:
    @strawberry.subscription
    async def news_feed(self, interval_seconds: float = 1.0, batch_size: int = 1) -> AsyncGenerator[List[NewsItem], None]:
        # Slightly slow down overall cadence while preserving jitter characteristics
        SLOW_FACTOR = 1.3
        while True:
            yield _random_news_batch(batch_size)
            # Add jitter so updates feel more realistic while staying fast
            low = max(0.05, interval_seconds * 0.5 * SLOW_FACTOR)
            high = max(low + 0.01, interval_seconds * 1.5 * SLOW_FACTOR)
            await asyncio.sleep(random.uniform(low, high))


schema = strawberry.Schema(query=Query, subscription=Subscription)

app = FastAPI()
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4000)