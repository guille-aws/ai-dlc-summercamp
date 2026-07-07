/** @type {import('next').NextConfig} */
const nextConfig = {
  // Static export (SPA) for Amplify Hosting (NFR-U7-1).
  output: "export",
  reactStrictMode: true,
  images: { unoptimized: true },
};

module.exports = nextConfig;
