import pytest
from httpx import AsyncClient, ASGITransport
from starlette.testclient import TestClient

from news_svc.server import app


@pytest.mark.asyncio
async def test_ping_query_returns_pong():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        query = """
        query { ping }
        """
        resp = await client.post("/graphql", json={"query": query})
        assert resp.status_code == 200
        payload = resp.json()
        assert payload.get("data", {}).get("ping") == "pong"


def test_news_feed_subscription_streams_updates():
    subscription = {
        "id": "1",
        "type": "subscribe",
        "payload": {
            "query": (
                "subscription { newsFeed(intervalSeconds: 0.05, batchSize: 2) { "
                "id title summary source timestamp } }"
            )
        },
    }

    with TestClient(app) as client:
        with client.websocket_connect("/graphql", subprotocols=["graphql-transport-ws"]) as websocket:
            websocket.send_json({"type": "connection_init", "payload": {}})
            ack = websocket.receive_json()
            assert ack["type"] == "connection_ack"

            websocket.send_json(subscription)
            msg = websocket.receive_json()
            assert msg["type"] == "next"
            assert msg["id"] == "1"
            data = msg["payload"]["data"]["newsFeed"]
            assert isinstance(data, list)
            assert len(data) >= 1
            first = data[0]
            assert isinstance(first["id"], int)
            assert isinstance(first["title"], str)
            assert isinstance(first["summary"], str)
            assert isinstance(first["source"], str)
            assert isinstance(first["timestamp"], str)

            # Close the stream cleanly
            websocket.send_json({"id": "1", "type": "complete"})
