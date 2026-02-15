/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ['localhost'],
  },
  // Enable WebSocket connections in dev
  async rewrites() {
    return [
      {
        source: '/ws/:path*',
        destination: `${process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'}/ws/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
