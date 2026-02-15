/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './lib/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        // F1 brand colors
        f1: {
          red: '#E10600',
          'red-dark': '#b30500',
          'red-light': '#ff1e00',
          black: '#15151E',
          white: '#FFFFFF',
          gray: {
            100: '#F5F5F5',
            200: '#E8E8E8',
            300: '#4a4a52',
            400: '#38383F',
            500: '#2D2D35',
            600: '#1F1F27',
            700: '#1a1a24',
            800: '#15151e',
            900: '#0d0d0f',
          },
          gold: '#ffb800',
          silver: '#c0c0c0',
          bronze: '#cd7f32',
        },
        // Team colors (2024 season)
        team: {
          redbull: '#3671C6',
          ferrari: '#F91536',
          mercedes: '#6CD3BF',
          mclaren: '#F58020',
          'aston-martin': '#229971',
          alpine: '#2293D1',
          williams: '#37BEDD',
          rb: '#6692FF',
          sauber: '#52E252',
          haas: '#B6BABD',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Menlo', 'monospace'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'slide-up': 'slideUp 0.5s ease-out',
        'slide-down': 'slideDown 0.5s ease-out',
        'slide-left': 'slideLeft 0.5s ease-out',
        'slide-right': 'slideRight 0.5s ease-out',
        'fade-in': 'fadeIn 0.5s ease-out',
        'scale-in': 'scaleIn 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55)',
        'shimmer': 'shimmer 2s infinite linear',
        'speed-lines': 'speedLines 1s linear infinite',
      },
      keyframes: {
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideDown: {
          '0%': { opacity: '0', transform: 'translateY(-20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideLeft: {
          '0%': { opacity: '0', transform: 'translateX(20px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        slideRight: {
          '0%': { opacity: '0', transform: 'translateX(-20px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        scaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.9)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-1000px 0' },
          '100%': { backgroundPosition: '1000px 0' },
        },
        speedLines: {
          '0%': { backgroundPosition: '0 0' },
          '100%': { backgroundPosition: '100px 0' },
        },
      },
      boxShadow: {
        'f1-red': '0 10px 40px -10px rgba(225, 6, 0, 0.5)',
        'f1-glow': '0 0 20px rgba(225, 6, 0, 0.4)',
      },
    },
  },
  plugins: [],
};
