import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// In Docker, nginx serves the build and proxies /api -> api:8000.
// For local `npm run dev`, proxy /api to the API on localhost:8000.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (p) => p.replace(/^\/api/, ''),
      },
    },
  },
})
