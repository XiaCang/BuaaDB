<template>
  <div class="profile-page">
    <!-- 顶部标题 -->
    <div class="profile-header">
      <el-avatar :size="100" class="avatar" src="https://via.placeholder.com/100" />
      <div class="user-info">
        <h2 class="username">用户名</h2>
        <p class="desc">热爱生活的二手交易者</p>
        <el-button type="primary" size="small" class="edit-btn">
          <el-icon><Edit /></el-icon> 修改资料
        </el-button>
      </div>
    </div>

    <!-- 下方信息面板 -->
    <div class="profile-stats">
      <el-card class="stat-card" shadow="hover">
        <el-icon><ChatDotSquare /></el-icon>
        <div class="stat-value">24</div>
        <div class="stat-label">我的评价</div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <el-icon><Box /></el-icon>
        <div class="stat-value">12</div>
        <div class="stat-label">商品数</div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <el-icon><ShoppingCart /></el-icon>
        <div class="stat-value">8</div>
        <div class="stat-label">购买数</div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <el-icon><Star /></el-icon>
        <div class="stat-value">5</div>
        <div class="stat-label">收藏夹</div>
      </el-card>
    </div>

    <!-- 最近活动 -->
    <div class="recent-section">
      <h3>最近评价</h3>
      <el-card class="review-card" v-for="i in 3" :key="i" shadow="hover">
        <div class="review-item">
          <el-avatar :size="40" src="https://via.placeholder.com/40" />
          <div class="review-text">
            <p class="review-username">用户{{ i }}</p>
            <!-- 星级评分 -->
            <el-rate v-model="dummyRatings[i - 1]" disabled show-score text-color="#ffd700" score-template="{value}" />
            <p class="review-content">交易愉快，商品质量很好！</p>
          </div>
          <span class="review-time">2025-10-20</span>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue"


// 模拟评分数据
const dummyRatings = ref([4.5, 5, 3.5])
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  background-color: #0b1e3a;
  color: white;
  padding: 40px 60px;
  box-sizing: border-box;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 30px;
  margin-bottom: 40px;
}

.avatar {
  border: 3px solid #1e3a8a;
}

.user-info .username {
  margin: 0;
  font-size: 24px;
  font-weight: bold;
}

.user-info .desc {
  margin: 6px 0;
  color: #a0aec0;
}

.edit-btn {
  margin-top: 10px;
}

.profile-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 25px;
  margin-bottom: 50px;
}

.stat-card {
  text-align: center;
  background-color: #11284d;
  color: white;
  border: none;
  border-radius: 12px;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-card .el-icon {
  font-size: 28px;
  margin-bottom: 10px;
  color: #60a5fa;
}

.stat-value {
  font-size: 22px;
  font-weight: bold;
}

.stat-label {
  color: #9ca3af;
}

.recent-section h3 {
  margin-bottom: 20px;
  color: #93c5fd;
}

.review-card {
  background-color: #102c58;
  margin-bottom: 15px;
  border: none;
}

.review-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.review-text {
  flex: 1;
  margin-left: 15px;
}

.review-username {
  margin: 0;
  font-weight: bold;
}

.review-content {
  margin: 4px 0 0 0;
  color: #cbd5e1;
}

.review-time {
  font-size: 12px;
  color: #9ca3af;
}

.el-rate {
  margin: 6px 0;
}
</style>
