import pytest
from httpx import AsyncClient, ASGITransport
from starlette.testclient import TestClient

from data_svc.server import app


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


def test_prices_subscription_streams_updates():
    subscription = {
        "id": "1",
        "type": "subscribe",
        "payload": {
            "query": (
                "subscription { prices(symbols: [\"AAPL\"], intervalSeconds: 0.05) { "
                "symbol price changePercent timestamp } }"
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
            data = msg["payload"]["data"]["prices"]
            assert isinstance(data, list)
            assert len(data) >= 1
            first = data[0]
            assert first["symbol"] == "AAPL"
            assert isinstance(first["price"], (int, float))

            # Close the stream cleanly
            websocket.send_json({"id": "1", "type": "complete"})
