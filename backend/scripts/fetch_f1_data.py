"""
Script to fetch F1 data from FastF1 and populate the database.

Usage:
    # Fetch full 2024 season (schedule only)
    python scripts/fetch_f1_data.py --year 2024
    
    # Fetch specific race session
    python scripts/fetch_f1_data.py --year 2024 --round 1 --session Race
    
    # Fetch multiple recent seasons
    python scripts/fetch_f1_data.py --year 2024 --year 2023
"""

import asyncio
import argparse
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.database import async_session_maker, init_db
from app.services.f1_data import fetch_season_schedule, fetch_session_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)


async def fetch_season(year: int) -> None:
    """Fetch season schedule for a given year."""
    async with async_session_maker() as db:
        try:
            logger.info(f"Fetching season {year}...")
            season = await fetch_season_schedule(db, year)
            logger.info(f"✅ Successfully fetched {season.total_rounds} events for {year}")
        except Exception as e:
            logger.error(f"❌ Failed to fetch season {year}: {e}")
            raise


async def fetch_session(year: int, round_num: int, session_type: str) -> None:
    """Fetch complete session data including telemetry."""
    async with async_session_maker() as db:
        try:
            logger.info(f"Fetching {year} R{round_num} {session_type}...")
            session = await fetch_session_data(db, year, round_num, session_type)
            logger.info(f"✅ Successfully fetched session data")
            logger.info(f"   - Session ID: {session.id}")
            logger.info(f"   - Total Laps: {session.total_laps or 'N/A'}")
            logger.info(f"   - Has Telemetry: {'Yes' if session.has_telemetry else 'No'}")
        except Exception as e:
            logger.error(f"❌ Failed to fetch session: {e}")
            raise


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Fetch F1 data from FastF1")
    parser.add_argument(
        "--year",
        type=int,
        action="append",
        required=True,
        help="Season year(s) to fetch (can specify multiple)"
    )
    parser.add_argument(
        "--round",
        type=int,
        help="Specific round number to fetch (requires --session)"
    )
    parser.add_argument(
        "--session",
        type=str,
        choices=["FP1", "FP2", "FP3", "Q", "SQ", "S", "R", "Race", "Qualifying", "Sprint"],
        help="Session type to fetch (requires --round)"
    )
    parser.add_argument(
        "--init-db",
        action="store_true",
        help="Initialize database schema before fetching"
    )
    
    args = parser.parse_args()
    
    # Initialize database if requested
    if args.init_db:
        logger.info("Initializing database schema...")
        await init_db()
        logger.info("✅ Database initialized")
    
    # Fetch data
    for year in args.year:
        if args.round and args.session:
            # Fetch specific session
            await fetch_session(year, args.round, args.session)
        else:
            # Fetch season schedule
            await fetch_season(year)
    
    logger.info("🏁 All done!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
