import { createRouter, createWebHashHistory } from 'vue-router'
import Messenger from './Messenger.vue'
import Auth from './Auth.vue'
import Logout from './Logout.vue'
import {isLoggedIn} from '@/AuthStore'
const routes = [
  { path: '/', component: Messenger },
  { path: '/signup', component:Auth },
  { path: '/login', component: Auth},
  { path: '/logout', component: Logout}
]
const router = createRouter({
  history: createWebHashHistory(),
  routes,
})
router.beforeEach(async (to) => {
  if (
    // make sure the user is authenticated
    !isLoggedIn() &&
    // ❗️ Avoid an infinite redirect
    to.path !== '/login' &&
    to.path !== '/signup' &&
    to.path !== '/logout'
  ) {
    // redirect the user to the login page
    return { path: '/login' }
  }
})
export default router;
