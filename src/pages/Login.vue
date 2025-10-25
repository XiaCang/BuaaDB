<template>
  <div class="login-page">
    <!-- 背景 -->
    <div class="background">
      <!-- 左白右蓝 -->
      <div class="bg-left">
      </div>
      <div class="bg-right">
        <!-- 简单几何图形装饰 -->
        <div class="circle"></div>
        <div class="triangle"></div>
      </div>
    </div>

    <!-- 登录卡片 -->
    <div class="login-card">
      <!-- 左侧登录表单 -->
      <div class="login-form">
        <div class="tabs">
          <span
            :class="{ active: activeTab === 'login' }"
            @click="activeTab = 'login'"
          >登录</span>
          <span
            :class="{ active: activeTab === 'register' }"
            @click="activeTab = 'register'"
          >注册</span>
        </div>

        <el-form
          :model="form"
          class="form"
          label-position="top"
          @submit.prevent="onSubmit"
        >
          <el-form-item label="用户名">
            <el-input v-model="form.username" placeholder="请输入用户名" prefix-icon="el-icon-user"/>
          </el-form-item>

          <el-form-item label="密码">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="请输入密码"
              prefix-icon="el-icon-lock"
              show-password
            />
          </el-form-item>

          <el-text :type="info_type">{{  error_info }}</el-text>
          

          <el-button type="primary" class="login-btn" @click="onSubmit">
            {{ activeTab === 'login' ? '登录' : '注册' }}
          </el-button>
        </el-form>
      </div>

      <!-- 右侧介绍区域 -->
      <div class="welcome-section">
        <div class="welcome-content">
          <h2>Welcome to TradeHub</h2>
          <p>在这里，让闲置重新发光 ✨</p>
          <p>一个安全高效的二手物品交易系统。</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { login,register } from "@/api/auth";
import { useUserTokenStore } from "@/stores/auth";
import { useRouter } from "vue-router";

import md5 from "js-md5";

const router = useRouter();

const form = ref({
  username: "",
  password: "",
});

const error_info = ref("");
const info_type = ref("danger")
const activeTab = ref("login");

const onSubmit = () => {

  if (form.value.username === "") {
    error_info.value = "请输入用户名";
  }
  else if (form.value.password === "") {
    error_info.value = "请输入密码";
  } else {
    error_info.value = "";
  }
  const md5_password = md5(form.value.password);
  if (activeTab.value === "login") {

    login(form.value.username, md5_password)
    .then((res) => {
      const userTokenStore = useUserTokenStore();
      userTokenStore.token = res.data.token;
      localStorage.setItem("token", res.data.token);
      router.push({ name: "home" });
    }).catch((err) => {
      info_type.value = "danger"
      error_info.value = err.response.data.message;
    })
  } else {
    register(form.value.username, md5_password).then((res) => {
      info_type.value = "success"
      error_info.value = res.data.message;
    }).catch((err) => {
      info_type.value = "danger"
      error_info.value = err.response.data.message;
    })
  }
};
</script>

<style scoped>
.login-page {
  position: relative;
  width: 100%;
  height: 100vh;
  overflow: hidden;
  font-family: "Segoe UI", "PingFang SC", sans-serif;
}

.background {
  display: flex;
  position: absolute;
  inset: 0;
  z-index: 0;
}

.bg-left {
  flex: 1;
  background-color: #ffffff;
}

.bg-right {
  flex: 1;
  background-color: #0b3c63;
  position: relative;
  overflow: hidden;
}

.circle {
  position: absolute;
  top: 80px;
  right: 100px;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.08);
}

.triangle {
  position: absolute;
  bottom: 100px;
  left: 80px;
  width: 0;
  height: 0;
  border-left: 60px solid transparent;
  border-right: 60px solid transparent;
  border-bottom: 100px solid rgba(255, 255, 255, 0.08);
}

/* 登录卡片 */
.login-card {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 900px;
  height: 500px;
  transform: translate(-50%, -50%);
  display: flex;
  box-shadow: 0 0 30px rgba(0, 0, 0, 0.2);
  border-radius: 20px;
  overflow: hidden;
  z-index: 1;
}

/* 表单部分 */
.login-form {
  flex: 1;
  background-color: white;
  padding: 60px 80px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.tabs {
  display: flex;
  gap: 40px;
  margin-bottom: 40px;
  font-size: 22px;
  font-weight: 600;
}

.tabs span {
  cursor: pointer;
  color: #aaa;
  transition: 0.3s;
}

.tabs span.active {
  color: #0b3c63;
  border-bottom: 3px solid #0b3c63;
  padding-bottom: 6px;
}

.el-form-item {
  margin-bottom: 24px;
}

.el-input {
  border: none;
  border-bottom: 1px solid #ccc;
  border-radius: 0;
}

.el-input:focus-within {
  border-bottom-color: #0b3c63;
}

.login-btn {
  width: 100%;
  margin-top: 20px;
  background-color: #0b3c63;
  border: none;
}

/* 右侧欢迎语部分 */
.welcome-section {
  flex: 1;
  background-color: #0b3c63;
  color: #fff;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
}

.welcome-content {
  text-align: center;
  padding: 0 40px;
}

.welcome-content h2 {
  font-size: 32px;
  margin-bottom: 20px;
}

.welcome-content p {
  font-size: 18px;
  line-height: 1.6;
}
</style>
