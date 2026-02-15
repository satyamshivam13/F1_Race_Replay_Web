'use client';

import { Play, Pause, Square, SkipBack, SkipForward, Gauge } from 'lucide-react';
import { useReplayStore } from '@/lib/store';
import { play, pause, stop, seek, setSpeed } from '@/lib/socket';

const SPEED_OPTIONS = [0.5, 1, 2, 5, 10, 20];

export default function ReplayControls() {
  const {
    status,
    isPlaying,
    currentTimeMs,
    totalDurationMs,
    replaySpeed,
    currentLap,
    totalLaps,
  } = useReplayStore();

  const formatTime = (ms: number) => {
    const totalSec = Math.floor(ms / 1000);
    const hours = Math.floor(totalSec / 3600);
    const minutes = Math.floor((totalSec % 3600) / 60);
    const seconds = totalSec % 60;
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  };

  const progress = totalDurationMs > 0 ? (currentTimeMs / totalDurationMs) * 100 : 0;

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseFloat(e.target.value);
    const timeMs = (value / 100) * totalDurationMs;
    seek(timeMs);
  };

  const handleSpeedChange = (newSpeed: number) => {
    setSpeed(newSpeed);
  };

  const isReady = status === 'ready' || status === 'playing' || status === 'paused';

  return (
    <div className="f1-card p-4">
      {/* Progress bar */}
      <div className="mb-4">
        <input
          type="range"
          min="0"
          max="100"
          step="0.1"
          value={progress}
          onChange={handleSeek}
          disabled={!isReady}
          className="w-full h-2 bg-f1-gray-400 rounded-lg appearance-none cursor-pointer
                     [&::-webkit-slider-thumb]:appearance-none
                     [&::-webkit-slider-thumb]:w-4
                     [&::-webkit-slider-thumb]:h-4
                     [&::-webkit-slider-thumb]:bg-f1-red
                     [&::-webkit-slider-thumb]:rounded-full
                     [&::-webkit-slider-thumb]:cursor-pointer
                     disabled:opacity-50 disabled:cursor-not-allowed"
        />
      </div>

      <div className="flex items-center justify-between">
        {/* Time display */}
        <div className="flex items-center gap-4 text-sm">
          <span className="font-mono text-lg">{formatTime(currentTimeMs)}</span>
          <span className="text-gray-500">/</span>
          <span className="font-mono text-gray-400">{formatTime(totalDurationMs)}</span>
        </div>

        {/* Playback controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={stop}
            disabled={!isReady}
            className="p-2 rounded hover:bg-f1-gray-400 disabled:opacity-50 disabled:cursor-not-allowed"
            title="Stop"
          >
            <Square className="w-5 h-5" />
          </button>
          
          <button
            onClick={() => seek(Math.max(0, currentTimeMs - 10000))}
            disabled={!isReady}
            className="p-2 rounded hover:bg-f1-gray-400 disabled:opacity-50 disabled:cursor-not-allowed"
            title="Back 10s"
          >
            <SkipBack className="w-5 h-5" />
          </button>
          
          <button
            onClick={() => isPlaying ? pause() : play()}
            disabled={!isReady}
            className="p-3 bg-f1-red rounded-full hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
            title={isPlaying ? 'Pause' : 'Play'}
          >
            {isPlaying ? (
              <Pause className="w-6 h-6" />
            ) : (
              <Play className="w-6 h-6" />
            )}
          </button>
          
          <button
            onClick={() => seek(Math.min(totalDurationMs, currentTimeMs + 10000))}
            disabled={!isReady}
            className="p-2 rounded hover:bg-f1-gray-400 disabled:opacity-50 disabled:cursor-not-allowed"
            title="Forward 10s"
          >
            <SkipForward className="w-5 h-5" />
          </button>
        </div>

        {/* Speed and lap info */}
        <div className="flex items-center gap-6">
          {/* Speed selector */}
          <div className="flex items-center gap-2">
            <Gauge className="w-4 h-4 text-gray-400" />
            <div className="flex gap-1">
              {SPEED_OPTIONS.map((speed) => (
                <button
                  key={speed}
                  onClick={() => handleSpeedChange(speed)}
                  disabled={!isReady}
                  className={`px-2 py-1 text-xs rounded transition-colors ${
                    replaySpeed === speed
                      ? 'bg-f1-red text-white'
                      : 'bg-f1-gray-400 hover:bg-f1-gray-300'
                  } disabled:opacity-50 disabled:cursor-not-allowed`}
                >
                  {speed}x
                </button>
              ))}
            </div>
          </div>

          {/* Lap counter */}
          <div className="text-sm">
            <span className="text-gray-400">Lap</span>
            <span className="font-mono font-semibold ml-2">
              {currentLap}/{totalLaps}
            </span>
          </div>
        </div>
      </div>

      {/* Status indicator */}
      {status === 'loading' && (
        <div className="mt-3 text-center text-sm text-gray-400">
          Loading replay data...
        </div>
      )}
      {status === 'error' && (
        <div className="mt-3 text-center text-sm text-red-500">
          Connection error. Please refresh the page.
        </div>
      )}
      {status === 'finished' && (
        <div className="mt-3 text-center text-sm text-green-500">
          Race replay finished
        </div>
      )}
    </div>
  );
}
