import asyncio
import random
import time
from datetime import datetime
from typing import AsyncGenerator, List, Optional

import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter


# ----- Domain Types -----
@strawberry.type
class Price:
    symbol: str
    price: float
    change_percent: float
    timestamp: str


@strawberry.type
class Query:
    @strawberry.field
    def ping(self) -> str:
        return "pong"


DEFAULT_SYMBOLS: List[str] = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]


def _initialize_prices(symbols: List[str]) -> dict[str, float]:
    random.seed(42)
    base_prices: dict[str, float] = {}
    for s in symbols:
        # Start each equity at a deterministic but varied base
        base_prices[s] = round(random.uniform(100, 400), 2)
    return base_prices


def _apply_ticks(last_prices: dict[str, float], symbols: List[str], update_set: set[str]) -> list[Price]:
    snapshot: list[Price] = []
    for s in symbols:
        prev = last_prices[s]
        if s in update_set:
            delta = prev * random.uniform(-0.01, 0.01)
            new_price = max(0.01, round(prev + delta, 2))
            change_pct = ((new_price - prev) / prev) * 100 if prev > 0 else 0.0
            last_prices[s] = new_price
            price_value = new_price
            change_value = round(change_pct, 2)
        else:
            price_value = prev
            change_value = 0.0

        snapshot.append(
            Price(
                symbol=s,
                price=price_value,
                change_percent=change_value,
                timestamp=datetime.utcnow().isoformat() + "Z",
            )
        )
    return snapshot


@strawberry.type
class Subscription:
    @strawberry.subscription
    async def prices(
        self,
        symbols: Optional[List[str]] = None,
        interval_seconds: float = 1.0,
    ) -> AsyncGenerator[List[Price], None]:
        """Stream random price updates for the requested symbols.

        - symbols: optional filter list; defaults to a preset basket
        - interval_seconds: how often to push an update batch
        """
        tracked = symbols or DEFAULT_SYMBOLS
        last_prices = _initialize_prices(tracked)

        # Assign each symbol an individual pace factor and next due time
        pace_factor: dict[str, float] = {s: random.uniform(0.5, 1.5) for s in tracked}
        next_due: dict[str, float] = {
            s: time.monotonic() + interval_seconds * pace_factor[s] * random.uniform(0.8, 1.2)
            for s in tracked
        }

        while True:
            now = time.monotonic()
            due_symbols = {s for s, due in next_due.items() if due <= now}
            if not due_symbols:
                sleep_time = max(0.01, min(next_due.values()) - now)
                await asyncio.sleep(min(sleep_time, 0.25))
                continue

            # Apply ticks only to due symbols but emit a full snapshot for all tracked symbols
            yield _apply_ticks(last_prices, tracked, due_symbols)

            # Schedule next due time for updated symbols with slight jitter
            for s in due_symbols:
                next_due[s] = now + interval_seconds * pace_factor[s] * random.uniform(0.8, 1.2)


# Create the GraphQL schema with subscription
schema = strawberry.Schema(query=Query, subscription=Subscription)

# Create FastAPI app and GraphQL route
app = FastAPI()
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)