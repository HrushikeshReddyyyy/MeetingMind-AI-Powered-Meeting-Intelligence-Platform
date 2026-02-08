import pytest


@pytest.mark.asyncio
async def test_list_integrations(client):
    response = await client.get("/api/integrations")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 4
    service_names = [c["service_name"] for c in data]
    assert "otter" in service_names
    assert "notion" in service_names
    assert "zapier" in service_names
    assert "openai" in service_names


@pytest.mark.asyncio
async def test_get_integration(client):
    response = await client.get("/api/integrations/notion")
    assert response.status_code == 200
    data = response.json()
    assert data["service_name"] == "notion"
    assert data["is_enabled"] is False


@pytest.mark.asyncio
async def test_update_integration(client):
    response = await client.put("/api/integrations/notion", json={
        "is_enabled": True,
    })
    assert response.status_code == 200
    assert response.json()["is_enabled"] is True


@pytest.mark.asyncio
async def test_unknown_service(client):
    response = await client.get("/api/integrations/unknown")
    assert response.status_code == 404
