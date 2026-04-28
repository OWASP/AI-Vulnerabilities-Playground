import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(() => {
  // Keep dev proxy configurable; default works for local uvicorn.
  const env = process.env
  const apiTarget = env.VITE_DEV_API_TARGET

  return {
    plugins: [react()],
    server: {
      port: 5173,
      host: true,
      // Proxy API requests to backend during development
      proxy: apiTarget
        ? {
            '/api': {
              target: apiTarget,
              changeOrigin: true,
              secure: false,
            }
          }
        : undefined
    }
  }
})
