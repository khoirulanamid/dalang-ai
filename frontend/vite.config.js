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
  },
});
