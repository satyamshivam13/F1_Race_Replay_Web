import Link from 'next/link';
import { Flag, Home, ArrowLeft } from 'lucide-react';

export default function NotFound() {
  return (
    <div className="min-h-[calc(100vh-theme(spacing.32))] flex items-center justify-center px-4">
      <div className="max-w-2xl w-full text-center animate-scale-in">
        {/* Large 404 */}
        <div className="relative mb-8">
          <h1 className="text-9xl font-bold text-gradient-red opacity-20">
            404
          </h1>
          <div className="absolute inset-0 flex items-center justify-center">
            <Flag className="w-24 h-24 text-f1-red animate-pulse" />
          </div>
        </div>

        {/* Message */}
        <h2 className="text-3xl font-bold mb-4">
          Race Not Found
        </h2>
        <p className="text-gray-400 text-lg mb-8">
          Looks like this race has been red-flagged. The page you're looking for doesn't exist.
        </p>

        {/* Racing stripes decoration */}
        <div className="racing-stripes h-2 w-32 mx-auto mb-8 rounded-full opacity-50" />

        {/* Actions */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            href="/"
            className="f1-button inline-flex items-center justify-center gap-2"
          >
            <Home className="w-5 h-5" />
            Back to Home
          </Link>
          <button
            onClick={() => window.history.back()}
            className="f1-button-secondary inline-flex items-center justify-center gap-2"
          >
            <ArrowLeft className="w-5 h-5" />
            Go Back
          </button>
        </div>

        {/* Additional info */}
        <div className="mt-12 p-6 bg-f1-gray-600 rounded-lg border border-f1-gray-400">
          <h3 className="font-semibold mb-2">Looking for something specific?</h3>
          <p className="text-sm text-gray-400">
            Browse our <Link href="/races" className="text-f1-red hover:underline">race archive</Link> to find historical F1 races from 1950 to present.
          </p>
        </div>
      </div>
    </div>
  );
}
