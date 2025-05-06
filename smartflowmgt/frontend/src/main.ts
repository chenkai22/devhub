// import './assets/styles/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import zhCN from 'element-plus/es/locale/lang/zh-cn'
import 'element-plus/dist/index.css'
import './assets/styles/border.css'
import './assets/styles/reset.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(ElementPlus, { locale: zhCN })

app.mount('#app')
