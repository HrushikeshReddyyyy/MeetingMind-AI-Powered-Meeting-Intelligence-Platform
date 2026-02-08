import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
import enum

from app.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class MeetingStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    RECORDING = "recording"
    TRANSCRIBING = "transcribing"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ActionItemPriority(str, enum.Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ActionItemStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"


class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String(500), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    duration_minutes = Column(Integer, nullable=True)
    participants = Column(Text, nullable=True)  # JSON string of participant list
    status = Column(SAEnum(MeetingStatus), default=MeetingStatus.SCHEDULED)
    otter_meeting_id = Column(String(255), nullable=True)

    # Content
    transcript = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    key_decisions = Column(Text, nullable=True)  # JSON string

    # Integration tracking
    notion_page_id = Column(String(255), nullable=True)
    synced_to_notion = Column(Boolean, default=False)
    zapier_notified = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    action_items = relationship("ActionItem", back_populates="meeting", cascade="all, delete-orphan")
    analytics = relationship("MeetingAnalytics", back_populates="meeting", uselist=False, cascade="all, delete-orphan")


class ActionItem(Base):
    __tablename__ = "action_items"

    id = Column(String, primary_key=True, default=generate_uuid)
    meeting_id = Column(String, ForeignKey("meetings.id"), nullable=False)
    description = Column(Text, nullable=False)
    assignee = Column(String(255), nullable=True)
    due_date = Column(DateTime, nullable=True)
    priority = Column(SAEnum(ActionItemPriority), default=ActionItemPriority.MEDIUM)
    status = Column(SAEnum(ActionItemStatus), default=ActionItemStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    meeting = relationship("Meeting", back_populates="action_items")


class MeetingAnalytics(Base):
    __tablename__ = "meeting_analytics"

    id = Column(String, primary_key=True, default=generate_uuid)
    meeting_id = Column(String, ForeignKey("meetings.id"), nullable=False, unique=True)
    word_count = Column(Integer, default=0)
    speaker_count = Column(Integer, default=0)
    sentiment_score = Column(String(50), nullable=True)  # positive/neutral/negative
    topic_tags = Column(Text, nullable=True)  # JSON string of topics
    engagement_score = Column(Integer, nullable=True)  # 1-100
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    meeting = relationship("Meeting", back_populates="analytics")


class IntegrationConfig(Base):
    __tablename__ = "integration_configs"

    id = Column(String, primary_key=True, default=generate_uuid)
    service_name = Column(String(100), nullable=False, unique=True)  # otter, notion, zapier, openai
    is_enabled = Column(Boolean, default=False)
    config_data = Column(Text, nullable=True)  # JSON string of config
    last_sync = Column(DateTime, nullable=True)
    status = Column(String(50), default="disconnected")  # connected/disconnected/error
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
