import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig(async () => {
  // Dynamically import the ESM module
  const { viteStaticCopy } = await import('vite-plugin-static-copy')
  
  return {
    plugins: [
      vue(),
      viteStaticCopy({
        targets: [
          {
            src: 'node_modules/pdfjs-dist/build/pdf.worker.min.mjs',
            dest: 'assets'
          }
        ]
      })
    ],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      }
    },
    server: {
      port: 3000,
      proxy: {
        '/api': {
          target: 'http://localhost:5001',
          changeOrigin: true
        }
      }
    },
    define: {
      // 定义全局环境变量
      'import.meta.env.VITE_API_BASE_URL': JSON.stringify('http://localhost:5001')
    }
  }
})