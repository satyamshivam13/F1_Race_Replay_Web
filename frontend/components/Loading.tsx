'use client';

import { Loader2 } from 'lucide-react';

interface LoadingProps {
  message?: string;
  fullScreen?: boolean;
}

export default function Loading({ message = 'Loading...', fullScreen = false }: LoadingProps) {
  const content = (
    <div className="flex flex-col items-center justify-center gap-4">
      <Loader2 className="w-12 h-12 text-f1-red animate-spin" />
      <p className="text-gray-400 animate-pulse">{message}</p>
    </div>
  );

  if (fullScreen) {
    return (
      <div className="min-h-screen bg-f1-gray-800 flex items-center justify-center">
        {content}
      </div>
    );
  }

  return content;
}

// Racing-themed loading with speed lines
export function RacingLoader() {
  return (
    <div className="flex flex-col items-center justify-center gap-4 p-8">
      <div className="relative">
        <div className="w-16 h-16 rounded-full border-4 border-f1-gray-400 border-t-f1-red animate-spin" />
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-8 h-8 rounded-full bg-f1-red animate-pulse" />
        </div>
      </div>
      <div className="text-center">
        <div className="text-gradient-red font-bold text-lg mb-1">
          Loading Race Data
        </div>
        <div className="text-xs text-gray-500 uppercase tracking-wider">
          Please wait...
        </div>
      </div>
    </div>
  );
}

// Skeleton loader for lists
export function SkeletonCard() {
  return (
    <div className="f1-card p-6 animate-pulse">
      <div className="h-4 bg-f1-gray-400 rounded w-3/4 mb-4" />
      <div className="h-3 bg-f1-gray-400 rounded w-1/2 mb-2" />
      <div className="h-3 bg-f1-gray-400 rounded w-2/3" />
    </div>
  );
}

// Loading bar for progress
export function LoadingBar({ progress }: { progress?: number }) {
  return (
    <div className="w-full h-1 bg-f1-gray-400 rounded-full overflow-hidden">
      <div
        className="h-full bg-gradient-to-r from-f1-red via-f1-red-light to-f1-red transition-all duration-300"
        style={{ width: progress ? `${progress}%` : '50%' }}
      >
        {!progress && (
          <div className="w-full h-full bg-gradient-to-r from-transparent via-white/30 to-transparent animate-speed-lines" />
        )}
      </div>
    </div>
  );
}
