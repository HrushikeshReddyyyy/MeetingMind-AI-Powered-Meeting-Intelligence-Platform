"""
Notion Integration Service for MeetingMind.
Manages meeting database templates and syncs meeting data to Notion.
"""
import json
import logging
from typing import Optional
from datetime import datetime

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class NotionService:
    """Handles integration with Notion for meeting documentation storage."""

    BASE_URL = "https://api.notion.com/v1"
    NOTION_VERSION = "2022-06-28"

    def __init__(self):
        self.api_key = settings.notion_api_key
        self.database_id = settings.notion_database_id

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and self.database_id)

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": self.NOTION_VERSION,
        }

    async def check_connection(self) -> dict:
        if not self.is_configured:
            return {"status": "disconnected", "message": "API key or database ID not configured"}

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.BASE_URL}/databases/{self.database_id}",
                    headers=self._headers(),
                )
                if response.status_code == 200:
                    return {"status": "connected", "message": "Successfully connected to Notion"}
                else:
                    return {"status": "error", "message": f"Connection failed: {response.status_code}"}
        except Exception as e:
            return {"status": "error", "message": f"Connection error: {str(e)}"}

    async def create_meeting_page(
        self,
        title: str,
        date: Optional[datetime],
        summary: str,
        action_items: list[dict],
        key_decisions: list[str],
        participants: Optional[list[str]] = None,
    ) -> Optional[str]:
        if not self.is_configured:
            logger.warning("Notion not configured, skipping page creation")
            return None

        # Build page properties
        properties = {
            "Name": {"title": [{"text": {"content": title}}]},
            "Status": {"select": {"name": "Completed"}},
        }

        if date:
            properties["Date"] = {"date": {"start": date.isoformat()}}

        if participants:
            properties["Participants"] = {
                "rich_text": [{"text": {"content": ", ".join(participants)}}]
            }

        # Build page content blocks
        children = []

        # Summary section
        children.append(self._heading_block("Meeting Summary"))
        children.append(self._paragraph_block(summary))

        # Key Decisions section
        if key_decisions:
            children.append(self._heading_block("Key Decisions"))
            for decision in key_decisions:
                children.append(self._bulleted_list_block(decision))

        # Action Items section
        if action_items:
            children.append(self._heading_block("Action Items"))
            for item in action_items:
                assignee = item.get("assignee", "Unassigned")
                priority = item.get("priority", "medium")
                text = f"[{priority.upper()}] {item['description']} - Assigned to: {assignee}"
                children.append(self._to_do_block(text))

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.BASE_URL}/pages",
                    headers=self._headers(),
                    json={
                        "parent": {"database_id": self.database_id},
                        "properties": properties,
                        "children": children[:100],  # Notion limit
                    },
                )
                if response.status_code == 200:
                    data = response.json()
                    page_id = data["id"]
                    logger.info(f"Created Notion page: {page_id}")
                    return page_id
                else:
                    logger.error(f"Failed to create Notion page: {response.status_code} - {response.text}")
                    return None
        except Exception as e:
            logger.error(f"Error creating Notion page: {e}")
            return None

    async def update_meeting_page(self, page_id: str, updates: dict) -> bool:
        if not self.is_configured:
            return False

        try:
            properties = {}
            if "status" in updates:
                properties["Status"] = {"select": {"name": updates["status"]}}

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.patch(
                    f"{self.BASE_URL}/pages/{page_id}",
                    headers=self._headers(),
                    json={"properties": properties},
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Error updating Notion page: {e}")
            return False

    def _heading_block(self, text: str) -> dict:
        return {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": text}}]
            },
        }

    def _paragraph_block(self, text: str) -> dict:
        # Notion blocks have a 2000 char limit for rich text
        truncated = text[:2000] if len(text) > 2000 else text
        return {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": truncated}}]
            },
        }

    def _bulleted_list_block(self, text: str) -> dict:
        return {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [{"type": "text", "text": {"content": text}}]
            },
        }

    def _to_do_block(self, text: str) -> dict:
        return {
            "object": "block",
            "type": "to_do",
            "to_do": {
                "rich_text": [{"type": "text", "text": {"content": text}}],
                "checked": False,
            },
        }


notion_service = NotionService()
