"""
Async Kafka utilities for data-svc.

This module encapsulates Kafka publisher concerns so the GraphQL layer stays
clean and focused on schema/resolvers.

Responsibilities
- Read configuration from environment variables
- Lazily create and cache a single AIOKafkaProducer instance
- Encode a Price-like object into a JSON payload matching the GraphQL shape
- Publish an iterable of bytes to a Kafka topic
- Fail safely (no-ops) when Kafka is disabled or unavailable

Environment variables
- ENABLE_KAFKA: enable/disable Kafka usage (default: false)
- KAFKA_BOOTSTRAP_SERVERS: Kafka bootstrap servers (default: "kafka:9092").
  Optional override; comma-separated host:port entries are supported.
- KAFKA_PRICE_TOPIC: topic name for price events (default: "prices")

Usage
    from .kafka_utils import KAFKA_ENABLED, KAFKA_PRICE_TOPIC, encode_price, publish_batch

    if KAFKA_ENABLED:
        asyncio.create_task(
            publish_batch(KAFKA_PRICE_TOPIC, (encode_price(p) for p in prices))
        )

Note: publish_batch awaits each send to preserve ordering guarantees while
remaining simple. In high-throughput scenarios consider batching or fire-and-
forget sends with careful backpressure handling.
"""

import os
import json
import logging
from typing import Optional, Iterable


KAFKA_ENABLED: bool = os.getenv("ENABLE_KAFKA", "false").lower() in {"1", "true", "yes"}
KAFKA_BOOTSTRAP: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
KAFKA_PRICE_TOPIC: str = os.getenv("KAFKA_PRICE_TOPIC", "prices")


try:
    from aiokafka import AIOKafkaProducer, AIOKafkaConsumer  # type: ignore
except Exception:  # pragma: no cover
    AIOKafkaProducer = None  # type: ignore
    AIOKafkaConsumer = None  # type: ignore


_producer: Optional["AIOKafkaProducer"] = None


async def ensure_producer() -> Optional["AIOKafkaProducer"]:
    """Return a started singleton AIOKafkaProducer or None if disabled/unavailable.

    - Creates and starts the producer on first call (lazy init)
    - Returns None when Kafka is disabled, misconfigured, or the client
      is not importable (e.g., missing dependency)
    """
    global _producer
    if not KAFKA_ENABLED or not KAFKA_BOOTSTRAP or AIOKafkaProducer is None:
        return None
    if _producer is None:
        try:
            _producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP)
            await _producer.start()
        except Exception as exc:  # pragma: no cover
            logging.warning("Kafka producer start failed: %s", exc)
            _producer = None
    return _producer


async def publish_batch(topic: str, values: Iterable[bytes]) -> None:
    """Publish an iterable of byte payloads to a topic.

    Ensures a producer exists. If unavailable, returns without error.
    Logs (warn) on failures but does not raise to avoid impacting callers.
    """
    producer = await ensure_producer()
    if producer is None:
        return
    try:
        for value in values:
            await producer.send_and_wait(topic, value)
    except Exception as exc:  # pragma: no cover
        logging.warning("Kafka publish failed: %s", exc)


def encode_price(item: object) -> bytes:
    """Encode a Price-like object to JSON bytes using snake_case field names.

    The on-wire schema mirrors the Python/GraphQL type attributes exactly:
    symbol, price, change_percent, timestamp. This keeps the GraphQL type as
    the single source of truth and avoids case-mapping at the boundaries.
    """
    payload = {
        "symbol": getattr(item, "symbol", None),
        "price": getattr(item, "price", None),
        "change_percent": getattr(item, "change_percent", None),
        "timestamp": getattr(item, "timestamp", None),
    }
    return json.dumps(payload).encode("utf-8")


def decode_price(value: bytes) -> dict:
    """Decode a JSON price payload into a dict using snake_case field names."""
    try:
        obj = json.loads(value.decode("utf-8"))
    except Exception:
        return {}
    return {
        "symbol": obj.get("symbol"),
        "price": obj.get("price"),
        "change_percent": obj.get("change_percent"),
        "timestamp": obj.get("timestamp"),
    }


async def create_started_consumer(topic: str, group_id: str | None = None):
    """Create and start a consumer subscribed to topic or return None if disabled.

    Uses latest offsets by default; intended for live streaming. Call stop() on
    the returned consumer when finished.
    """
    if not KAFKA_ENABLED or not KAFKA_BOOTSTRAP or AIOKafkaConsumer is None:
        return None
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=KAFKA_BOOTSTRAP,
        group_id=group_id,
        auto_offset_reset="latest",
        enable_auto_commit=True,
    )
    await consumer.start()
    return consumer

