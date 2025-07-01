// File: frontend/vite.config.ts (Enhanced)
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
    },
  },
  build: {
    // Enable build optimizations
    target: 'esnext',
    minify: 'terser',
    sourcemap: false, // Disable in production
    
    // Chunk splitting for better caching
    rollupOptions: {
      output: {
        manualChunks: {
          // Separate vendor chunks
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'ui-vendor': ['@tiptap/react', '@tiptap/starter-kit', 'react-beautiful-dnd'],
          'utils-vendor': ['axios', 'lodash', 'date-fns'],
          'socket-vendor': ['socket.io-client']
        },
        // Better file naming
        chunkFileNames: 'assets/js/[name]-[hash].js',
        entryFileNames: 'assets/js/[name]-[hash].js',
        assetFileNames: 'assets/[ext]/[name]-[hash].[ext]'
      }
    },
    
    // Set chunk size warning limit
    chunkSizeWarningLimit: 1000,
    
    // Optimize dependencies
    commonjsOptions: {
      include: [/node_modules/]
    }
  },
  
  // Development server optimizations
  server: {
    port: 5173,
    host: true,
    cors: true
  },
  
  // Preview server config
  preview: {
    port: 4173,
    host: true
  }
})