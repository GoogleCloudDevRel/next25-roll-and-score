import { createApp } from 'vue'
import App from './App.vue'
import RollAndScoreApp from './App.vue'
import { getQueryParam } from './utils/get-query-param'
import { createPinia } from 'pinia'

const pinia = createPinia()

let app
if (getQueryParam('roolAndScore')) {
  app = createApp(RollAndScoreApp)
} else {
  app = createApp(App)
}

app.use(pinia)
app.mount('#app')
