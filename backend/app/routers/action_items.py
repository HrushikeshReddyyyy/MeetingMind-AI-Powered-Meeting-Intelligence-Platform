"""
Action Item API Routes for MeetingMind.
Manages action items extracted from meetings.
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.database import get_db
from app.models import ActionItem, ActionItemStatus, ActionItemPriority
from app.schemas import ActionItemCreate, ActionItemUpdate, ActionItemResponse

router = APIRouter(prefix="/api/action-items", tags=["action-items"])


@router.get("", response_model=list[ActionItemResponse])
async def list_action_items(
    meeting_id: Optional[str] = None,
    status: Optional[ActionItemStatus] = None,
    priority: Optional[ActionItemPriority] = None,
    assignee: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List action items with optional filtering."""
    query = select(ActionItem).order_by(desc(ActionItem.created_at))

    if meeting_id:
        query = query.where(ActionItem.meeting_id == meeting_id)
    if status:
        query = query.where(ActionItem.status == status)
    if priority:
        query = query.where(ActionItem.priority == priority)
    if assignee:
        query = query.where(ActionItem.assignee.ilike(f"%{assignee}%"))

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    items = result.scalars().all()

    return items


@router.post("", response_model=ActionItemResponse, status_code=201)
async def create_action_item(
    item_data: ActionItemCreate,
    meeting_id: str = Query(..., description="Meeting ID to associate this action item with"),
    db: AsyncSession = Depends(get_db),
):
    """Create a new action item for a meeting."""
    item = ActionItem(
        meeting_id=meeting_id,
        description=item_data.description,
        assignee=item_data.assignee,
        due_date=item_data.due_date,
        priority=item_data.priority,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.get("/{item_id}", response_model=ActionItemResponse)
async def get_action_item(item_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific action item."""
    result = await db.execute(select(ActionItem).where(ActionItem.id == item_id))
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Action item not found")

    return item


@router.put("/{item_id}", response_model=ActionItemResponse)
async def update_action_item(
    item_id: str,
    item_data: ActionItemUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an action item."""
    result = await db.execute(select(ActionItem).where(ActionItem.id == item_id))
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Action item not found")

    update_dict = item_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(item, key, value)

    item.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=204)
async def delete_action_item(item_id: str, db: AsyncSession = Depends(get_db)):
    """Delete an action item."""
    result = await db.execute(select(ActionItem).where(ActionItem.id == item_id))
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Action item not found")

    await db.delete(item)
    await db.commit()
