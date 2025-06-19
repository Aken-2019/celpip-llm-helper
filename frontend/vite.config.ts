import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import path from 'path';

export default defineConfig(({}) => ({
  plugins: [svelte()],
  resolve: {
    alias: {
      '@': path.resolve('./src')
    }
  },
  build: {
    outDir: '../static/frontend',
    emptyOutDir: true,
    rollupOptions: {
      input: 'main.ts',
      output: {
        entryFileNames: 'assets/components.js',
        chunkFileNames: 'assets/[name].[hash].js',
        assetFileNames: 'assets/[name].[hash][extname]'
      }
    }
  },
  server: {
    port: 5173,
    strictPort: true,
    fs: {
      // Allow serving files from one level up from the package root
      allow: ['..']
    },
    // Uncomment and adjust when you need to proxy API requests
    // proxy: {
    //   '/api': {
    //     target: 'http://localhost:8000',
    //     changeOrigin: true,
    //     rewrite: (path) => path.replace(/^\/api/, '')
    //   }
    // }
  }
}));