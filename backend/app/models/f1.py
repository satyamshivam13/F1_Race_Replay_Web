"""
SQLAlchemy ORM models for F1 Race Replay.
Ported from desktop application with async support.
"""

from datetime import datetime
from typing import Optional, List

from sqlalchemy import (
    Boolean, Float, ForeignKey, Index, Integer, String, Text,
    UniqueConstraint, DateTime
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Season(Base):
    """F1 Championship season (1950–present)."""
    __tablename__ = "seasons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    year: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True)
    total_rounds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    data_fetched: Mapped[bool] = mapped_column(Boolean, default=False)
    last_updated: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    events: Mapped[List["RaceEvent"]] = relationship(
        "RaceEvent", back_populates="season", cascade="all, delete-orphan"
    )


class RaceEvent(Base):
    """A Grand Prix weekend event."""
    __tablename__ = "race_events"
    __table_args__ = (
        UniqueConstraint("season_id", "round_number", name="uq_season_round"),
        Index("ix_race_event_lookup", "season_id", "round_number"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    season_id: Mapped[int] = mapped_column(Integer, ForeignKey("seasons.id"), nullable=False)
    round_number: Mapped[int] = mapped_column(Integer, nullable=False)
    event_name: Mapped[str] = mapped_column(String(200), nullable=False)
    official_name: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    circuit_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    circuit_short_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    date_start: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    date_end: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_sprint_weekend: Mapped[bool] = mapped_column(Boolean, default=False)
    data_level: Mapped[int] = mapped_column(Integer, default=1)
    data_fetched: Mapped[bool] = mapped_column(Boolean, default=False)
    track_layout_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    track_length_km: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Relationships
    season: Mapped["Season"] = relationship("Season", back_populates="events")
    sessions: Mapped[List["RaceSession"]] = relationship(
        "RaceSession", back_populates="event", cascade="all, delete-orphan"
    )


class RaceSession(Base):
    """Individual session within a race weekend."""
    __tablename__ = "race_sessions"
    __table_args__ = (
        UniqueConstraint("event_id", "session_type", name="uq_event_session"),
        Index("ix_session_lookup", "event_id", "session_type"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(Integer, ForeignKey("race_events.id"), nullable=False)
    session_type: Mapped[str] = mapped_column(String(10), nullable=False)
    session_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    total_laps: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    weather: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    air_temp: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    track_temp: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    data_fetched: Mapped[bool] = mapped_column(Boolean, default=False)
    has_telemetry: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    event: Mapped["RaceEvent"] = relationship("RaceEvent", back_populates="sessions")
    results: Mapped[List["SessionResult"]] = relationship(
        "SessionResult", back_populates="session", cascade="all, delete-orphan"
    )
    laps: Mapped[List["LapData"]] = relationship(
        "LapData", back_populates="session", cascade="all, delete-orphan"
    )
    telemetry_frames: Mapped[List["TelemetryFrame"]] = relationship(
        "TelemetryFrame", back_populates="session", cascade="all, delete-orphan"
    )


class Driver(Base):
    """F1 driver."""
    __tablename__ = "drivers"
    __table_args__ = (Index("ix_driver_code", "driver_code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    driver_code: Mapped[Optional[str]] = mapped_column(String(10), unique=True, nullable=True)
    driver_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    abbreviation: Mapped[Optional[str]] = mapped_column(String(3), nullable=True)
    nationality: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    headshot_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Relationships
    results: Mapped[List["SessionResult"]] = relationship("SessionResult", back_populates="driver")


class Team(Base):
    """F1 constructor/team."""
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    short_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    color: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)
    nationality: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Relationships
    results: Mapped[List["SessionResult"]] = relationship("SessionResult", back_populates="team")


class SessionResult(Base):
    """A driver's result for a session."""
    __tablename__ = "session_results"
    __table_args__ = (
        UniqueConstraint("session_id", "driver_id", name="uq_session_driver"),
        Index("ix_result_lookup", "session_id", "position"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("race_sessions.id"), nullable=False)
    driver_id: Mapped[int] = mapped_column(Integer, ForeignKey("drivers.id"), nullable=False)
    team_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("teams.id"), nullable=True)
    position: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    grid_position: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    points: Mapped[float] = mapped_column(Float, default=0.0)
    total_time_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    fastest_lap_time_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    laps_completed: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relationships
    session: Mapped["RaceSession"] = relationship("RaceSession", back_populates="results")
    driver: Mapped["Driver"] = relationship("Driver", back_populates="results")
    team: Mapped[Optional["Team"]] = relationship("Team", back_populates="results")


class LapData(Base):
    """Individual lap data for a driver in a session."""
    __tablename__ = "lap_data"
    __table_args__ = (
        UniqueConstraint("session_id", "driver_id", "lap_number", name="uq_session_driver_lap"),
        Index("ix_lap_lookup", "session_id", "driver_id", "lap_number"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("race_sessions.id"), nullable=False)
    driver_id: Mapped[int] = mapped_column(Integer, ForeignKey("drivers.id"), nullable=False)
    lap_number: Mapped[int] = mapped_column(Integer, nullable=False)
    lap_time_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sector1_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sector2_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sector3_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    speed_trap_kmh: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    compound: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    tyre_life: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_pit_in_lap: Mapped[bool] = mapped_column(Boolean, default=False)
    is_pit_out_lap: Mapped[bool] = mapped_column(Boolean, default=False)
    position: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    gap_to_leader_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    interval_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    lap_start_time_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Relationships
    session: Mapped["RaceSession"] = relationship("RaceSession", back_populates="laps")


class TelemetryFrame(Base):
    """High-frequency telemetry data stored as JSON arrays per lap."""
    __tablename__ = "telemetry_frames"
    __table_args__ = (
        UniqueConstraint("session_id", "driver_id", "lap_number", name="uq_telemetry_lap"),
        Index("ix_telemetry_lookup", "session_id", "driver_id", "lap_number"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("race_sessions.id"), nullable=False)
    driver_id: Mapped[int] = mapped_column(Integer, ForeignKey("drivers.id"), nullable=False)
    lap_number: Mapped[int] = mapped_column(Integer, nullable=False)
    sample_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Compressed JSON arrays
    timestamps_ms: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    speed_kmh: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    throttle_pct: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    brake_pct: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rpm: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    gear: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    drs: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    pos_x: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    pos_y: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    session: Mapped["RaceSession"] = relationship("RaceSession", back_populates="telemetry_frames")
