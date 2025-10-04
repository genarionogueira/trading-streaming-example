"""
GraphQL server for data-svc.

This service exposes a Strawberry GraphQL API with:
- Query: lightweight health-check via `ping`
- Subscription: `prices` stream that emits synthetic price updates for symbols

Runtime behavior
- Generates deterministic-but-jittered price movements for a tracked set
  of symbols, emitting snapshots at an adjustable cadence.
- When Kafka is enabled, publishes every emitted snapshot to the `prices`
  topic using helpers from `data_svc.kafka_utils`.
- Kafka publishing is fire-and-forget (via `asyncio.create_task`) so
  subscribers are not delayed by broker latency.

Environment
- ENABLE_KAFKA, KAFKA_BOOTSTRAP_SERVERS, KAFKA_PRICE_TOPIC are read by
  `data_svc.kafka_utils`.

Integration
- The API is mounted under `/graphql` on a FastAPI app and is typically
  consumed by the API gateway and the UI via HTTP/WS.
"""

import asyncio
import random
import time
from datetime import datetime
from typing import AsyncGenerator, List, Optional

import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from .kafka_utils import (
    KAFKA_ENABLED,
    KAFKA_PRICE_TOPIC,
    encode_price,
    publish_batch,
    decode_price,
    create_started_consumer,
)


# ----- Domain Types -----
@strawberry.type
class Price:
    """GraphQL type representing a single price observation.

    Fields mirror the payload published to Kafka so downstream consumers can
    rely on a consistent schema across protocols.
    """
    symbol: str
    price: float
    change_percent: float
    timestamp: str


@strawberry.type
class Query:
    @strawberry.field
    def ping(self) -> str:
        """Simple liveness probe used by tests and orchestrators."""
        return "pong"


DEFAULT_SYMBOLS: List[str] = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]


def _initialize_prices(symbols: List[str]) -> dict[str, float]:
    """Create a deterministic initial price map for the provided symbols.

    Seeding randomness keeps test and demo runs stable while still producing
    varied starting points across symbols.
    """
    random.seed(42)
    base_prices: dict[str, float] = {}
    for s in symbols:
        # Start each equity at a deterministic but varied base
        base_prices[s] = round(random.uniform(100, 400), 2)
    return base_prices


def _apply_ticks(last_prices: dict[str, float], symbols: List[str], update_set: set[str]) -> list[Price]:
    """Advance prices for due symbols and return a full snapshot for all.

    Only symbols in `update_set` receive a new random walk step. All tracked
    symbols are included in the returned snapshot for subscriber simplicity.
    """
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
        - interval_seconds: base cadence for emitting update batches

        Implementation notes
        - Each symbol advances on its own jittered schedule. We still emit a
          complete snapshot every time any symbol updates so clients have a
          simple, idempotent stream to process.
        - When Kafka is enabled, each emitted snapshot is encoded and published
          to the `prices` topic without blocking the subscription iterator.
        """
        # If Kafka is enabled and a consumer can be created, stream from Kafka
        if KAFKA_ENABLED:
            consumer = await create_started_consumer(KAFKA_PRICE_TOPIC, group_id=None)
            if consumer is not None:
                try:
                    while True:
                        message = await consumer.getone()
                        data = decode_price(message.value)
                        if not data:
                            continue
                        yield [
                            Price(
                                symbol=str(data.get("symbol")),
                                price=float(data.get("price", 0.0)),
                                change_percent=float(data.get("change_percent", 0.0)),
                                timestamp=str(data.get("timestamp")),
                            )
                        ]
                finally:
                    await consumer.stop()
                return

        # Fallback to in-process generator when Kafka is disabled/unavailable
        tracked = symbols or DEFAULT_SYMBOLS
        last_prices = _initialize_prices(tracked)

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

            snapshot = _apply_ticks(last_prices, tracked, due_symbols)

            if KAFKA_ENABLED:
                asyncio.create_task(
                    publish_batch(KAFKA_PRICE_TOPIC, (encode_price(p) for p in snapshot))
                )

            yield snapshot

            for s in due_symbols:
                next_due[s] = now + interval_seconds * pace_factor[s] * random.uniform(0.8, 1.2)


# Create the GraphQL schema with subscription and mount it on FastAPI
schema = strawberry.Schema(query=Query, subscription=Subscription)

# Create FastAPI app and GraphQL route
app = FastAPI()
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")


# ---------------- Startup Publisher (Kafka) ----------------
_publisher_task: Optional[asyncio.Task] = None


async def _publisher_loop(symbols: List[str], interval_seconds: float = 1.0) -> None:
    """Background task that generates ticks and publishes them to Kafka.

    Publishes individual price messages as they occur to keep the stream granular.
    """
    last_prices = _initialize_prices(symbols)
    pace_factor: dict[str, float] = {s: random.uniform(0.5, 1.5) for s in symbols}
    next_due: dict[str, float] = {
        s: time.monotonic() + interval_seconds * pace_factor[s] * random.uniform(0.8, 1.2)
        for s in symbols
    }
    while True:
        now = time.monotonic()
        due_symbols = [s for s, due in next_due.items() if due <= now]
        if not due_symbols:
            sleep_time = max(0.01, min(next_due.values()) - now)
            await asyncio.sleep(min(sleep_time, 0.25))
            continue
        # Publish each due symbol as an individual message
        prices = _apply_ticks(last_prices, symbols, set(due_symbols))
        for p in prices:
            if p.symbol in due_symbols:
                await publish_batch(KAFKA_PRICE_TOPIC, (encode_price(p) for _ in [0]))
        for s in due_symbols:
            next_due[s] = now + interval_seconds * pace_factor[s] * random.uniform(0.8, 1.2)


@app.on_event("startup")
async def _on_startup() -> None:
    global _publisher_task
    if KAFKA_ENABLED and _publisher_task is None:
        _publisher_task = asyncio.create_task(_publisher_loop(DEFAULT_SYMBOLS))


@app.on_event("shutdown")
async def _on_shutdown() -> None:
    global _publisher_task
    if _publisher_task is not None:
        _publisher_task.cancel()
        try:
            await _publisher_task
        except Exception:
            pass
        _publisher_task = None


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)