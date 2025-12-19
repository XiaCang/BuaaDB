<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { Loading } from '@element-plus/icons-vue'
import { auth } from './hooks/auth'
import { getSelfInfo } from './api'
const userStore = useUserStore()
const appReady = ref(false)

onMounted(async () => {
  try {
    // 初始化用户信息（如果有token）
      if (auth.getToken()) {
        const info = await getSelfInfo()
        userStore.setUserInfo(info)
      }
  } catch (error) {
    console.error('应用初始化失败:', error)
  } finally {
    appReady.value = true
  }
})
</script>

<template>
  <router-view></router-view>
</template>

<style>
html, body {
  margin: 0;
  padding: 0;
}

</style>
