import pytest
from app.services.ai_engine import AIEngine


@pytest.fixture
def engine():
    return AIEngine()


def test_fallback_summary(engine):
    transcript = "Alice: Let's discuss Q4 goals.\nBob: We need to increase revenue by 20%.\nAlice: Agreed. Let's also focus on customer retention."
    result = engine._fallback_summary(transcript)
    assert len(result) > 0
    assert "words" in result


def test_fallback_action_items(engine):
    transcript = (
        "We need to prepare the quarterly report. "
        "Bob should follow up with the client by Friday. "
        "Alice will complete the design review."
    )
    items = engine._fallback_action_items(transcript)
    assert len(items) > 0
    assert all("description" in item for item in items)
    assert all("priority" in item for item in items)


def test_fallback_action_items_empty(engine):
    transcript = "Hello world. Nice weather today."
    items = engine._fallback_action_items(transcript)
    assert isinstance(items, list)


def test_fallback_key_decisions(engine):
    transcript = (
        "We decided to go with vendor A for the cloud migration. "
        "The team agreed to postpone the launch by two weeks. "
        "Nothing else was discussed."
    )
    decisions = engine._fallback_key_decisions(transcript)
    assert len(decisions) > 0


def test_fallback_analytics(engine):
    transcript = "Alice: Hello everyone.\nBob: Hi Alice.\nCharlie: Let's begin."
    analytics = engine._fallback_analytics(transcript)
    assert "sentiment_score" in analytics
    assert "topic_tags" in analytics
    assert "engagement_score" in analytics
    assert "speaker_count" in analytics
    assert analytics["speaker_count"] >= 1


def test_parse_due_date_hint_tomorrow(engine):
    result = engine._parse_due_date_hint("tomorrow")
    assert result is not None


def test_parse_due_date_hint_next_week(engine):
    result = engine._parse_due_date_hint("next week")
    assert result is not None


def test_parse_due_date_hint_unknown(engine):
    result = engine._parse_due_date_hint("sometime later")
    assert result is None
