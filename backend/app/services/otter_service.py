"""
Otter.ai Integration Service for MeetingMind.
Handles fetching transcriptions from Otter.ai meetings.
"""
import logging
from typing import Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class OtterService:
    """Handles integration with Otter.ai for meeting transcription."""

    BASE_URL = "https://otter.ai/forward/api/v1"

    def __init__(self):
        self.email = settings.otter_email
        self.password = settings.otter_password
        self._token: Optional[str] = None

    @property
    def is_configured(self) -> bool:
        return bool(self.email and self.password)

    async def authenticate(self) -> bool:
        if not self.is_configured:
            logger.warning("Otter.ai credentials not configured")
            return False

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.BASE_URL}/login",
                    json={"email": self.email, "password": self.password},
                )
                if response.status_code == 200:
                    data = response.json()
                    self._token = data.get("token")
                    logger.info("Successfully authenticated with Otter.ai")
                    return True
                else:
                    logger.error(f"Otter.ai authentication failed: {response.status_code}")
                    return False
        except Exception as e:
            logger.error(f"Otter.ai authentication error: {e}")
            return False

    async def get_speeches(self, limit: int = 20) -> list[dict]:
        if not self._token:
            if not await self.authenticate():
                return []

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.BASE_URL}/speeches",
                    headers={"Authorization": f"Bearer {self._token}"},
                    params={"limit": limit},
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("speeches", [])
                else:
                    logger.error(f"Failed to fetch speeches: {response.status_code}")
                    return []
        except Exception as e:
            logger.error(f"Error fetching Otter.ai speeches: {e}")
            return []

    async def get_transcript(self, speech_id: str) -> Optional[str]:
        if not self._token:
            if not await self.authenticate():
                return None

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.BASE_URL}/speeches/{speech_id}",
                    headers={"Authorization": f"Bearer {self._token}"},
                )
                if response.status_code == 200:
                    data = response.json()
                    # Extract transcript text from Otter.ai response
                    transcripts = data.get("transcripts", [])
                    full_text = []
                    for t in transcripts:
                        speaker = t.get("speaker", "Unknown")
                        text = t.get("text", "")
                        full_text.append(f"{speaker}: {text}")
                    return "\n".join(full_text) if full_text else None
                else:
                    logger.error(f"Failed to fetch transcript: {response.status_code}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching Otter.ai transcript: {e}")
            return None

    async def check_connection(self) -> dict:
        if not self.is_configured:
            return {"status": "disconnected", "message": "Credentials not configured"}

        authenticated = await self.authenticate()
        if authenticated:
            return {"status": "connected", "message": "Successfully connected to Otter.ai"}
        return {"status": "error", "message": "Authentication failed"}


otter_service = OtterService()
