import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"

const allowed_hosts = process.env.VITE_ALLOWED_HOSTS || ".com"

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: "0.0.0.0",
    open: true,
    proxy: {
      "/api": {
        changeOrigin: true,
        secure: false,
      },
    },
    allowedHosts: [allowed_hosts],
  },
  build: {
    sourcemap: true,
  },
})
