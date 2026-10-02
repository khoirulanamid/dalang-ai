import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  esbuild: {
    // Treat undefined variables strictly
    pure: ["console.debug"],
  },
  server: {
    port: 5173,
    host: true,
    allowedHosts: true,
    proxy: {
      "/ws": {
        target: "http://127.0.0.1:8765",
        ws: true,
        changeOrigin: true,
      },
      "/agents": {
        target: "http://127.0.0.1:8765",
        changeOrigin: true,
      },
      "/tasks": {
        target: "http://127.0.0.1:8765",
        changeOrigin: true,
      },
      "/vault": {
        target: "http://127.0.0.1:8765",
        changeOrigin: true,
      },
      "/orchestrate": {
        target: "http://127.0.0.1:8765",
        changeOrigin: true,
      },
      "/events": {
        target: "http://127.0.0.1:8765",
        changeOrigin: true,
      },
      "/api": {
        target: "http://127.0.0.1:8765",
        changeOrigin: true,
      },
    },
  },
});
