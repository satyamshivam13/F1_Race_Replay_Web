'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { ChevronRight, Loader2, AlertCircle } from 'lucide-react';
import { getSession, Session } from '@/lib/api';
import { connectReplay, disconnect } from '@/lib/socket';
import { useReplayStore } from '@/lib/store';
import TrackCanvas from '@/components/track/TrackCanvas';
import ReplayControls from '@/components/controls/ReplayControls';
import StandingsPanel from '@/components/panels/StandingsPanel';
import TelemetryPanel from '@/components/panels/TelemetryPanel';

export default function ReplayPage() {
  const params = useParams();
  const year = Number(params.year);
  const round = Number(params.round);
  
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const { status, cars } = useReplayStore();

  // Load session data
  useEffect(() => {
    setLoading(true);
    setError(null);
    
    getSession(year, round, 'R')
      .then(setSession)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
      
    return () => {
      disconnect();
    };
  }, [year, round]);

  // Connect to replay when session is loaded
  useEffect(() => {
    if (session?.id && session.has_telemetry) {
      connectReplay(session.id).catch(console.error);
    }
  }, [session]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-f1-gray-600">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-f1-red mx-auto" />
          <p className="mt-4 text-gray-400">Loading race data...</p>
        </div>
      </div>
    );
  }

  if (error || !session) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-f1-gray-600">
        <div className="f1-card p-8 text-center max-w-md">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold mb-2">Failed to load race</h2>
          <p className="text-gray-400 mb-4">{error || 'Session not found'}</p>
          <Link href="/races" className="f1-button">
            Back to Races
          </Link>
        </div>
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-f1-gray-600 flex flex-col">
      {/* Header */}
      <header className="bg-f1-gray-500 border-b border-f1-gray-400 flex-shrink-0">
        <div className="max-w-full mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Link href="/" className="text-f1-red font-bold text-xl">
                F1 Replay
              </Link>
              <ChevronRight className="w-4 h-4 text-gray-500" />
              <Link href="/races" className="text-gray-400 hover:text-white">
                Races
              </Link>
              <ChevronRight className="w-4 h-4 text-gray-500" />
              <span className="font-semibold">{session.event_name}</span>
            </div>
            
            <div className="flex items-center gap-4 text-sm">
              <span className="text-gray-400">
                {year} Round {round}
              </span>
              {session.has_telemetry ? (
                <span className="bg-green-600 text-white px-2 py-0.5 rounded text-xs">
                  Telemetry Available
                </span>
              ) : (
                <span className="bg-yellow-600 text-white px-2 py-0.5 rounded text-xs">
                  Results Only
                </span>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Track Visualization */}
        <div className="flex-1 relative">
          <TrackCanvas
            trackLayout={session.track_layout}
            cars={cars}
          />
          
          {/* Replay Controls Overlay */}
          <div className="absolute bottom-0 left-0 right-0 p-4">
            <ReplayControls />
          </div>
        </div>

        {/* Side Panels */}
        <div className="w-80 flex-shrink-0 border-l border-f1-gray-400 flex flex-col overflow-hidden">
          {/* Standings */}
          <div className="flex-1 overflow-hidden">
            <StandingsPanel results={session.results} />
          </div>
          
          {/* Telemetry */}
          {session.has_telemetry && (
            <div className="h-64 border-t border-f1-gray-400">
              <TelemetryPanel />
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
