import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  turbopack: {
    root: "/Users/joel/Documents/Dev/Athena/trusted-service/config-rule",
  },
  async rewrites() {
    return [
      {
        source: "/api/v1/:path*",
        destination: "http://localhost:8002/api/v1/:path*",
      },
    ];
  },
};

export default nextConfig;



