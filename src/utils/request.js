// src/utils/request.js

import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const service = axios.create({
  baseURL: 'http://localhost:5000/api', // 这里假设你配置了 vite 的 proxy，或者直接写后端全路径
  timeout: 5000
})

// 请求拦截器
service.interceptors.request.use(
  (config) => {
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers['Authorization'] = userStore.token // 假设后端使用 Bearer Token
      // 或者 config.headers['token'] = userStore.token
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器
service.interceptors.response.use(
  (response) => {
    const res = response.data
    // 假设后端只要不是 200 就是错误，或者根据 message 判断
    // 这里根据你的API文档，似乎没有统一 code，主要看 http status 或 message
    return res
  },
  (error) => {
    ElMessage.error(error.response?.data?.message || '请求失败')
    return Promise.reject(error)
  }
)

export default service