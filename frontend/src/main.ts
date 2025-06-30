import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import { navigationService } from './services/navigationService'

// 初始化导航服务
navigationService.init(router)

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
