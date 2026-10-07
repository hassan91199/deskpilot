import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // DP-8: static-exported to `out/`, synced to S3 and served via
  // CloudFront. Safe here - no API routes, no server-side data fetching
  // (see lib/api.ts: pure client-side fetch against the FastAPI backend).
  output: "export",
};

export default nextConfig;
