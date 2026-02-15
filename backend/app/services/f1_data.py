"""
FastF1 data fetching and ingestion service.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Optional, List, Tuple

import fastf1
import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.f1 import (
    Season, RaceEvent, RaceSession, Driver, Team,
    SessionResult, LapData, TelemetryFrame
)

logger = logging.getLogger(__name__)
settings = get_settings()

# Configure FastF1 cache
fastf1.Cache.enable_cache(settings.fastf1_cache_dir)


async def fetch_season_schedule(db: AsyncSession, year: int) -> Season:
    """
    Fetch F1 season schedule and create/update season record.
    """
    logger.info(f"Fetching season schedule for {year}")
    
    # Get or create season
    query = select(Season).where(Season.year == year)
    result = await db.execute(query)
    season = result.scalar_one_or_none()
    
    if not season:
        season = Season(year=year)
        db.add(season)
    
    # Fetch schedule using FastF1
    try:
        schedule = await asyncio.to_thread(fastf1.get_event_schedule, year)
        season.total_rounds = len(schedule)
        
        # Process each event
        for idx, event in schedule.iterrows():
            await _process_event(db, season, event, idx + 1)
        
        season.data_fetched = True
        season.last_updated = datetime.utcnow()
        await db.commit()
        
        logger.info(f"Successfully fetched {len(schedule)} events for {year}")
        return season
        
    except Exception as e:
        logger.error(f"Failed to fetch season {year}: {e}")
        await db.rollback()
        raise


async def _process_event(
    db: AsyncSession,
    season: Season,
    event_data: pd.Series,
    round_number: int
) -> RaceEvent:
    """Process a single race event from FastF1 data."""
    
    # Check if event already exists
    query = select(RaceEvent).where(
        RaceEvent.season_id == season.id,
        RaceEvent.round_number == round_number
    )
    result = await db.execute(query)
    race_event = result.scalar_one_or_none()
    
    if not race_event:
        race_event = RaceEvent(
            season_id=season.id,
            round_number=round_number
        )
        db.add(race_event)
    
    # Update event details
    race_event.event_name = str(event_data.get('EventName', ''))
    race_event.official_name = str(event_data.get('OfficialEventName', ''))
    race_event.country = str(event_data.get('Country', ''))
    race_event.location = str(event_data.get('Location', ''))
    race_event.date_start = pd.to_datetime(event_data.get('EventDate'))
    race_event.is_sprint_weekend = bool(event_data.get('EventFormat', '') == 'sprint')
    
    return race_event


async def fetch_session_data(
    db: AsyncSession,
    year: int,
    round_number: int,
    session_type: str
) -> RaceSession:
    """
    Fetch complete session data including results, laps, and telemetry.
    """
    logger.info(f"Fetching {session_type} session for {year} R{round_number}")
    
    # Get event
    query = (
        select(RaceEvent)
        .join(Season)
        .where(Season.year == year, RaceEvent.round_number == round_number)
    )
    result = await db.execute(query)
    event = result.scalar_one_or_none()
    
    if not event:
        raise ValueError(f"Event not found: {year} R{round_number}")
    
    # Get or create session
    query = select(RaceSession).where(
        RaceSession.event_id == event.id,
        RaceSession.session_type == session_type.upper()
    )
    result = await db.execute(query)
    session = result.scalar_one_or_none()
    
    if not session:
        session = RaceSession(
            event_id=event.id,
            session_type=session_type.upper()
        )
        db.add(session)
        await db.flush()
    
    # Load FastF1 session data
    try:
        f1_session = await asyncio.to_thread(
            fastf1.get_session, year, round_number, session_type
        )
        await asyncio.to_thread(f1_session.load)
        
        # Update session metadata
        session.session_date = pd.to_datetime(f1_session.date) if hasattr(f1_session, 'date') else None
        session.total_laps = int(f1_session.total_laps) if hasattr(f1_session, 'total_laps') else None
        
        # Process results
        await _process_results(db, session, f1_session)
        
        # Process lap data
        await _process_laps(db, session, f1_session)
        
        # Process telemetry (if available)
        has_telemetry = await _process_telemetry(db, session, f1_session)
        session.has_telemetry = has_telemetry
        
        # Store track layout
        if hasattr(f1_session, 'get_circuit_info'):
            try:
                circuit_info = f1_session.get_circuit_info()
                if hasattr(circuit_info, 'corners'):
                    event.track_layout_json = json.dumps({
                        'x': circuit_info.corners['X'].tolist(),
                        'y': circuit_info.corners['Y'].tolist()
                    })
            except Exception as e:
                logger.warning(f"Failed to get track layout: {e}")
        
        session.data_fetched = True
        await db.commit()
        
        logger.info(f"Successfully fetched session data for {year} R{round_number} {session_type}")
        return session
        
    except Exception as e:
        logger.error(f"Failed to fetch session data: {e}")
        await db.rollback()
        raise


async def _process_results(
    db: AsyncSession,
    session: RaceSession,
    f1_session
) -> None:
    """Process session results and drivers/teams."""
    
    results_df = f1_session.results
    
    for idx, result in results_df.iterrows():
        # Get or create driver
        driver = await _get_or_create_driver(db, result)
        
        # Get or create team
        team = await _get_or_create_team(db, result) if 'TeamName' in result else None
        
        # Create session result
        session_result = SessionResult(
            session_id=session.id,
            driver_id=driver.id,
            team_id=team.id if team else None,
            position=int(result.get('Position', 0)) or None,
            grid_position=int(result.get('GridPosition', 0)) or None,
            status=str(result.get('Status', '')),
            points=float(result.get('Points', 0.0)),
        )
        db.add(session_result)


async def _get_or_create_driver(db: AsyncSession, result: pd.Series) -> Driver:
    """Get or create driver from result data."""
    
    driver_code = str(result.get('Abbreviation', ''))
    
    query = select(Driver).where(Driver.driver_code == driver_code)
    db_result = await db.execute(query)
    driver = db_result.scalar_one_or_none()
    
    if not driver:
        driver = Driver(
            driver_code=driver_code,
            driver_number=int(result.get('DriverNumber', 0)) or None,
            first_name=str(result.get('FirstName', '')),
            last_name=str(result.get('LastName', '')),
            full_name=str(result.get('FullName', '')),
            abbreviation=driver_code,
        )
        db.add(driver)
        await db.flush()
    
    return driver


async def _get_or_create_team(db: AsyncSession, result: pd.Series) -> Team:
    """Get or create team from result data."""
    
    team_name = str(result.get('TeamName', ''))
    
    query = select(Team).where(Team.name == team_name)
    db_result = await db.execute(query)
    team = db_result.scalar_one_or_none()
    
    if not team:
        team = Team(
            name=team_name,
            color=str(result.get('TeamColor', '')),
        )
        db.add(team)
        await db.flush()
    
    return team


async def _process_laps(
    db: AsyncSession,
    session: RaceSession,
    f1_session
) -> None:
    """Process lap data for all drivers."""
    
    laps_df = f1_session.laps
    
    for idx, lap in laps_df.iterrows():
        # Get driver ID
        driver_code = str(lap.get('Driver', ''))
        query = select(Driver).where(Driver.driver_code == driver_code)
        result = await db.execute(query)
        driver = result.scalar_one_or_none()
        
        if not driver:
            continue
        
        lap_data = LapData(
            session_id=session.id,
            driver_id=driver.id,
            lap_number=int(lap.get('LapNumber', 0)),
            lap_time_ms=float(lap.get('LapTime', pd.NaT).total_seconds() * 1000) if pd.notna(lap.get('LapTime')) else None,
            sector1_ms=float(lap.get('Sector1Time', pd.NaT).total_seconds() * 1000) if pd.notna(lap.get('Sector1Time')) else None,
            sector2_ms=float(lap.get('Sector2Time', pd.NaT).total_seconds() * 1000) if pd.notna(lap.get('Sector2Time')) else None,
            sector3_ms=float(lap.get('Sector3Time', pd.NaT).total_seconds() * 1000) if pd.notna(lap.get('Sector3Time')) else None,
            compound=str(lap.get('Compound', '')) if pd.notna(lap.get('Compound')) else None,
            is_pit_in_lap=bool(lap.get('PitInTime', pd.NaT) != pd.NaT),
            is_pit_out_lap=bool(lap.get('PitOutTime', pd.NaT) != pd.NaT),
            position=int(lap.get('Position', 0)) or None,
        )
        db.add(lap_data)


async def _process_telemetry(
    db: AsyncSession,
    session: RaceSession,
    f1_session
) -> bool:
    """Process telemetry data for all drivers (if available)."""
    
    try:
        laps_df = f1_session.laps
        
        # Check if telemetry is available
        if laps_df.empty:
            return False
        
        for driver_code in laps_df['Driver'].unique():
            driver_laps = laps_df[laps_df['Driver'] == driver_code]
            
            # Get driver ID
            query = select(Driver).where(Driver.driver_code == driver_code)
            result = await db.execute(query)
            driver = result.scalar_one_or_none()
            
            if not driver:
                continue
            
            # Process telemetry for each lap
            for idx, lap in driver_laps.iterrows():
                try:
                    telemetry = await asyncio.to_thread(lap.get_telemetry)
                    
                    if telemetry.empty:
                        continue
                    
                    # Store telemetry as JSON arrays
                    frame = TelemetryFrame(
                        session_id=session.id,
                        driver_id=driver.id,
                        lap_number=int(lap.get('LapNumber', 0)),
                        sample_count=len(telemetry),
                        timestamps_ms=json.dumps(telemetry.get('Time', pd.Series()).dt.total_seconds().mul(1000).tolist()),
                        speed_kmh=json.dumps(telemetry.get('Speed', pd.Series()).tolist()),
                        throttle_pct=json.dumps(telemetry.get('Throttle', pd.Series()).tolist()),
                        brake_pct=json.dumps(telemetry.get('Brake', pd.Series()).tolist()),
                        rpm=json.dumps(telemetry.get('RPM', pd.Series()).tolist()),
                        gear=json.dumps(telemetry.get('nGear', pd.Series()).tolist()),
                        drs=json.dumps(telemetry.get('DRS', pd.Series()).tolist()),
                        pos_x=json.dumps(telemetry.get('X', pd.Series()).tolist()),
                        pos_y=json.dumps(telemetry.get('Y', pd.Series()).tolist()),
                    )
                    db.add(frame)
                    
                except Exception as e:
                    logger.warning(f"Failed to process telemetry for {driver_code} lap {lap.get('LapNumber')}: {e}")
                    continue
        
        return True
        
    except Exception as e:
        logger.warning(f"Telemetry not available: {e}")
        return False
