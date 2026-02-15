'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { ChevronRight, Calendar, MapPin, Loader2 } from 'lucide-react';
import { getSeasons, getSeason, Season, RaceEvent } from '@/lib/api';

export default function RacesPage() {
  const [seasons, setSeasons] = useState<Season[]>([]);
  const [selectedYear, setSelectedYear] = useState<number | null>(null);
  const [events, setEvents] = useState<RaceEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingEvents, setLoadingEvents] = useState(false);

  // Load seasons on mount
  useEffect(() => {
    getSeasons()
      .then((data) => {
        setSeasons(data);
        // Select most recent season by default
        if (data.length > 0) {
          setSelectedYear(data[0].year);
        }
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  // Load events when year changes
  useEffect(() => {
    if (!selectedYear) return;
    
    setLoadingEvents(true);
    getSeason(selectedYear)
      .then((data) => setEvents(data.events || []))
      .catch(console.error)
      .finally(() => setLoadingEvents(false));
  }, [selectedYear]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-f1-red" />
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-f1-gray-600">
      {/* Header */}
      <header className="bg-f1-gray-500 border-b border-f1-gray-400">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center gap-4">
            <Link href="/" className="text-f1-red font-bold text-2xl">
              F1 Replay
            </Link>
            <ChevronRight className="w-5 h-5 text-gray-500" />
            <h1 className="text-xl font-semibold">Race Browser</h1>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-4 gap-8">
          {/* Season Selector */}
          <div className="lg:col-span-1">
            <div className="f1-card p-4 sticky top-8">
              <h2 className="font-semibold text-lg mb-4">Seasons</h2>
              <div className="space-y-1 max-h-[70vh] overflow-y-auto">
                {seasons.map((season) => (
                  <button
                    key={season.year}
                    onClick={() => setSelectedYear(season.year)}
                    className={`w-full text-left px-3 py-2 rounded transition-colors ${
                      selectedYear === season.year
                        ? 'bg-f1-red text-white'
                        : 'hover:bg-f1-gray-400'
                    }`}
                  >
                    <span className="font-semibold">{season.year}</span>
                    {season.total_rounds && (
                      <span className="text-sm text-gray-400 ml-2">
                        ({season.total_rounds} races)
                      </span>
                    )}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Events List */}
          <div className="lg:col-span-3">
            <h2 className="text-2xl font-bold mb-6">
              {selectedYear} Season
            </h2>
            
            {loadingEvents ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="w-8 h-8 animate-spin text-f1-red" />
              </div>
            ) : events.length === 0 ? (
              <div className="f1-card p-8 text-center text-gray-400">
                No events found for this season
              </div>
            ) : (
              <div className="grid md:grid-cols-2 gap-4">
                {events.map((event) => (
                  <EventCard key={event.id} event={event} year={selectedYear!} />
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}

function EventCard({ event, year }: { event: RaceEvent; year: number }) {
  const dateStr = event.date_start
    ? new Date(event.date_start).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
      })
    : null;

  return (
    <Link
      href={`/races/${year}/${event.round_number}`}
      className="f1-card p-4 hover:border-f1-red transition-colors group"
    >
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2 text-sm text-gray-400 mb-1">
            <span className="font-mono">R{event.round_number}</span>
            {dateStr && (
              <>
                <span>•</span>
                <Calendar className="w-3 h-3" />
                <span>{dateStr}</span>
              </>
            )}
          </div>
          <h3 className="font-semibold text-lg group-hover:text-f1-red transition-colors">
            {event.event_name}
          </h3>
          {event.circuit_name && (
            <div className="flex items-center gap-1 text-sm text-gray-400 mt-1">
              <MapPin className="w-3 h-3" />
              <span>{event.circuit_name}</span>
            </div>
          )}
        </div>
        
        <div className="flex flex-col items-end gap-2">
          {event.is_sprint_weekend && (
            <span className="text-xs bg-purple-600 text-white px-2 py-0.5 rounded">
              Sprint
            </span>
          )}
          {event.data_fetched ? (
            <span className="text-xs bg-green-600 text-white px-2 py-0.5 rounded">
              Ready
            </span>
          ) : (
            <span className="text-xs bg-gray-600 text-gray-300 px-2 py-0.5 rounded">
              Not fetched
            </span>
          )}
        </div>
      </div>
    </Link>
  );
}
