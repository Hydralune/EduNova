import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import { navigationService } from './services/navigationService'
import NotificationContainer from './components/NotificationContainer.vue'
import ConfirmDialog from './components/ConfirmDialog.vue'

// 初始化导航服务
navigationService.init(router)

const app = createApp(App)

app.use(createPinia())
app.use(router)

// 注册全局组件
app.component('NotificationContainer', NotificationContainer)
app.component('ConfirmDialog', ConfirmDialog)

app.mount('#app')
