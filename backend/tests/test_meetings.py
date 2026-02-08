import pytest


@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "MeetingMind API"


@pytest.mark.asyncio
async def test_create_meeting(client):
    response = await client.post("/api/meetings", json={
        "title": "Weekly Team Standup",
        "duration_minutes": 30,
        "participants": ["Alice", "Bob", "Charlie"],
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Weekly Team Standup"
    assert data["duration_minutes"] == 30
    assert data["participants"] == ["Alice", "Bob", "Charlie"]
    assert data["status"] == "scheduled"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_meetings(client):
    # Create two meetings
    await client.post("/api/meetings", json={"title": "Meeting 1"})
    await client.post("/api/meetings", json={"title": "Meeting 2"})

    response = await client.get("/api/meetings")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_get_meeting(client):
    # Create a meeting
    create_resp = await client.post("/api/meetings", json={"title": "Test Meeting"})
    meeting_id = create_resp.json()["id"]

    response = await client.get(f"/api/meetings/{meeting_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Test Meeting"


@pytest.mark.asyncio
async def test_get_meeting_not_found(client):
    response = await client.get("/api/meetings/nonexistent-id")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_meeting(client):
    create_resp = await client.post("/api/meetings", json={"title": "Original Title"})
    meeting_id = create_resp.json()["id"]

    response = await client.put(f"/api/meetings/{meeting_id}", json={
        "title": "Updated Title",
        "duration_minutes": 45,
    })
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"
    assert response.json()["duration_minutes"] == 45


@pytest.mark.asyncio
async def test_delete_meeting(client):
    create_resp = await client.post("/api/meetings", json={"title": "To Delete"})
    meeting_id = create_resp.json()["id"]

    response = await client.delete(f"/api/meetings/{meeting_id}")
    assert response.status_code == 204

    # Verify it's gone
    get_resp = await client.get(f"/api/meetings/{meeting_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_upload_transcript(client):
    create_resp = await client.post("/api/meetings", json={"title": "Transcript Test"})
    meeting_id = create_resp.json()["id"]

    response = await client.post(f"/api/meetings/{meeting_id}/transcript", json={
        "transcript": "Alice: Let's discuss the roadmap.\nBob: I agree we need to prioritize mobile."
    })
    assert response.status_code == 200
    # Status should change to transcribing (processing will happen in background)
    assert response.json()["status"] in ["transcribing", "processing"]


@pytest.mark.asyncio
async def test_filter_meetings_by_status(client):
    await client.post("/api/meetings", json={"title": "Scheduled Meeting"})

    response = await client.get("/api/meetings?status=scheduled")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert all(m["status"] == "scheduled" for m in data)


@pytest.mark.asyncio
async def test_search_meetings(client):
    await client.post("/api/meetings", json={"title": "Q4 Planning Session"})
    await client.post("/api/meetings", json={"title": "Daily Standup"})

    response = await client.get("/api/meetings?search=Q4")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert "Q4" in data[0]["title"]
