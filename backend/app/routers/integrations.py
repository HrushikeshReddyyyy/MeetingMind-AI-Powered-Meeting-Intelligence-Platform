"""
Integration Configuration API Routes for MeetingMind.
Manages connections to Otter.ai, Notion, Zapier, and OpenAI.
"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import IntegrationConfig
from app.schemas import IntegrationConfigResponse, IntegrationConfigUpdate
from app.services.otter_service import otter_service
from app.services.notion_service import notion_service
from app.services.zapier_service import zapier_service
from app.config import settings

router = APIRouter(prefix="/api/integrations", tags=["integrations"])

SERVICES = ["otter", "notion", "zapier", "openai"]


@router.get("", response_model=list[IntegrationConfigResponse])
async def list_integrations(db: AsyncSession = Depends(get_db)):
    """List all integration configurations."""
    configs = []

    for service_name in SERVICES:
        result = await db.execute(
            select(IntegrationConfig).where(IntegrationConfig.service_name == service_name)
        )
        config = result.scalar_one_or_none()

        if not config:
            # Create default config
            config = IntegrationConfig(
                service_name=service_name,
                is_enabled=False,
                status="disconnected",
            )
            db.add(config)
            await db.commit()
            await db.refresh(config)

        configs.append(config)

    return configs


@router.get("/{service_name}", response_model=IntegrationConfigResponse)
async def get_integration(service_name: str, db: AsyncSession = Depends(get_db)):
    """Get a specific integration configuration."""
    if service_name not in SERVICES:
        raise HTTPException(status_code=404, detail=f"Unknown service: {service_name}")

    result = await db.execute(
        select(IntegrationConfig).where(IntegrationConfig.service_name == service_name)
    )
    config = result.scalar_one_or_none()

    if not config:
        config = IntegrationConfig(
            service_name=service_name,
            is_enabled=False,
            status="disconnected",
        )
        db.add(config)
        await db.commit()
        await db.refresh(config)

    return config


@router.put("/{service_name}", response_model=IntegrationConfigResponse)
async def update_integration(
    service_name: str,
    update: IntegrationConfigUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an integration configuration."""
    if service_name not in SERVICES:
        raise HTTPException(status_code=404, detail=f"Unknown service: {service_name}")

    result = await db.execute(
        select(IntegrationConfig).where(IntegrationConfig.service_name == service_name)
    )
    config = result.scalar_one_or_none()

    if not config:
        config = IntegrationConfig(service_name=service_name)
        db.add(config)

    if update.is_enabled is not None:
        config.is_enabled = update.is_enabled

    config.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(config)
    return config


@router.post("/{service_name}/test", response_model=dict)
async def test_integration(service_name: str, db: AsyncSession = Depends(get_db)):
    """Test the connection for a specific integration."""
    if service_name not in SERVICES:
        raise HTTPException(status_code=404, detail=f"Unknown service: {service_name}")

    if service_name == "otter":
        connection_result = await otter_service.check_connection()
    elif service_name == "notion":
        connection_result = await notion_service.check_connection()
    elif service_name == "zapier":
        connection_result = await zapier_service.check_connection()
    elif service_name == "openai":
        connection_result = _check_openai()
    else:
        connection_result = {"status": "error", "message": "Unknown service"}

    # Update config status
    result = await db.execute(
        select(IntegrationConfig).where(IntegrationConfig.service_name == service_name)
    )
    config = result.scalar_one_or_none()
    if config:
        config.status = connection_result["status"]
        config.last_sync = datetime.utcnow()
        await db.commit()

    return connection_result


def _check_openai() -> dict:
    if settings.openai_api_key:
        return {"status": "connected", "message": "API key configured"}
    return {"status": "disconnected", "message": "API key not configured"}
