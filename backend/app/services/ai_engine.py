"""
AI Processing Engine for MeetingMind.
Uses OpenAI API to generate meeting summaries, extract action items,
identify key decisions, and analyze meeting sentiment/topics.
"""
import json
import logging
from typing import Optional
from datetime import datetime, timedelta

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

SUMMARY_PROMPT = """You are a meeting intelligence assistant. Analyze the following meeting transcript and provide a comprehensive summary.

The summary should include:
1. A concise overview (2-3 sentences)
2. Main topics discussed
3. Key points for each topic
4. Overall meeting outcome

Meeting Transcript:
{transcript}

Provide the summary in clear, professional language. Format with paragraphs for readability."""

ACTION_ITEMS_PROMPT = """You are a meeting intelligence assistant. Extract all action items from the following meeting transcript.

For each action item, identify:
- description: What needs to be done
- assignee: Who is responsible (use "Unassigned" if unclear)
- due_date_hint: Any mentioned deadline or timeframe (use null if none mentioned)
- priority: "high", "medium", or "low" based on urgency/importance

Meeting Transcript:
{transcript}

Respond with a JSON array of action items. Example:
[
  {{"description": "Prepare Q4 report", "assignee": "John", "due_date_hint": "next Friday", "priority": "high"}},
  {{"description": "Review design mockups", "assignee": "Unassigned", "due_date_hint": null, "priority": "medium"}}
]

Return ONLY the JSON array, no other text."""

KEY_DECISIONS_PROMPT = """You are a meeting intelligence assistant. Extract all key decisions made during the following meeting.

Meeting Transcript:
{transcript}

List each decision as a clear, concise statement. Respond with a JSON array of strings.
Example: ["Approved the Q4 budget of $50,000", "Decided to postpone the product launch to March"]

Return ONLY the JSON array, no other text."""

ANALYTICS_PROMPT = """You are a meeting analytics assistant. Analyze the following meeting transcript and provide metrics.

Meeting Transcript:
{transcript}

Respond with a JSON object containing:
- sentiment_score: "positive", "neutral", or "negative" (overall meeting tone)
- topic_tags: array of 3-5 topic tags that describe the meeting content
- engagement_score: 1-100 rating of how engaged/productive the meeting was
- speaker_count: estimated number of distinct speakers

Return ONLY the JSON object, no other text."""


