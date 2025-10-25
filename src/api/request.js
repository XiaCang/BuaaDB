// src/api/request.js
import axios from 'axios'

const request = axios.create({
  baseURL: 'http://localhost:5000/api', // 本地测试后端
  timeout: 1000
})

// 请求拦截器：自动加 token
request.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `${token}`
  }
  return config
})

export default request
