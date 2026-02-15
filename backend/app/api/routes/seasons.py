"""
Seasons API endpoints.
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.f1 import Season, RaceEvent
from app.schemas.f1 import SeasonSummary, SeasonDetail, EventSummary
from app.services.f1_data import fetch_season_schedule

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/seasons", tags=["seasons"])


@router.get("", response_model=List[SeasonSummary])
async def list_seasons(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """List all F1 seasons (1950-present)."""
    query = (
        select(Season)
        .order_by(Season.year.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    seasons = result.scalars().all()
    return seasons


@router.get("/{year}", response_model=SeasonDetail)
async def get_season(year: int, db: AsyncSession = Depends(get_db)):
    """Get a specific season with its events."""
    query = (
        select(Season)
        .where(Season.year == year)
        .options(selectinload(Season.events))
    )
    result = await db.execute(query)
    season = result.scalar_one_or_none()
    
    if not season:
        raise HTTPException(status_code=404, detail=f"Season {year} not found")
    
    return season


@router.get("/{year}/events", response_model=List[EventSummary])
async def list_events(year: int, db: AsyncSession = Depends(get_db)):
    """List all events for a season."""
    query = (
        select(RaceEvent)
        .join(Season)
        .where(Season.year == year)
        .order_by(RaceEvent.round_number)
    )
    result = await db.execute(query)
    events = result.scalars().all()
    return events


@router.post("/{year}/fetch")
async def fetch_season(
    year: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Fetch and populate season data from FastF1.
    
    This endpoint triggers a background task to fetch the season schedule
    and basic event information. For detailed session data, use the
    races endpoint.
    """
    # Check if season already exists
    query = select(Season).where(Season.year == year)
    result = await db.execute(query)
    existing_season = result.scalar_one_or_none()
    
    if existing_season and existing_season.data_fetched:
        return {
            "message": f"Season {year} already fetched",
            "season_id": existing_season.id,
            "total_rounds": existing_season.total_rounds
        }
    
    try:
        logger.info(f"Fetching season {year}...")
        season = await fetch_season_schedule(db, year)
        return {
            "message": f"Successfully fetched season {year}",
            "season_id": season.id,
            "total_rounds": season.total_rounds
        }
    except Exception as e:
        logger.error(f"Failed to fetch season {year}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch season data: {str(e)}"
        )
