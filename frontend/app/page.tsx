'use client';

import Link from 'next/link';
import { Flag, Play, BarChart3, Clock } from 'lucide-react';

export default function HomePage() {
  return (
    <main className="min-h-screen">
      {/* Hero Section */}
      <div className="relative bg-gradient-to-br from-f1-gray-600 via-f1-gray-500 to-f1-gray-600">
        <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-10" />
        
        <div className="relative max-w-7xl mx-auto px-4 py-24 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-5xl md:text-7xl font-bold tracking-tight">
              <span className="text-f1-red">F1</span> Race Replay
            </h1>
            <p className="mt-6 text-xl md:text-2xl text-gray-300 max-w-3xl mx-auto">
              Watch any Formula 1 race from 1950 to present with animated car positions, 
              live timing, and telemetry data.
            </p>
            
            <div className="mt-10 flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/races"
                className="f1-button text-lg px-8 py-4 inline-flex items-center justify-center gap-2"
              >
                <Play className="w-5 h-5" />
                Browse Races
              </Link>
              <a
                href="#features"
                className="f1-button-secondary text-lg px-8 py-4 inline-flex items-center justify-center gap-2"
              >
                Learn More
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <section id="features" className="py-24 bg-f1-gray-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center mb-16">Features</h2>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            <FeatureCard
              icon={<Play className="w-8 h-8 text-f1-red" />}
              title="Race Replay"
              description="Watch any F1 race with animated car positions on the circuit map"
            />
            <FeatureCard
              icon={<Clock className="w-8 h-8 text-f1-red" />}
              title="Live Timing"
              description="Real-time standings, gaps, intervals, and sector times"
            />
            <FeatureCard
              icon={<BarChart3 className="w-8 h-8 text-f1-red" />}
              title="Telemetry"
              description="Speed, throttle, brake, gear, RPM, and DRS data"
            />
            <FeatureCard
              icon={<Flag className="w-8 h-8 text-f1-red" />}
              title="All Seasons"
              description="Complete F1 history from 1950 to present day"
            />
          </div>
        </div>
      </section>

      {/* Data Coverage */}
      <section className="py-24 bg-f1-gray-600">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center mb-16">Data Coverage</h2>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <DataCard
              era="2018 – Present"
              level="Full Telemetry"
              description="GPS, speed, throttle, brake, gear, DRS"
              color="bg-green-500"
            />
            <DataCard
              era="2011 – 2017"
              level="Detailed Laps"
              description="Sector times, limited telemetry"
              color="bg-blue-500"
            />
            <DataCard
              era="1996 – 2010"
              level="Lap Data"
              description="Lap times, pit stops, results"
              color="bg-yellow-500"
            />
            <DataCard
              era="1950 – 1995"
              level="Results"
              description="Race results, grid positions"
              color="bg-gray-500"
            />
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 bg-f1-gray-600 border-t border-f1-gray-400">
        <div className="max-w-7xl mx-auto px-4 text-center text-gray-400">
          <p>Built with ❤️ for the F1 community</p>
          <p className="mt-2 text-sm">
            Data provided by FastF1 • Not affiliated with Formula 1
          </p>
        </div>
      </footer>
    </main>
  );
}

function FeatureCard({ icon, title, description }: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <div className="f1-card p-6 text-center">
      <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-f1-gray-400 mb-4">
        {icon}
      </div>
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="text-gray-400">{description}</p>
    </div>
  );
}

function DataCard({ era, level, description, color }: {
  era: string;
  level: string;
  description: string;
  color: string;
}) {
  return (
    <div className="f1-card p-6">
      <div className={`w-3 h-3 rounded-full ${color} mb-4`} />
      <h3 className="font-bold text-lg">{era}</h3>
      <p className="text-f1-red font-semibold mt-1">{level}</p>
      <p className="text-gray-400 text-sm mt-2">{description}</p>
    </div>
  );
}