class AIEngine:
    """Handles all AI-powered processing of meeting transcripts."""

    def __init__(self):
        self.api_key = settings.openai_api_key
        self.base_url = "https://api.openai.com/v1"
        self.model = "gpt-3.5-turbo"

    async def _call_openai(self, prompt: str) -> Optional[str]:
        if not self.api_key:
            logger.warning("OpenAI API key not configured, using fallback processing")
            return None

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.3,
                        "max_tokens": 2000,
                    },
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            return None

    async def generate_summary(self, transcript: str) -> str:
        result = await self._call_openai(SUMMARY_PROMPT.format(transcript=transcript))
        if result:
            return result
        return self._fallback_summary(transcript)

    async def extract_action_items(self, transcript: str) -> list[dict]:
        result = await self._call_openai(ACTION_ITEMS_PROMPT.format(transcript=transcript))
        if result:
            try:
                items = json.loads(result)
                return self._normalize_action_items(items)
            except json.JSONDecodeError:
                logger.error("Failed to parse action items JSON from AI response")
        return self._fallback_action_items(transcript)

    async def extract_key_decisions(self, transcript: str) -> list[str]:
        result = await self._call_openai(KEY_DECISIONS_PROMPT.format(transcript=transcript))
        if result:
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                logger.error("Failed to parse key decisions JSON from AI response")
        return self._fallback_key_decisions(transcript)

    async def analyze_meeting(self, transcript: str) -> dict:
        result = await self._call_openai(ANALYTICS_PROMPT.format(transcript=transcript))
        if result:
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                logger.error("Failed to parse analytics JSON from AI response")
        return self._fallback_analytics(transcript)

    def _normalize_action_items(self, items: list[dict]) -> list[dict]:
        normalized = []
        for item in items:
            due_date = None
            hint = item.get("due_date_hint")
            if hint:
                due_date = self._parse_due_date_hint(hint)

            normalized.append({
                "description": item.get("description", ""),
                "assignee": item.get("assignee", "Unassigned"),
                "due_date": due_date,
                "priority": item.get("priority", "medium"),
            })
        return normalized

    def _parse_due_date_hint(self, hint: str) -> Optional[str]:
        now = datetime.utcnow()
        hint_lower = hint.lower()

        if "tomorrow" in hint_lower:
            return (now + timedelta(days=1)).isoformat()
        elif "next week" in hint_lower:
            return (now + timedelta(weeks=1)).isoformat()
        elif "next month" in hint_lower:
            return (now + timedelta(days=30)).isoformat()
        elif "friday" in hint_lower:
            days_until_friday = (4 - now.weekday()) % 7
            if days_until_friday == 0:
                days_until_friday = 7
            return (now + timedelta(days=days_until_friday)).isoformat()
        elif "end of week" in hint_lower:
            days_until_friday = (4 - now.weekday()) % 7
            return (now + timedelta(days=days_until_friday)).isoformat()
        return None

    # --- Fallback methods when OpenAI is not available ---

    def _fallback_summary(self, transcript: str) -> str:
        sentences = [s.strip() for s in transcript.replace("\n", ". ").split(".") if s.strip()]
        word_count = len(transcript.split())

        summary_parts = [
            f"Meeting transcript contains {word_count} words across approximately {len(sentences)} statements.",
            "",
            "Key Points:",
        ]

        for i, sentence in enumerate(sentences[:10]):
            if len(sentence) > 20:
                summary_parts.append(f"- {sentence}")

        if len(sentences) > 10:
            summary_parts.append(f"\n... and {len(sentences) - 10} additional points discussed.")

        return "\n".join(summary_parts)

    def _fallback_action_items(self, transcript: str) -> list[dict]:
        action_keywords = ["need to", "should", "will", "must", "action", "todo",
                          "follow up", "assign", "deadline", "by next", "complete"]
        items = []
        sentences = transcript.split(".")

        for sentence in sentences:
            sentence = sentence.strip()
            if any(keyword in sentence.lower() for keyword in action_keywords) and len(sentence) > 15:
                items.append({
                    "description": sentence.strip(),
                    "assignee": "Unassigned",
                    "due_date": None,
                    "priority": "medium",
                })

        return items[:10]  # Limit to 10 action items

    def _fallback_key_decisions(self, transcript: str) -> list[str]:
        decision_keywords = ["decided", "agreed", "approved", "confirmed", "resolved",
                           "conclusion", "final", "go with", "chosen"]
        decisions = []
        sentences = transcript.split(".")

        for sentence in sentences:
            sentence = sentence.strip()
            if any(keyword in sentence.lower() for keyword in decision_keywords) and len(sentence) > 15:
                decisions.append(sentence)

        return decisions[:5]

    def _fallback_analytics(self, transcript: str) -> dict:
        words = transcript.split()
        word_count = len(words)
        lines = [l for l in transcript.split("\n") if l.strip()]

        # Estimate speakers by looking for name patterns (e.g., "Name:" or "Name -")
        speakers = set()
        for line in lines:
            if ":" in line:
                potential_speaker = line.split(":")[0].strip()
                if len(potential_speaker) < 30 and potential_speaker:
                    speakers.add(potential_speaker)

        return {
            "sentiment_score": "neutral",
            "topic_tags": ["general discussion"],
            "engagement_score": min(70, max(30, word_count // 10)),
            "speaker_count": max(1, len(speakers)),
        }


ai_engine = AIEngine()
