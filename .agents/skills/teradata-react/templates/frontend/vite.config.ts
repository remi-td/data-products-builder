import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "node:path";

const BACKEND_PORT = parseInt(process.env.VITE_BACKEND_PORT ?? "8000", 10);
const FRONTEND_PORT = parseInt(process.env.VITE_FRONTEND_PORT ?? "5173", 10);

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: { "@": path.resolve(__dirname, "./src") },
  },
  server: {
    port: FRONTEND_PORT,
    strictPort: true,
    proxy: {
      "/api": `http://localhost:${BACKEND_PORT}`,
    },
  },
});
