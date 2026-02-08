import pytest


@pytest.mark.asyncio
async def test_create_action_item(client):
    # First create a meeting
    meeting_resp = await client.post("/api/meetings", json={"title": "Action Item Test"})
    meeting_id = meeting_resp.json()["id"]

    response = await client.post(f"/api/action-items?meeting_id={meeting_id}", json={
        "description": "Prepare Q4 report",
        "assignee": "Alice",
        "priority": "high",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["description"] == "Prepare Q4 report"
    assert data["assignee"] == "Alice"
    assert data["priority"] == "high"
    assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_list_action_items(client):
    meeting_resp = await client.post("/api/meetings", json={"title": "AI Test Meeting"})
    meeting_id = meeting_resp.json()["id"]

    await client.post(f"/api/action-items?meeting_id={meeting_id}", json={
        "description": "Task 1",
    })
    await client.post(f"/api/action-items?meeting_id={meeting_id}", json={
        "description": "Task 2",
    })

    response = await client.get("/api/action-items")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_update_action_item_status(client):
    meeting_resp = await client.post("/api/meetings", json={"title": "Status Test"})
    meeting_id = meeting_resp.json()["id"]

    create_resp = await client.post(f"/api/action-items?meeting_id={meeting_id}", json={
        "description": "Complete testing",
    })
    item_id = create_resp.json()["id"]

    response = await client.put(f"/api/action-items/{item_id}", json={
        "status": "completed",
    })
    assert response.status_code == 200
    assert response.json()["status"] == "completed"


@pytest.mark.asyncio
async def test_delete_action_item(client):
    meeting_resp = await client.post("/api/meetings", json={"title": "Delete AI Test"})
    meeting_id = meeting_resp.json()["id"]

    create_resp = await client.post(f"/api/action-items?meeting_id={meeting_id}", json={
        "description": "To be deleted",
    })
    item_id = create_resp.json()["id"]

    response = await client.delete(f"/api/action-items/{item_id}")
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_filter_action_items_by_priority(client):
    meeting_resp = await client.post("/api/meetings", json={"title": "Priority Test"})
    meeting_id = meeting_resp.json()["id"]

    await client.post(f"/api/action-items?meeting_id={meeting_id}", json={
        "description": "High priority task",
        "priority": "high",
    })
    await client.post(f"/api/action-items?meeting_id={meeting_id}", json={
        "description": "Low priority task",
        "priority": "low",
    })

    response = await client.get("/api/action-items?priority=high")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["priority"] == "high"
