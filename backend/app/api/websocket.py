"""
WebSocket endpoint for real-time race replay streaming.
"""

import asyncio
import json
import logging
from typing import Dict, Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_maker
from app.core.config import get_settings
from app.models.f1 import RaceSession, RaceEvent, Season, LapData, TelemetryFrame, SessionResult
from app.schemas.f1 import ReplayCommand, ReplayFrame, CarPosition

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter()


class ReplayState:
    """Manages the state of a single replay session."""
    
    def __init__(self, session_id: int):
        self.session_id = session_id
        self.current_time_ms: float = 0.0
        self.replay_speed: float = 1.0
        self.is_playing: bool = False
        self.total_duration_ms: float = 0.0
        self.total_laps: int = 0
        self.current_lap: int = 0
        self.drivers: Dict[int, dict] = {}  # driver_id -> info
        self.laps: list = []
        self.telemetry: Dict[int, Dict[int, dict]] = {}  # driver_id -> lap -> telemetry


class ConnectionManager:
    """Manages WebSocket connections for replay sessions."""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.replay_states: Dict[int, ReplayState] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
    
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
    
    async def send_json(self, client_id: str, data: dict):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(data)


manager = ConnectionManager()


async def load_session_data(session_id: int) -> Optional[ReplayState]:
    """Load all necessary data for replay."""
    state = ReplayState(session_id)
    
    async with async_session_maker() as db:
        # Get session info
        query = (
            select(RaceSession)
            .where(RaceSession.id == session_id)
        )
        result = await db.execute(query)
        session = result.scalar_one_or_none()
        
        if not session:
            return None
        
        state.total_laps = session.total_laps or 0
        
        # Get results for driver info
        results_query = (
            select(SessionResult)
            .where(SessionResult.session_id == session_id)
        )
        result = await db.execute(results_query)
        results = result.scalars().all()
        
        for r in results:
            # Load driver and team info
            state.drivers[r.driver_id] = {
                "driver_id": r.driver_id,
                "team_id": r.team_id,
                "position": r.position or 0,
            }
        
        # Get all laps
        laps_query = (
            select(LapData)
            .where(LapData.session_id == session_id)
            .order_by(LapData.lap_number, LapData.driver_id)
        )
        result = await db.execute(laps_query)
        state.laps = result.scalars().all()
        
        # Calculate total duration
        for lap in state.laps:
            if lap.lap_start_time_ms and lap.lap_time_ms:
                end_time = lap.lap_start_time_ms + lap.lap_time_ms
                state.total_duration_ms = max(state.total_duration_ms, end_time)
        
        # Load telemetry (if available)
        tel_query = (
            select(TelemetryFrame)
            .where(TelemetryFrame.session_id == session_id)
        )
        result = await db.execute(tel_query)
        tel_frames = result.scalars().all()
        
        for frame in tel_frames:
            if frame.driver_id not in state.telemetry:
                state.telemetry[frame.driver_id] = {}
            
            # Parse JSON data
            try:
                state.telemetry[frame.driver_id][frame.lap_number] = {
                    "timestamps": json.loads(frame.timestamps_ms) if frame.timestamps_ms else [],
                    "pos_x": json.loads(frame.pos_x) if frame.pos_x else [],
                    "pos_y": json.loads(frame.pos_y) if frame.pos_y else [],
                    "speed": json.loads(frame.speed_kmh) if frame.speed_kmh else [],
                    "gear": json.loads(frame.gear) if frame.gear else [],
                    "drs": json.loads(frame.drs) if frame.drs else [],
                }
            except json.JSONDecodeError:
                continue
    
    return state


def interpolate_position(state: ReplayState, driver_id: int, time_ms: float) -> Optional[dict]:
    """Interpolate car position at a given time."""
    # Find the current lap for this driver
    driver_laps = [l for l in state.laps if l.driver_id == driver_id]
    
    current_lap = None
    for lap in driver_laps:
        if lap.lap_start_time_ms is None:
            continue
        lap_end = lap.lap_start_time_ms + (lap.lap_time_ms or 0)
        if lap.lap_start_time_ms <= time_ms <= lap_end:
            current_lap = lap
            break
    
    if not current_lap:
        return None
    
    # Get telemetry for this lap
    tel = state.telemetry.get(driver_id, {}).get(current_lap.lap_number)
    if not tel or not tel["timestamps"]:
        return None
    
    # Find position in telemetry
    timestamps = tel["timestamps"]
    lap_time_offset = time_ms - current_lap.lap_start_time_ms
    
    # Binary search for the right timestamp
    idx = 0
    for i, t in enumerate(timestamps):
        if t > lap_time_offset:
            break
        idx = i
    
    # Get position (with bounds checking)
    pos_x = tel["pos_x"][idx] if idx < len(tel["pos_x"]) else 0
    pos_y = tel["pos_y"][idx] if idx < len(tel["pos_y"]) else 0
    speed = tel["speed"][idx] if idx < len(tel["speed"]) else 0
    gear = tel["gear"][idx] if idx < len(tel["gear"]) else 0
    drs = tel["drs"][idx] if idx < len(tel["drs"]) else 0
    
    return {
        "x": pos_x,
        "y": pos_y,
        "speed_kmh": speed,
        "gear": gear,
        "drs_active": drs > 0,
        "lap_number": current_lap.lap_number,
        "position": current_lap.position or 0,
        "compound": current_lap.compound,
        "gap_to_leader_ms": current_lap.gap_to_leader_ms,
        "interval_ms": current_lap.interval_ms,
    }


