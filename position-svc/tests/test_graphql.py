import pytest
from httpx import AsyncClient, ASGITransport

from position_svc.server import app


@pytest.mark.asyncio
async def test_positions_query_returns_list():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        query = """
        query {
          positions { id symbol quantity price }
        }
        """
        resp = await client.post("/graphql", json={"query": query})
        assert resp.status_code == 200
        payload = resp.json()
        assert "data" in payload
        positions = payload["data"]["positions"]
        assert isinstance(positions, list)
        assert len(positions) >= 2
        # basic shape checks
        first = positions[0]
        assert {"id", "symbol", "quantity", "price"}.issubset(first.keys())


@pytest.mark.asyncio
async def test_positions_query_contains_expected_items():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        query = """
        query {
          positions { id symbol quantity price }
        }
        """
        resp = await client.post("/graphql", json={"query": query})
        assert resp.status_code == 200
        positions = resp.json()["data"]["positions"]
        # Assert known fixtures exist
        assert any(p["symbol"] == "AAPL" and p["id"] == 1 for p in positions)
        assert any(p["symbol"] == "GOOG" and p["id"] == 2 for p in positions)
