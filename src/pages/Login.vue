<template>
  <div class="login-container">
    <div class="decoration circle-1"></div>
    <div class="decoration circle-2"></div>

    <el-card class="login-card">
      <div class="login-header">
        <div class="logo">
          <el-icon :size="40" color="#ff6600"><Shop /></el-icon>
        </div>
        <h2>校园二手交易系统</h2>
        <p>让闲置物品焕发新生</p>
      </div>

      <el-tabs v-model="activeName" class="login-tabs" stretch>
        <el-tab-pane label="账号登录" name="login">
          <el-form :model="loginForm" :rules="rules" ref="loginFormRef" label-position="top">
            <el-form-item label="用户名" prop="username">
              <el-input 
                v-model="loginForm.username" 
                placeholder="请输入用户名"
                prefix-icon="User"
              />
            </el-form-item>
            <el-form-item label="密码" prop="password">
              <el-input 
                v-model="loginForm.password" 
                type="password" 
                placeholder="请输入密码" 
                prefix-icon="Lock"
                show-password
                @keyup.enter="handleLogin"
              />
            </el-form-item>
            <el-button 
              type="primary" 
              class="submit-btn" 
              @click="handleLogin" 
              :loading="loading"
            >
              立即登录
            </el-button>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="新用户注册" name="register">
          <el-form :model="registerForm" :rules="rules" ref="registerFormRef" label-position="top">
            <el-form-item label="用户名" prop="username">
              <el-input v-model="registerForm.username" placeholder="设置用户名" prefix-icon="User" />
            </el-form-item>
            <el-form-item label="密码" prop="password">
              <el-input v-model="registerForm.password" type="password" placeholder="设置密码" prefix-icon="Lock" show-password />
            </el-form-item>
            <el-button 
              type="primary" 
              class="submit-btn" 
              @click="handleRegister" 
              :loading="loading"
            >
              注册账号
            </el-button>
          </el-form>
        </el-tab-pane>
      </el-tabs>

    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Shop, User, Lock } from '@element-plus/icons-vue'
import { login, register, getSelfInfo } from '@/api/index'
import { useUserStore } from '@/stores/user'
import md5 from 'js-md5'

const router = useRouter()
const userStore = useUserStore()

const activeName = ref('login')
const loading = ref(false)
const rememberMe = ref(false)
const loginFormRef = ref(null)
const registerFormRef = ref(null)

const loginForm = reactive({
  username: '',
  password: ''
})

const registerForm = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }, { min: 6, message: '密码不能少于6位', trigger: 'blur' }]
}

// 登录
const handleLogin = async () => {
  if (!loginFormRef.value) return
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        // 加密密码
        const data = {
          username: loginForm.username,
          password: md5(loginForm.password)
        }
        const res = await login(data)

        console.log('In handleLogin: res = ', res);
        
        const token = res.token || res.data?.token
        
        if (token) {
          userStore.setToken(token)

          const info = await getSelfInfo()
          userStore.setUserInfo(info)
          
          ElMessage.success('登录成功！欢迎回来')
          router.push('/') 
        }
      } catch (error) {
        console.error(error)
      } finally {
        loading.value = false
      }
    }
  })
}

// 注册
const handleRegister = async () => {
  if (!registerFormRef.value) return
  await registerFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        // 加密密码
        const data = {
          username: registerForm.username,
          password: md5(registerForm.password)
        }
        await register(data)
        ElMessage.success('注册成功，请登录')
        activeName.value = 'login'
      } catch (error) {
        console.error(error)
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>

.login-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #fff5e6 0%, #ffedcc 100%);
  position: relative;
  overflow: hidden;
}


.decoration {
  position: absolute;
  border-radius: 50%;
  background: linear-gradient(to bottom right, #ff6600, #ff9838);
  opacity: 0.1;
  z-index: 0;
}
.circle-1 { width: 400px; height: 400px; top: -100px; left: -100px; }
.circle-2 { width: 300px; height: 300px; bottom: -50px; right: -50px; }


.login-card {
  width: 420px;
  border-radius: 16px;
  box-shadow: 0 12px 32px rgba(255, 102, 0, 0.1);
  border: none;
  z-index: 1;
  padding: 10px;
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h2 {
  color: #333;
  margin: 10px 0 5px;
  font-size: 24px;
}

.login-header p {
  color: #999;
  font-size: 14px;
}

.login-tabs :deep(.el-tabs__item.is-active) {
  color: #ff6600;
  font-weight: bold;
}

.login-tabs :deep(.el-tabs__active-bar) {
  background-color: #ff6600;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.submit-btn {
  width: 100%;
  height: 45px;
  font-size: 16px;
  border-radius: 8px;
  background: linear-gradient(90deg, #ff9838, #ff6600);
  border: none;
  margin-top: 10px;
}

.submit-btn:hover {
  opacity: 0.9;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(255, 102, 0, 0.3);
}

.login-footer {
  text-align: center;
  margin-top: 30px;
  font-size: 12px;
  color: #bbb;
}


:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #ff6600 inset !important;
}
</style>