def generate_frame(state: ReplayState) -> dict:
    """Generate a single frame of replay data."""
    cars = []
    
    for driver_id, driver_info in state.drivers.items():
        pos = interpolate_position(state, driver_id, state.current_time_ms)
        if pos:
            cars.append({
                "driver_id": driver_id,
                "driver_code": f"D{driver_id}",  # Would be filled from actual data
                "team_color": "#808080",  # Would be filled from actual data
                "x": pos["x"],
                "y": pos["y"],
                "heading": 0,  # Would be calculated from position delta
                "speed_kmh": pos["speed_kmh"],
                "position": pos["position"],
                "gap_to_leader_ms": pos["gap_to_leader_ms"],
                "interval_ms": pos["interval_ms"],
                "compound": pos["compound"],
                "drs_active": pos["drs_active"],
            })
    
    # Format elapsed time
    total_sec = int(state.current_time_ms / 1000)
    hours = total_sec // 3600
    minutes = (total_sec % 3600) // 60
    seconds = total_sec % 60
    elapsed_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    # Determine current lap (from leader)
    if cars:
        leader = min(cars, key=lambda c: c["position"] if c["position"] else 999)
        state.current_lap = leader.get("lap_number", 0) or 0
    
    return {
        "type": "frame",
        "data": {
            "timestamp_ms": state.current_time_ms,
            "current_lap": state.current_lap,
            "total_laps": state.total_laps,
            "elapsed_time_str": elapsed_str,
            "replay_speed": state.replay_speed,
            "cars": cars,
            "track_status": None,
        }
    }


@router.websocket("/ws/replay/{session_id}")
async def replay_websocket(websocket: WebSocket, session_id: int):
    """WebSocket endpoint for race replay streaming."""
    client_id = f"{session_id}_{id(websocket)}"
    await manager.connect(websocket, client_id)
    
    try:
        # Load session data
        state = await load_session_data(session_id)
        if not state:
            await websocket.send_json({"type": "error", "message": "Session not found"})
            return
        
        manager.replay_states[session_id] = state
        
        # Send initial state
        await websocket.send_json({
            "type": "init",
            "data": {
                "total_duration_ms": state.total_duration_ms,
                "total_laps": state.total_laps,
                "driver_count": len(state.drivers),
                "has_telemetry": len(state.telemetry) > 0,
            }
        })
        
        # Main loop
        frame_interval = 1.0 / settings.replay_fps
        last_frame_time = asyncio.get_event_loop().time()
        
        while True:
            try:
                # Check for commands (non-blocking)
                try:
                    data = await asyncio.wait_for(
                        websocket.receive_json(),
                        timeout=frame_interval
                    )
                    
                    # Handle command
                    action = data.get("action")
                    if action == "play":
                        state.is_playing = True
                    elif action == "pause":
                        state.is_playing = False
                    elif action == "stop":
                        state.is_playing = False
                        state.current_time_ms = 0
                    elif action == "seek":
                        state.current_time_ms = data.get("time_ms", 0)
                    elif action == "speed":
                        state.replay_speed = max(0.1, min(60.0, data.get("speed", 1.0)))
                    
                    # Send status update
                    await websocket.send_json({
                        "type": "status",
                        "data": {
                            "is_playing": state.is_playing,
                            "current_time_ms": state.current_time_ms,
                            "replay_speed": state.replay_speed,
                        }
                    })
                    
                except asyncio.TimeoutError:
                    pass
                
                # Update time if playing
                current_time = asyncio.get_event_loop().time()
                dt = current_time - last_frame_time
                last_frame_time = current_time
                
                if state.is_playing:
                    state.current_time_ms += dt * 1000 * state.replay_speed
                    
                    # Check if finished
                    if state.current_time_ms >= state.total_duration_ms:
                        state.current_time_ms = state.total_duration_ms
                        state.is_playing = False
                        await websocket.send_json({"type": "finished"})
                    else:
                        # Send frame
                        frame = generate_frame(state)
                        await websocket.send_json(frame)
                
            except WebSocketDisconnect:
                break
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
    
    finally:
        manager.disconnect(client_id)
        if session_id in manager.replay_states:
            del manager.replay_states[session_id]
