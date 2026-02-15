'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Flag, Home, Calendar } from 'lucide-react';

export default function Header() {
  const pathname = usePathname();

  const isActive = (path: string) => {
    return pathname === path || pathname.startsWith(path + '/');
  };

  return (
    <header className="sticky top-0 z-50 bg-f1-gray-700/95 backdrop-blur-sm border-b border-f1-gray-400 shadow-lg">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link 
            href="/" 
            className="flex items-center gap-2 group"
          >
            <div className="relative">
              <Flag className="w-6 h-6 text-f1-red group-hover:scale-110 transition-transform" />
              <div className="absolute inset-0 bg-f1-red blur-lg opacity-50 group-hover:opacity-100 transition-opacity" />
            </div>
            <span className="text-xl font-bold">
              <span className="text-f1-red">F1</span> Replay
            </span>
          </Link>

          {/* Navigation */}
          <div className="flex items-center gap-1">
            <NavLink
              href="/"
              icon={<Home className="w-4 h-4" />}
              label="Home"
              isActive={pathname === '/'}
            />
            <NavLink
              href="/races"
              icon={<Calendar className="w-4 h-4" />}
              label="Races"
              isActive={isActive('/races')}
            />
          </div>
        </div>
      </nav>
    </header>
  );
}

interface NavLinkProps {
  href: string;
  icon: React.ReactNode;
  label: string;
  isActive: boolean;
}

function NavLink({ href, icon, label, isActive }: NavLinkProps) {
  return (
    <Link
      href={href}
      className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${
        isActive
          ? 'bg-f1-red text-white shadow-lg shadow-f1-red/30'
          : 'text-gray-300 hover:text-white hover:bg-f1-gray-600'
      }`}
    >
      {icon}
      <span className="hidden sm:inline">{label}</span>
    </Link>
  );
}
