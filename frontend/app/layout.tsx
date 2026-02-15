import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import Header from '@/components/Header';
import { ErrorBoundary } from '@/components/ErrorBoundary';

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' });

export const metadata: Metadata = {
  title: 'F1 Race Replay | Interactive Race Visualization',
  description: 'Watch any Formula 1 race from 1950 to present with animated car positions, live timing, and telemetry data',
  keywords: ['F1', 'Formula 1', 'Race Replay', 'Telemetry', 'Racing', 'Motorsport'],
  authors: [{ name: 'F1 Race Replay' }],
  openGraph: {
    title: 'F1 Race Replay',
    description: 'Interactive Formula 1 race replay and data visualization',
    type: 'website',
  },
  icons: {
    icon: '/favicon.ico',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} font-sans min-h-screen bg-f1-gray-800 text-white`}>
        <ErrorBoundary>
          <div className="flex flex-col min-h-screen">
            <Header />
            <main className="flex-1">
              {children}
            </main>
            <footer className="border-t border-f1-gray-400 py-6 mt-auto">
              <div className="max-w-7xl mx-auto px-4 text-center text-sm text-gray-400">
                <p>Built with ❤️ for the F1 community</p>
                <p className="mt-1">Data provided by FastF1 • Not affiliated with Formula 1</p>
              </div>
            </footer>
          </div>
        </ErrorBoundary>
      </body>
    </html>
  );
}
