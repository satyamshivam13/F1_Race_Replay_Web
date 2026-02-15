'use client';

import { useReplayStore } from '@/lib/store';

export default function TelemetryPanel() {
  const { selectedDriverId, cars } = useReplayStore();
  
  // Find selected car data
  const selectedCar = cars.find((c) => c.driver_id === selectedDriverId);

  if (!selectedDriverId) {
    return (
      <div className="h-full flex items-center justify-center bg-f1-gray-500 text-gray-500">
        <p className="text-sm">Select a driver to view telemetry</p>
      </div>
    );
  }

  if (!selectedCar) {
    return (
      <div className="h-full flex items-center justify-center bg-f1-gray-500 text-gray-500">
        <p className="text-sm">No telemetry data for selected driver</p>
      </div>
    );
  }

  return (
    <div className="h-full bg-f1-gray-500 p-4 flex flex-col">
      {/* Driver header */}
      <div className="flex items-center gap-3 mb-4">
        <div
          className="w-3 h-8 rounded"
          style={{ backgroundColor: selectedCar.team_color }}
        />
        <div>
          <span className="font-mono font-bold text-lg">{selectedCar.driver_code}</span>
          <span className="text-gray-400 ml-2">P{selectedCar.position}</span>
        </div>
      </div>

      {/* Telemetry gauges */}
      <div className="space-y-4 flex-1">
        {/* Speed */}
        <TelemetryGauge
          label="Speed"
          value={selectedCar.speed_kmh}
          max={370}
          unit="km/h"
          color="#3B82F6"
        />

        {/* These would need actual telemetry data from WebSocket */}
        {/* For now, showing placeholder based on speed */}
        <TelemetryGauge
          label="Throttle"
          value={selectedCar.speed_kmh > 200 ? 100 : (selectedCar.speed_kmh / 200) * 100}
          max={100}
          unit="%"
          color="#22C55E"
        />

        <TelemetryGauge
          label="Brake"
          value={selectedCar.speed_kmh < 100 ? 50 : 0}
          max={100}
          unit="%"
          color="#EF4444"
        />
      </div>

      {/* Additional info */}
      <div className="grid grid-cols-3 gap-2 mt-4 text-center">
        <div className="bg-f1-gray-400 rounded p-2">
          <div className="text-xs text-gray-400">DRS</div>
          <div className={`font-bold ${selectedCar.drs_active ? 'text-green-500' : 'text-gray-500'}`}>
            {selectedCar.drs_active ? 'ON' : 'OFF'}
          </div>
        </div>
        <div className="bg-f1-gray-400 rounded p-2">
          <div className="text-xs text-gray-400">Compound</div>
          <div className="font-bold">
            {selectedCar.compound?.charAt(0) || '-'}
          </div>
        </div>
        <div className="bg-f1-gray-400 rounded p-2">
          <div className="text-xs text-gray-400">Gap</div>
          <div className="font-mono text-sm">
            {selectedCar.gap_to_leader_ms 
              ? `+${(selectedCar.gap_to_leader_ms / 1000).toFixed(1)}s`
              : 'LEAD'}
          </div>
        </div>
      </div>
    </div>
  );
}

interface TelemetryGaugeProps {
  label: string;
  value: number;
  max: number;
  unit: string;
  color: string;
}

function TelemetryGauge({ label, value, max, unit, color }: TelemetryGaugeProps) {
  const percentage = Math.min(100, (value / max) * 100);

  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="text-gray-400">{label}</span>
        <span className="font-mono">
          {Math.round(value)} <span className="text-gray-500">{unit}</span>
        </span>
      </div>
      <div className="h-2 bg-f1-gray-400 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-100"
          style={{ width: `${percentage}%`, backgroundColor: color }}
        />
      </div>
    </div>
  );
}
