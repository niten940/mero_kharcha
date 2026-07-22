import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import { quasar, transformAssetUrls } from '@quasar/vite-plugin'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue({
      template: { transformAssetUrls } // Helps Vue process Quasar assets correctly
    }),
    vueDevTools(),
    quasar({
      sassVariables: 'quasar/src/css/variables.sass' // Handles Quasar components and styling
    })
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  css: {
    preprocessorOptions: {
      sass: {
        // Silences the older @import warnings from Quasar inside your console logs
        silenceDeprecations: ['import']
      }
    }
  },
  server: {
    host: '0.0.0.0',
    port: 5173 // Vue's default port
  }
})
