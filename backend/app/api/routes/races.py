"""
Races and Sessions API endpoints.
"""

import json
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.f1 import (
    Season, RaceEvent, RaceSession, SessionResult, LapData, TelemetryFrame
)
from app.schemas.f1 import (
    EventDetail, SessionDetail, SessionWithTrack, LapDataSchema, TelemetryFrameSchema
)
from app.services.f1_data import fetch_session_data

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/races", tags=["races"])


@router.get("/{year}/{round}", response_model=EventDetail)
async def get_event(year: int, round: int, db: AsyncSession = Depends(get_db)):
    """Get event details with all sessions."""
    query = (
        select(RaceEvent)
        .join(Season)
        .where(Season.year == year, RaceEvent.round_number == round)
        .options(selectinload(RaceEvent.sessions))
    )
    result = await db.execute(query)
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(
            status_code=404, 
            detail=f"Event not found: {year} Round {round}"
        )
    
    return event


@router.get("/{year}/{round}/{session_type}", response_model=SessionWithTrack)
async def get_session(
    year: int, 
    round: int, 
    session_type: str,
    db: AsyncSession = Depends(get_db)
):
    """Get session details with results and track layout."""
    query = (
        select(RaceSession)
        .join(RaceEvent)
        .join(Season)
        .where(
            Season.year == year,
            RaceEvent.round_number == round,
            RaceSession.session_type == session_type.upper()
        )
        .options(
            selectinload(RaceSession.results)
            .selectinload(SessionResult.driver),
            selectinload(RaceSession.results)
            .selectinload(SessionResult.team),
            selectinload(RaceSession.event)
        )
    )
    result = await db.execute(query)
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=404,
            detail=f"Session not found: {year} R{round} {session_type}"
        )
    
    # Parse track layout JSON
    track_layout = None
    if session.event and session.event.track_layout_json:
        try:
            track_layout = json.loads(session.event.track_layout_json)
        except json.JSONDecodeError:
            pass
    
    return SessionWithTrack(
        id=session.id,
        session_type=session.session_type,
        session_date=session.session_date,
        total_laps=session.total_laps,
        data_fetched=session.data_fetched,
        has_telemetry=session.has_telemetry,
        weather=session.weather,
        air_temp=session.air_temp,
        track_temp=session.track_temp,
        results=session.results,
        track_layout=track_layout,
        event_name=session.event.event_name if session.event else "",
        circuit_name=session.event.circuit_name if session.event else None,
    )


@router.get("/{year}/{round}/{session_type}/laps", response_model=List[LapDataSchema])
async def get_laps(
    year: int,
    round: int,
    session_type: str,
    driver_id: Optional[int] = Query(None, description="Filter by driver ID"),
    lap_number: Optional[int] = Query(None, description="Filter by lap number"),
    db: AsyncSession = Depends(get_db)
):
    """Get lap data for a session."""
    # First get the session
    session_query = (
        select(RaceSession)
        .join(RaceEvent)
        .join(Season)
        .where(
            Season.year == year,
            RaceEvent.round_number == round,
            RaceSession.session_type == session_type.upper()
        )
    )
    result = await db.execute(session_query)
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Build lap query
    query = select(LapData).where(LapData.session_id == session.id)
    
    if driver_id:
        query = query.where(LapData.driver_id == driver_id)
    if lap_number:
        query = query.where(LapData.lap_number == lap_number)
    
    query = query.order_by(LapData.lap_number, LapData.driver_id)
    
    result = await db.execute(query)
    laps = result.scalars().all()
    return laps


@router.get("/{year}/{round}/{session_type}/telemetry")
async def get_telemetry(
    year: int,
    round: int,
    session_type: str,
    driver_id: int = Query(..., description="Driver ID"),
    lap_number: Optional[int] = Query(None, description="Specific lap number"),
    db: AsyncSession = Depends(get_db)
):
    """Get telemetry data for a driver in a session."""
    # First get the session
    session_query = (
        select(RaceSession)
        .join(RaceEvent)
        .join(Season)
        .where(
            Season.year == year,
            RaceEvent.round_number == round,
            RaceSession.session_type == session_type.upper()
        )
    )
    result = await db.execute(session_query)
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Build telemetry query
    query = (
        select(TelemetryFrame)
        .where(
            TelemetryFrame.session_id == session.id,
            TelemetryFrame.driver_id == driver_id
        )
    )
    
    if lap_number:
        query = query.where(TelemetryFrame.lap_number == lap_number)
    
    query = query.order_by(TelemetryFrame.lap_number)
    
    result = await db.execute(query)
    frames = result.scalars().all()
    
    # Parse JSON arrays
    telemetry_data = []
    for frame in frames:
        data = {
            "lap_number": frame.lap_number,
            "driver_id": frame.driver_id,
            "sample_count": frame.sample_count,
        }
        
        # Parse each JSON field
        for field in ['timestamps_ms', 'speed_kmh', 'throttle_pct', 'brake_pct', 
                      'rpm', 'gear', 'drs', 'pos_x', 'pos_y']:
            value = getattr(frame, field)
            if value:
                try:
                    data[field] = json.loads(value)
                except json.JSONDecodeError:
                    data[field] = None
            else:
                data[field] = None
        
        telemetry_data.append(data)
    
    return telemetry_data


@router.post("/{year}/{round}/{session_type}/fetch")
async def fetch_session(
    year: int,
    round: int,
    session_type: str,
    db: AsyncSession = Depends(get_db)
):
    """Fetch and populate session data from FastF1.
    
    This endpoint fetches complete session data including:
    - Session metadata
    - Driver results
    - Lap data
    - Telemetry (if available)
    
    Note: This can take several minutes for sessions with telemetry.
    """
    try:
        logger.info(f"Fetching {year} R{round} {session_type}...")
        session = await fetch_session_data(db, year, round, session_type)
        return {
            "message": f"Successfully fetched {session_type} session",
            "session_id": session.id,
            "total_laps": session.total_laps,
            "has_telemetry": session.has_telemetry
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to fetch session: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch session data: {str(e)}"
        )
