import os
import json
import logging
from typing import Optional, Iterable


# Configuration
KAFKA_ENABLED: bool = os.getenv("ENABLE_KAFKA", "false").lower() in {"1", "true", "yes"}
KAFKA_BOOTSTRAP: Optional[str] = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
KAFKA_NEWS_TOPIC: str = os.getenv("KAFKA_NEWS_TOPIC", "news")


try:
    from aiokafka import AIOKafkaProducer  # type: ignore
except Exception:  # pragma: no cover
    AIOKafkaProducer = None  # type: ignore


_producer: Optional["AIOKafkaProducer"] = None


async def ensure_producer() -> Optional["AIOKafkaProducer"]:
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
    producer = await ensure_producer()
    if producer is None:
        return
    try:
        for value in values:
            await producer.send_and_wait(topic, value)
    except Exception as exc:  # pragma: no cover
        logging.warning("Kafka publish failed: %s", exc)


def encode_news_item(item: object) -> bytes:
    payload = {
        "id": getattr(item, "id", None),
        "title": getattr(item, "title", None),
        "summary": getattr(item, "summary", None),
        "source": getattr(item, "source", None),
        "timestamp": getattr(item, "timestamp", None),
    }
    return json.dumps(payload).encode("utf-8")


