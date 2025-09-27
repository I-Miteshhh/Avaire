import { createRequire } from "module";

const require = createRequire(import.meta.url);

const nextConfig = {
  reactStrictMode: true,
  experimental: {
    appDir: true
  },
  images: {
    remotePatterns: [
      {
        protocol: "http",
        hostname: "localhost",
        port: "8000",
        pathname: "/storage/**"
      },
      {
        protocol: "https",
        hostname: "*.amazonaws.com"
      }
    ]
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
  }
};

export default nextConfig;
