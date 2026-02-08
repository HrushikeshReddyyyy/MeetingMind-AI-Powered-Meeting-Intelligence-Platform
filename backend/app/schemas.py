from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models import MeetingStatus, ActionItemPriority, ActionItemStatus


# --- Meeting Schemas ---

class MeetingCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    date: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    participants: Optional[List[str]] = None


class MeetingUpdate(BaseModel):
    title: Optional[str] = None
    date: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    participants: Optional[List[str]] = None
    status: Optional[MeetingStatus] = None
    transcript: Optional[str] = None


class ActionItemResponse(BaseModel):
    id: str
    meeting_id: str
    description: str
    assignee: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: ActionItemPriority
    status: ActionItemStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class MeetingAnalyticsResponse(BaseModel):
    id: str
    meeting_id: str
    word_count: int
    speaker_count: int
    sentiment_score: Optional[str] = None
    topic_tags: Optional[List[str]] = None
    engagement_score: Optional[int] = None

    model_config = {"from_attributes": True}


class MeetingResponse(BaseModel):
    id: str
    title: str
    date: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    participants: Optional[List[str]] = None
    status: MeetingStatus
    transcript: Optional[str] = None
    summary: Optional[str] = None
    key_decisions: Optional[List[str]] = None
    notion_page_id: Optional[str] = None
    synced_to_notion: bool
    zapier_notified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    action_items: List[ActionItemResponse] = []
    analytics: Optional[MeetingAnalyticsResponse] = None

    model_config = {"from_attributes": True}


class MeetingListResponse(BaseModel):
    id: str
    title: str
    date: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    status: MeetingStatus
    participants: Optional[List[str]] = None
    action_item_count: int = 0
    synced_to_notion: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Action Item Schemas ---

class ActionItemCreate(BaseModel):
    description: str = Field(..., min_length=1)
    assignee: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: ActionItemPriority = ActionItemPriority.MEDIUM


class ActionItemUpdate(BaseModel):
    description: Optional[str] = None
    assignee: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[ActionItemPriority] = None
    status: Optional[ActionItemStatus] = None


# --- Integration Schemas ---

class IntegrationConfigResponse(BaseModel):
    id: str
    service_name: str
    is_enabled: bool
    status: str
    last_sync: Optional[datetime] = None

    model_config = {"from_attributes": True}


class IntegrationConfigUpdate(BaseModel):
    is_enabled: Optional[bool] = None
    config_data: Optional[dict] = None


# --- Analytics Schemas ---

class DashboardStats(BaseModel):
    total_meetings: int
    completed_meetings: int
    total_action_items: int
    pending_action_items: int
    completed_action_items: int
    overdue_action_items: int
    avg_meeting_duration: Optional[float] = None
    meetings_this_week: int
    action_completion_rate: float


class TranscriptUpload(BaseModel):
    transcript: str = Field(..., min_length=1)
