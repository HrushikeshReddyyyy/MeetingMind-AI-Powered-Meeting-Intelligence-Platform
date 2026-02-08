"""
Meeting Processor Service for MeetingMind.
Orchestrates the full meeting processing pipeline:
1. Receive/fetch transcript
2. Generate AI summary
3. Extract action items & key decisions
4. Run analytics
5. Sync to Notion
6. Trigger Zapier webhooks
"""
import json
import logging
from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import Meeting, ActionItem, MeetingAnalytics, MeetingStatus, ActionItemPriority
from app.services.ai_engine import ai_engine
from app.services.notion_service import notion_service
from app.services.zapier_service import zapier_service

logger = logging.getLogger(__name__)


class MeetingProcessor:
    """Orchestrates the complete meeting processing pipeline."""

    async def process_meeting(self, meeting_id: str, db: AsyncSession) -> bool:
        """Run the full processing pipeline for a meeting."""
        result = await db.execute(select(Meeting).where(Meeting.id == meeting_id))
        meeting = result.scalar_one_or_none()

        if not meeting:
            logger.error(f"Meeting {meeting_id} not found")
            return False

        if not meeting.transcript:
            logger.error(f"Meeting {meeting_id} has no transcript")
            return False

        try:
            # Update status to processing
            meeting.status = MeetingStatus.PROCESSING
            await db.commit()

            # Step 1: Generate AI summary
            logger.info(f"Generating summary for meeting {meeting_id}")
            summary = await ai_engine.generate_summary(meeting.transcript)
            meeting.summary = summary

            # Step 2: Extract key decisions
            logger.info(f"Extracting key decisions for meeting {meeting_id}")
            decisions = await ai_engine.extract_key_decisions(meeting.transcript)
            meeting.key_decisions = json.dumps(decisions)

            # Step 3: Extract action items
            logger.info(f"Extracting action items for meeting {meeting_id}")
            raw_items = await ai_engine.extract_action_items(meeting.transcript)
            action_items = []
            for item_data in raw_items:
                action_item = ActionItem(
                    meeting_id=meeting_id,
                    description=item_data["description"],
                    assignee=item_data.get("assignee", "Unassigned"),
                    due_date=datetime.fromisoformat(item_data["due_date"]) if item_data.get("due_date") else None,
                    priority=ActionItemPriority(item_data.get("priority", "medium")),
                )
                db.add(action_item)
                action_items.append(item_data)

            # Step 4: Run analytics
            logger.info(f"Analyzing meeting {meeting_id}")
            analytics_data = await ai_engine.analyze_meeting(meeting.transcript)
            analytics = MeetingAnalytics(
                meeting_id=meeting_id,
                word_count=len(meeting.transcript.split()),
                speaker_count=analytics_data.get("speaker_count", 1),
                sentiment_score=analytics_data.get("sentiment_score", "neutral"),
                topic_tags=json.dumps(analytics_data.get("topic_tags", [])),
                engagement_score=analytics_data.get("engagement_score"),
            )
            db.add(analytics)

            # Step 5: Sync to Notion
            participants = json.loads(meeting.participants) if meeting.participants else None
            notion_page_id = await notion_service.create_meeting_page(
                title=meeting.title,
                date=meeting.date,
                summary=summary,
                action_items=action_items,
                key_decisions=decisions,
                participants=participants,
            )
            if notion_page_id:
                meeting.notion_page_id = notion_page_id
                meeting.synced_to_notion = True

            # Step 6: Trigger Zapier webhooks
            summary_sent = await zapier_service.send_meeting_summary(
                meeting_id=meeting_id,
                title=meeting.title,
                date=meeting.date,
                summary=summary,
                participants=participants,
                key_decisions=decisions,
            )
            items_sent = await zapier_service.send_action_items(
                meeting_id=meeting_id,
                meeting_title=meeting.title,
                action_items=action_items,
            )
            if summary_sent or items_sent:
                meeting.zapier_notified = True

            # Mark as completed
            meeting.status = MeetingStatus.COMPLETED
            meeting.updated_at = datetime.utcnow()
            await db.commit()

            logger.info(f"Meeting {meeting_id} processed successfully")
            return True

        except Exception as e:
            logger.error(f"Error processing meeting {meeting_id}: {e}")
            meeting.status = MeetingStatus.FAILED
            await db.commit()
            return False


meeting_processor = MeetingProcessor()
