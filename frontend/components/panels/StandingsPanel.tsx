'use client';

import { SessionResult } from '@/lib/api';
import { useReplayStore, CarPosition } from '@/lib/store';

interface StandingsPanelProps {
  results: SessionResult[];
}

export default function StandingsPanel({ results }: StandingsPanelProps) {
  const { cars, selectedDriverId, selectDriver } = useReplayStore();

  // Merge static results with live car data
  const standings = results
    .map((result) => {
      const liveCar = cars.find((c) => c.driver_id === result.driver.id);
      return {
        ...result,
        live: liveCar,
      };
    })
    .sort((a, b) => {
      // Sort by live position if available, otherwise static position
      const posA = a.live?.position ?? a.position ?? 99;
      const posB = b.live?.position ?? b.position ?? 99;
      return posA - posB;
    });

  const formatGap = (ms: number | null | undefined) => {
    if (ms == null) return '';
    if (ms === 0) return 'LEADER';
    const seconds = ms / 1000;
    if (seconds < 60) return `+${seconds.toFixed(3)}`;
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `+${mins}:${secs.toFixed(3).padStart(6, '0')}`;
  };

  return (
    <div className="h-full flex flex-col bg-f1-gray-500">
      {/* Header */}
      <div className="p-3 border-b border-f1-gray-400">
        <h2 className="font-semibold">Live Standings</h2>
      </div>

      {/* Standings list */}
      <div className="flex-1 overflow-y-auto">
        {standings.map((entry) => {
          const isSelected = selectedDriverId === entry.driver.id;
          const position = entry.live?.position ?? entry.position ?? '-';
          const teamColor = entry.team?.color || '#808080';
          const driverCode = entry.driver.abbreviation || entry.driver.driver_code || '???';
          const gap = entry.live?.gap_to_leader_ms ?? null;
          const interval = entry.live?.interval_ms ?? null;
          const compound = entry.live?.compound;

          return (
            <div
              key={entry.id}
              onClick={() => selectDriver(isSelected ? null : entry.driver.id)}
              className={`timing-row ${isSelected ? 'bg-f1-gray-400' : ''}`}
            >
              {/* Position */}
              <div className="timing-position">
                {position}
              </div>

              {/* Team color bar */}
              <div
                className="w-1 h-8 rounded"
                style={{ backgroundColor: teamColor }}
              />

              {/* Driver info */}
              <div className="timing-driver">
                <span className="font-mono">{driverCode}</span>
                {entry.live?.drs_active && (
                  <span className="ml-2 text-xs text-green-500">DRS</span>
                )}
              </div>

              {/* Gap/Interval */}
              <div className="timing-gap text-right">
                {position === 1 ? (
                  <span className="text-gray-500">LEADER</span>
                ) : gap != null ? (
                  <span>{formatGap(gap)}</span>
                ) : interval != null ? (
                  <span>{formatGap(interval)}</span>
                ) : (
                  <span className="text-gray-600">—</span>
                )}
              </div>

              {/* Tire compound */}
              {compound && (
                <div className="w-6 text-center">
                  <TireIcon compound={compound} />
                </div>
              )}
            </div>
          );
        })}

        {standings.length === 0 && (
          <div className="p-4 text-center text-gray-500">
            No standings data
          </div>
        )}
      </div>
    </div>
  );
}

function TireIcon({ compound }: { compound: string }) {
  const colors: Record<string, string> = {
    SOFT: '#FF3333',
    MEDIUM: '#FFC700',
    HARD: '#FFFFFF',
    INTERMEDIATE: '#43B02A',
    WET: '#0072CE',
  };

  const color = colors[compound.toUpperCase()] || '#808080';
  const letter = compound.charAt(0).toUpperCase();

  return (
    <div
      className="w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold"
      style={{ backgroundColor: color, color: compound === 'HARD' ? '#000' : '#FFF' }}
      title={compound}
    >
      {letter}
    </div>
  );
}
