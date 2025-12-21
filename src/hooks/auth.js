import {ref} from 'vue'

export const auth = {
  getToken() {
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