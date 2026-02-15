"""
Pydantic schemas for API request/response models.
"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict


# ============================================================================
# Base schemas with common config
# ============================================================================

class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Season schemas
# ============================================================================

class SeasonBase(BaseSchema):
    year: int
    total_rounds: Optional[int] = None


class SeasonSummary(SeasonBase):
    id: int
    data_fetched: bool


class SeasonDetail(SeasonSummary):
    events: List["EventSummary"] = []


# ============================================================================
# Event schemas
# ============================================================================

class EventBase(BaseSchema):
    round_number: int
    event_name: str
    country: Optional[str] = None
    circuit_name: Optional[str] = None


class EventSummary(EventBase):
    id: int
    date_start: Optional[datetime] = None
    is_sprint_weekend: bool = False
    data_fetched: bool = False


class EventDetail(EventSummary):
    official_name: Optional[str] = None
    location: Optional[str] = None
    circuit_short_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    track_length_km: Optional[float] = None
    data_level: int = 1
    sessions: List["SessionSummary"] = []


# ============================================================================
# Session schemas
# ============================================================================

class SessionBase(BaseSchema):
    session_type: str


class SessionSummary(SessionBase):
    id: int
    session_date: Optional[datetime] = None
    total_laps: Optional[int] = None
    data_fetched: bool = False
    has_telemetry: bool = False


class SessionDetail(SessionSummary):
    weather: Optional[str] = None
    air_temp: Optional[float] = None
    track_temp: Optional[float] = None
    results: List["ResultSummary"] = []


class SessionWithTrack(SessionDetail):
    """Session with track layout for replay."""
    track_layout: Optional[dict] = None
    event_name: str
    circuit_name: Optional[str] = None


# ============================================================================
# Driver schemas
# ============================================================================

class DriverBase(BaseSchema):
    driver_code: Optional[str] = None
    first_name: str
    last_name: str


class DriverSummary(DriverBase):
    id: int
    driver_number: Optional[int] = None
    abbreviation: Optional[str] = None


class DriverDetail(DriverSummary):
    full_name: str
    nationality: Optional[str] = None
    headshot_url: Optional[str] = None


# ============================================================================
# Team schemas
# ============================================================================

class TeamBase(BaseSchema):
    name: str


class TeamSummary(TeamBase):
    id: int
    short_name: Optional[str] = None
    color: Optional[str] = None


# ============================================================================
# Result schemas
# ============================================================================

class ResultSummary(BaseSchema):
    id: int
    position: Optional[int] = None
    grid_position: Optional[int] = None
    status: Optional[str] = None
    points: float = 0.0
    driver: DriverSummary
    team: Optional[TeamSummary] = None


# ============================================================================
# Lap data schemas
# ============================================================================

class LapDataSchema(BaseSchema):
    lap_number: int
    driver_id: int
    lap_time_ms: Optional[float] = None
    sector1_ms: Optional[float] = None
    sector2_ms: Optional[float] = None
    sector3_ms: Optional[float] = None
    compound: Optional[str] = None
    tyre_life: Optional[int] = None
    position: Optional[int] = None
    gap_to_leader_ms: Optional[float] = None
    interval_ms: Optional[float] = None
    is_pit_in_lap: bool = False
    is_pit_out_lap: bool = False
    lap_start_time_ms: Optional[float] = None


# ============================================================================
# Telemetry schemas
# ============================================================================

class TelemetryFrameSchema(BaseSchema):
    lap_number: int
    driver_id: int
    sample_count: int
    timestamps_ms: Optional[List[float]] = None
    speed_kmh: Optional[List[float]] = None
    throttle_pct: Optional[List[float]] = None
    brake_pct: Optional[List[float]] = None
    rpm: Optional[List[int]] = None
    gear: Optional[List[int]] = None
    drs: Optional[List[int]] = None
    pos_x: Optional[List[float]] = None
    pos_y: Optional[List[float]] = None


# ============================================================================
# Replay schemas (WebSocket)
# ============================================================================

class ReplayCommand(BaseModel):
    """Command sent by client to control replay."""
    action: str  # play, pause, stop, seek, speed
    time_ms: Optional[float] = None
    speed: Optional[float] = None


class CarPosition(BaseModel):
    """Single car position for a frame."""
    driver_id: int
    driver_code: str
    team_color: str
    x: float
    y: float
    heading: float
    speed_kmh: float
    position: int
    gap_to_leader_ms: Optional[float] = None
    interval_ms: Optional[float] = None
    compound: Optional[str] = None
    drs_active: bool = False


class ReplayFrame(BaseModel):
    """Single frame of replay data."""
    timestamp_ms: float
    current_lap: int
    total_laps: int
    elapsed_time_str: str
    replay_speed: float
    cars: List[CarPosition]
    track_status: Optional[str] = None


class StandingsEntry(BaseModel):
    """Single entry in standings."""
    position: int
    driver_id: int
    driver_code: str
    team_name: str
    team_color: str
    gap_to_leader: Optional[str] = None
    interval: Optional[str] = None
    last_lap_time: Optional[str] = None
    compound: Optional[str] = None
    pit_stops: int = 0


# Rebuild models that have forward references
SeasonDetail.model_rebuild()
EventDetail.model_rebuild()
SessionDetail.model_rebuild()
