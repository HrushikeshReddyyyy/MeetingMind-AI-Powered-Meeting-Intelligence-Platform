import pytest


@pytest.mark.asyncio
async def test_dashboard_stats_empty(client):
    response = await client.get("/api/analytics/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert data["total_meetings"] == 0
    assert data["total_action_items"] == 0
    assert data["action_completion_rate"] == 0.0


@pytest.mark.asyncio
async def test_dashboard_stats_with_data(client):
    # Create meetings
    await client.post("/api/meetings", json={"title": "Meeting 1"})
    await client.post("/api/meetings", json={"title": "Meeting 2"})

    response = await client.get("/api/analytics/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert data["total_meetings"] == 2
    assert data["meetings_this_week"] >= 0


@pytest.mark.asyncio
async def test_meetings_over_time(client):
    await client.post("/api/meetings", json={"title": "Timeline Test"})

    response = await client.get("/api/analytics/meetings-over-time?days=30")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_action_item_summary(client):
    response = await client.get("/api/analytics/action-item-summary")
    assert response.status_code == 200
    data = response.json()
    assert "by_status" in data
    assert "by_priority" in data
