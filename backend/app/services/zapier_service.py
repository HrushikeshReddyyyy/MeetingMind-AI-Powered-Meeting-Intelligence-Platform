"""
Zapier Integration Service for MeetingMind.
Sends webhook notifications to Zapier for automated workflows:
- Meeting summary distribution
- Action item assignments
- Follow-up reminders
"""
import logging
from typing import Optional
from datetime import datetime

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class ZapierService:
    """Handles integration with Zapier for automated workflow triggers."""

    def __init__(self):
        self.webhook_summary = settings.zapier_webhook_summary
        self.webhook_action_items = settings.zapier_webhook_action_items
        self.webhook_followup = settings.zapier_webhook_followup

    @property
    def is_configured(self) -> bool:
        return bool(self.webhook_summary or self.webhook_action_items or self.webhook_followup)

    async def send_meeting_summary(
        self,
        meeting_id: str,
        title: str,
        date: Optional[datetime],
        summary: str,
        participants: Optional[list[str]] = None,
        key_decisions: Optional[list[str]] = None,
    ) -> bool:
        if not self.webhook_summary:
            logger.info("Zapier summary webhook not configured, skipping")
            return False

        payload = {
            "event": "meeting_summary",
            "meeting_id": meeting_id,
            "title": title,
            "date": date.isoformat() if date else None,
            "summary": summary,
            "participants": participants or [],
            "key_decisions": key_decisions or [],
            "timestamp": datetime.utcnow().isoformat(),
        }

        return await self._send_webhook(self.webhook_summary, payload)

    async def send_action_items(
        self,
        meeting_id: str,
        meeting_title: str,
        action_items: list[dict],
    ) -> bool:
        if not self.webhook_action_items:
            logger.info("Zapier action items webhook not configured, skipping")
            return False

        payload = {
            "event": "action_items_created",
            "meeting_id": meeting_id,
            "meeting_title": meeting_title,
            "action_items": [
                {
                    "description": item.get("description", ""),
                    "assignee": item.get("assignee", "Unassigned"),
                    "due_date": item.get("due_date"),
                    "priority": item.get("priority", "medium"),
                }
                for item in action_items
            ],
            "total_items": len(action_items),
            "timestamp": datetime.utcnow().isoformat(),
        }

        return await self._send_webhook(self.webhook_action_items, payload)

    async def send_followup_reminder(
        self,
        meeting_id: str,
        meeting_title: str,
        overdue_items: list[dict],
    ) -> bool:
        if not self.webhook_followup:
            logger.info("Zapier follow-up webhook not configured, skipping")
            return False

        payload = {
            "event": "followup_reminder",
            "meeting_id": meeting_id,
            "meeting_title": meeting_title,
            "overdue_items": overdue_items,
            "total_overdue": len(overdue_items),
            "timestamp": datetime.utcnow().isoformat(),
        }

        return await self._send_webhook(self.webhook_followup, payload)

    async def check_connection(self) -> dict:
        if not self.is_configured:
            return {"status": "disconnected", "message": "No webhook URLs configured"}

        # Test with a ping payload
        test_payload = {"event": "connection_test", "timestamp": datetime.utcnow().isoformat()}
        webhook = self.webhook_summary or self.webhook_action_items or self.webhook_followup
        success = await self._send_webhook(webhook, test_payload)

        if success:
            return {"status": "connected", "message": "Webhook connection successful"}
        return {"status": "error", "message": "Webhook test failed"}

    async def _send_webhook(self, url: str, payload: dict) -> bool:
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(url, json=payload)
                if response.status_code in (200, 201):
                    logger.info(f"Zapier webhook sent successfully: {payload.get('event')}")
                    return True
                else:
                    logger.error(f"Zapier webhook failed: {response.status_code}")
                    return False
        except Exception as e:
            logger.error(f"Zapier webhook error: {e}")
            return False


zapier_service = ZapierService()
