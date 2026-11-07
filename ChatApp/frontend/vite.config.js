import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
    plugins: [react()],
    server: {
        host: true, // also listen on your network IP (e.g. 192.168.1.100)
        port: 5173,
    },
})