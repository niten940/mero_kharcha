import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { Quasar, Notify } from 'quasar'

import App from './App.vue'
import router from './router'

// Import Quasar Icons and Core Styles
import '@quasar/extras/material-icons/material-icons.css'
import 'quasar/src/css/index.sass'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(Quasar, {
  plugins: {
    Notify

  }, // Add Quasar plugins here if needed later (e.g., Notify, Dialog)
})

app.mount('#app')