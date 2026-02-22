import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// Импортируем стили
import './styles/reset.css'
import './styles/theme.css'
import './styles/panels.css'

// Create app
const app = createApp(App)

// Setup Pinia
const pinia = createPinia()
app.use(pinia)

// Setup Router
app.use(router)

// Mount app
app.mount('#app')
