"""
Meeting API Routes for MeetingMind.
Handles CRUD operations and meeting processing pipeline.
"""
import json
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Meeting, ActionItem, MeetingStatus
from app.schemas import (
    MeetingCreate, MeetingUpdate, MeetingResponse, MeetingListResponse,
    TranscriptUpload,
)
from app.services.meeting_processor import meeting_processor

router = APIRouter(prefix="/api/meetings", tags=["meetings"])


async def _get_meeting_with_relations(db: AsyncSession, meeting_id: str) -> Meeting | None:
    """Load a meeting with all relationships eagerly loaded."""
    result = await db.execute(
        select(Meeting)
        .options(selectinload(Meeting.action_items), selectinload(Meeting.analytics))
        .where(Meeting.id == meeting_id)
    )
    return result.scalar_one_or_none()


@router.get("", response_model=list[MeetingListResponse])
async def list_meetings(
    status: Optional[MeetingStatus] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List all meetings with optional filtering."""
    query = (
        select(Meeting)
        .options(selectinload(Meeting.action_items))
        .order_by(desc(Meeting.created_at))
    )

    if status:
        query = query.where(Meeting.status == status)
    if search:
        query = query.where(Meeting.title.ilike(f"%{search}%"))

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    meetings = result.scalars().unique().all()

    response = []
    for m in meetings:
        response.append(MeetingListResponse(
            id=m.id,
            title=m.title,
            date=m.date,
            duration_minutes=m.duration_minutes,
            status=m.status,
            participants=json.loads(m.participants) if m.participants else None,
            action_item_count=len(m.action_items) if m.action_items else 0,
            synced_to_notion=m.synced_to_notion,
            created_at=m.created_at,
        ))

    return response


@router.post("", response_model=MeetingResponse, status_code=201)
async def create_meeting(
    meeting_data: MeetingCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new meeting."""
    meeting = Meeting(
        title=meeting_data.title,
        date=meeting_data.date or datetime.utcnow(),
        duration_minutes=meeting_data.duration_minutes,
        participants=json.dumps(meeting_data.participants) if meeting_data.participants else None,
    )
    db.add(meeting)
    await db.commit()

    meeting = await _get_meeting_with_relations(db, meeting.id)
    return _meeting_to_response(meeting)


@router.get("/{meeting_id}", response_model=MeetingResponse)
async def get_meeting(meeting_id: str, db: AsyncSession = Depends(get_db)):
    """Get a meeting by ID with all details."""
    meeting = await _get_meeting_with_relations(db, meeting_id)

    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    return _meeting_to_response(meeting)


@router.put("/{meeting_id}", response_model=MeetingResponse)
async def update_meeting(
    meeting_id: str,
    meeting_data: MeetingUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a meeting's details."""
    result = await db.execute(select(Meeting).where(Meeting.id == meeting_id))
    meeting = result.scalar_one_or_none()

    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    update_dict = meeting_data.model_dump(exclude_unset=True)
    if "participants" in update_dict and update_dict["participants"] is not None:
        update_dict["participants"] = json.dumps(update_dict["participants"])

    for key, value in update_dict.items():
        setattr(meeting, key, value)

    meeting.updated_at = datetime.utcnow()
    await db.commit()

    meeting = await _get_meeting_with_relations(db, meeting_id)
    return _meeting_to_response(meeting)


@router.delete("/{meeting_id}", status_code=204)
async def delete_meeting(meeting_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a meeting and all associated data."""
    meeting = await _get_meeting_with_relations(db, meeting_id)

    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    await db.delete(meeting)
    await db.commit()


@router.post("/{meeting_id}/transcript", response_model=MeetingResponse)
async def upload_transcript(
    meeting_id: str,
    data: TranscriptUpload,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Upload a transcript for a meeting and trigger AI processing."""
    result = await db.execute(select(Meeting).where(Meeting.id == meeting_id))
    meeting = result.scalar_one_or_none()

    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    meeting.transcript = data.transcript
    meeting.status = MeetingStatus.TRANSCRIBING
    meeting.updated_at = datetime.utcnow()
    await db.commit()

    # Process meeting in background
    background_tasks.add_task(_process_meeting_background, meeting_id)

    meeting = await _get_meeting_with_relations(db, meeting_id)
    return _meeting_to_response(meeting)


@router.post("/{meeting_id}/process", response_model=MeetingResponse)
async def process_meeting(
    meeting_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Manually trigger processing for a meeting with an existing transcript."""
    result = await db.execute(select(Meeting).where(Meeting.id == meeting_id))
    meeting = result.scalar_one_or_none()

    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    if not meeting.transcript:
        raise HTTPException(status_code=400, detail="Meeting has no transcript to process")

    background_tasks.add_task(_process_meeting_background, meeting_id)

    meeting = await _get_meeting_with_relations(db, meeting_id)
    return _meeting_to_response(meeting)


async def _process_meeting_background(meeting_id: str):
    """Background task for meeting processing."""
    from app.database import async_session
    async with async_session() as db:
        await meeting_processor.process_meeting(meeting_id, db)


def _meeting_to_response(meeting: Meeting) -> MeetingResponse:
    """Convert a Meeting ORM object to a response schema."""
    action_items = meeting.action_items if meeting.action_items else []
    analytics = meeting.analytics if meeting.analytics else None

    return MeetingResponse(
        id=meeting.id,
        title=meeting.title,
        date=meeting.date,
        duration_minutes=meeting.duration_minutes,
        participants=json.loads(meeting.participants) if meeting.participants else None,
        status=meeting.status,
        transcript=meeting.transcript,
        summary=meeting.summary,
        key_decisions=json.loads(meeting.key_decisions) if meeting.key_decisions else None,
        notion_page_id=meeting.notion_page_id,
        synced_to_notion=meeting.synced_to_notion,
        zapier_notified=meeting.zapier_notified,
        created_at=meeting.created_at,
        updated_at=meeting.updated_at,
        action_items=[
            {
                "id": item.id,
                "meeting_id": item.meeting_id,
                "description": item.description,
                "assignee": item.assignee,
                "due_date": item.due_date,
                "priority": item.priority,
                "status": item.status,
                "created_at": item.created_at,
                "updated_at": item.updated_at,
            }
            for item in action_items
        ],
        analytics={
            "id": analytics.id,
            "meeting_id": analytics.meeting_id,
            "word_count": analytics.word_count,
            "speaker_count": analytics.speaker_count,
            "sentiment_score": analytics.sentiment_score,
            "topic_tags": json.loads(analytics.topic_tags) if analytics.topic_tags else None,
            "engagement_score": analytics.engagement_score,
        } if analytics else None,
    )
