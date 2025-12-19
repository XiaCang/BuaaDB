import {ref} from 'vue'

export const auth = {
    getToken() {
    // 可以从 localStorage、Vuex、Pinia 或 Cookie 获取
    return localStorage.getItem('token')
  },
  
  setToken(token) {
    localStorage.setItem('token', token)
  },
  
  removeToken() {
    localStorage.removeItem('token')
  },
  
  isAuthenticated() {
    return !!this.getToken()
  }
}