import { fileURLToPath, URL } from 'node:url';
import react from '@vitejs/plugin-react';
import { defineConfig } from 'vitest/config';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup.ts'],
    css: true,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html'],
      include: [
        'src/lib/config.ts',
        'src/components/app/**/*.tsx',
        'src/pages/Inventory.tsx',
      ],
      exclude: ['src/test/**', 'src/vite-env.d.ts', 'src/lib/mockData.ts'],
      thresholds: {
        lines: 60,
        functions: 60,
        statements: 60,
        branches: 45,
      },
    },
  },
});
