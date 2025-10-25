<template>
  <div class="home-container">
    <!-- 左侧导航栏 -->
    <el-menu
      class="sidebar"
      :default-active="activeMenu"
      background-color="#001f3f"
      text-color="#ffffff"
      active-text-color="#00bfff"
      router
    >
      <div class="logo">TradeHub</div>
      <el-menu-item index="user">
        <el-icon><User /></el-icon>
        <span>个人中心</span>
      </el-menu-item>
      <el-menu-item index="favorite">
        <el-icon><Star /></el-icon>
        <span>收藏夹</span>
      </el-menu-item>
      <el-menu-item index="goods">
        <el-icon><ShoppingCart /></el-icon>
        <span>商品</span>
      </el-menu-item>
      <el-menu-item index="order">
        <el-icon><Document /></el-icon>
        <span>我的订单</span>
      </el-menu-item>
      <el-menu-item index="mygoods">
        <el-icon><Box /></el-icon>
        <span>我的商品</span>
      </el-menu-item>
    </el-menu>

    <!-- 右侧主内容 -->
    <div class="main-content">
      <router-view></router-view>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";


const activeMenu = ref("dashboard");
</script>

<style scoped>
.home-container {
  display: flex;
  height: 100vh;
  background-color: #f0f4f8;
}

/* 左侧导航栏 */
.sidebar {
  width: 220px;
  min-width: 220px;
  height: 100%;
  background-color: #001f3f;
  color: #fff;
  border-right: none;
  padding-top: 20px;
}

.logo {
  color: #00bfff;
  font-size: 20px;
  font-weight: bold;
  text-align: center;
  margin-bottom: 20px;
}

/* 右侧主内容区 */
.main-content {
  flex: 1;
  padding: 30px;
  overflow-y: auto;
  background-color: #f0f4f8;
}

/* 欢迎卡片 */
.welcome-card {
  background-color: #001f3f;
  color: #fff;
  margin-bottom: 30px;
  padding: 20px;
  border-radius: 15px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.welcome-card h2 {
  margin: 0 0 10px 0;
  color: #00bfff;
}

.welcome-card p {
  color: #ffffffcc;
  line-height: 1.6;
}

/* 内容占位 */
.content-placeholder {
  height: 500px;
  background: #ffffff;
  border-radius: 15px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #555;
  font-size: 18px;
}
</style>
