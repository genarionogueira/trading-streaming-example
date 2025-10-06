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
            # Depending on environment (Kafka running or not), we may receive:
            # - a data message (type 'next' with data.prices)
            # - a GraphQL error delivered as 'next' with data=None and errors
            # - a transport error message (type 'error')
            assert msg["type"] in {"next", "error"}
            if msg["type"] == "next":
                assert msg["id"] == "1"
                payload = msg.get("payload") or {}
                data_obj = payload.get("data")
                if data_obj is not None:
                    data = data_obj["prices"]
                    assert isinstance(data, list)
                    assert len(data) >= 1
                    first = data[0]
                    assert first["symbol"] == "AAPL"
                    assert isinstance(first["price"], (int, float))
                    websocket.send_json({"id": "1", "type": "complete"})
                else:
                    # Expect GraphQL errors present when Kafka is unavailable
                    errors = payload.get("errors") or []
                    combined = str(errors)
                    assert "Kafka" in combined or "kafka" in combined
                    # Server should follow with a 'complete'
                    websocket.receive_json()
            else:
                # Error path should indicate Kafka is unavailable
                payload = msg.get("payload") or {}
                text = str(payload)
                assert "Kafka" in text or "kafka" in text
