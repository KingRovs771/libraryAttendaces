import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Register from '../components/Register.vue'
import Scan from '@/components/Scan.vue'
import Attendance from '@/components/Attendance.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/register', component: Register },
  { path: '/scan', component: Scan },
  { path: '/attendance', component: Attendance },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
