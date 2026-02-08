"""
Analytics API Routes for MeetingMind.
Provides dashboard statistics and meeting analytics data.
"""
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models import Meeting, ActionItem, MeetingStatus, ActionItemStatus
from app.schemas import DashboardStats

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    """Get aggregated dashboard statistics."""
    # Total meetings
    total_result = await db.execute(select(func.count()).select_from(Meeting))
    total_meetings = total_result.scalar() or 0

    # Completed meetings
    completed_result = await db.execute(
        select(func.count()).where(Meeting.status == MeetingStatus.COMPLETED)
    )
    completed_meetings = completed_result.scalar() or 0

    # Action item counts
    total_items_result = await db.execute(select(func.count()).select_from(ActionItem))
    total_action_items = total_items_result.scalar() or 0

    pending_result = await db.execute(
        select(func.count()).where(ActionItem.status == ActionItemStatus.PENDING)
    )
    pending_action_items = pending_result.scalar() or 0

    completed_items_result = await db.execute(
        select(func.count()).where(ActionItem.status == ActionItemStatus.COMPLETED)
    )
    completed_action_items = completed_items_result.scalar() or 0

    overdue_result = await db.execute(
        select(func.count()).where(ActionItem.status == ActionItemStatus.OVERDUE)
    )
    overdue_action_items = overdue_result.scalar() or 0

    # Average meeting duration
    avg_duration_result = await db.execute(
        select(func.avg(Meeting.duration_minutes)).where(Meeting.duration_minutes.isnot(None))
    )
    avg_meeting_duration = avg_duration_result.scalar()

    # Meetings this week
    week_start = datetime.utcnow() - timedelta(days=datetime.utcnow().weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    week_result = await db.execute(
        select(func.count()).where(Meeting.created_at >= week_start)
    )
    meetings_this_week = week_result.scalar() or 0

    # Action completion rate
    action_completion_rate = 0.0
    if total_action_items > 0:
        action_completion_rate = round((completed_action_items / total_action_items) * 100, 1)

    return DashboardStats(
        total_meetings=total_meetings,
        completed_meetings=completed_meetings,
        total_action_items=total_action_items,
        pending_action_items=pending_action_items,
        completed_action_items=completed_action_items,
        overdue_action_items=overdue_action_items,
        avg_meeting_duration=round(avg_meeting_duration, 1) if avg_meeting_duration else None,
        meetings_this_week=meetings_this_week,
        action_completion_rate=action_completion_rate,
    )


@router.get("/meetings-over-time")
async def meetings_over_time(
    days: int = 30,
    db: AsyncSession = Depends(get_db),
):
    """Get meeting count grouped by day for the specified period."""
    start_date = datetime.utcnow() - timedelta(days=days)

    result = await db.execute(
        select(
            func.date(Meeting.created_at).label("date"),
            func.count().label("count"),
        )
        .where(Meeting.created_at >= start_date)
        .group_by(func.date(Meeting.created_at))
        .order_by(func.date(Meeting.created_at))
    )

    data = [{"date": str(row.date), "count": row.count} for row in result]
    return data


@router.get("/action-item-summary")
async def action_item_summary(db: AsyncSession = Depends(get_db)):
    """Get action item breakdown by status and priority."""
    # By status
    status_result = await db.execute(
        select(
            ActionItem.status,
            func.count().label("count"),
        )
        .group_by(ActionItem.status)
    )
    by_status = {str(row.status.value): row.count for row in status_result}

    # By priority
    priority_result = await db.execute(
        select(
            ActionItem.priority,
            func.count().label("count"),
        )
        .group_by(ActionItem.priority)
    )
    by_priority = {str(row.priority.value): row.count for row in priority_result}

    return {"by_status": by_status, "by_priority": by_priority}
