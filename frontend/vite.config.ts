import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import path from 'path';

export default defineConfig(({ command }) => ({
  plugins: [svelte()],
  resolve: {
    alias: {
      '@': path.resolve('./src')
    }
  },
  base: command === 'build' ? '/static/' : '/',
  build: {
    outDir: '../static/frontend',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        // main: './index.html',
        components: './main.ts'
      },
      output: {
        entryFileNames: 'assets/[name].js',
        chunkFileNames: 'assets/[name].[hash].js',
        assetFileNames: 'assets/[name].[hash][extname]'
      }
    }
  },
  server: {
    port: 5173,
    strictPort: true,
    fs: {
      allow: ['..']
    },
    hmr: {
      protocol: 'ws',
      host: 'localhost'
    },
  }
}));