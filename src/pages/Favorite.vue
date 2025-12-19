<template>
  <div class="favorites-container">
    <div class="top-nav">
      <el-button link @click="router.back()" class="back-link">
        <el-icon><ArrowLeft /></el-icon>
        返回个人中心
      </el-button>
      <h2 class="page-title">我的收藏夹</h2>
    </div>

    <el-card class="list-card" shadow="never">
      <div v-loading="loading" class="content-wrapper">
        <div v-if="favoriteList.length > 0" class="fav-grid">
          <div v-for="item in favoriteList" :key="item.id" class="fav-item">
            <el-image 
              class="prod-img" 
              :src="item.image_url" 
              fit="cover"
              @click="goDetail(item.id)"
            >
              <template #error>
                <div class="img-error"><el-icon><Picture /></el-icon></div>
              </template>
            </el-image>

            <div class="prod-details">
              <h4 class="prod-name" @click="goDetail(item.id)">{{ item.name }}</h4>
              <div class="price-action">
                <span class="price">¥{{ item.price }}</span>
                <el-button 
                  type="danger" 
                  icon="Delete" 
                  circle 
                  size="small" 
                  plain
                  @click="handleRemove(item.id)"
                  title="移除收藏"
                />
              </div>
            </div>
          </div>
        </div>

        <el-empty v-else description="收藏夹空空如也，去逛逛吧~">
          <el-button type="primary" class="btn-orange" @click="router.push('/')">去首页</el-button>
        </el-empty>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, Picture, Delete } from '@element-plus/icons-vue'
import { getFavorites, getProductDetail, deleteFavorite } from '@/api/index'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const loading = ref(false)
const favoriteList = ref([])

// 获取收藏夹完整数据
const fetchFavorites = async () => {
  loading.value = true
  try {
    // 1. 获取收藏的 ID 列表
    const res = await getFavorites()
    const favIds = res.favorites || []
    
    // 2. 由于列表只有 ID，需要拉取每个商品的详细信息进行展示
    // 注意：在实际生产环境中，建议后端优化此接口直接返回商品基本信息
    const detailPromises = favIds.map(item => getProductDetail(item.product_id))
    const details = await Promise.all(detailPromises)
    
    favoriteList.value = details
  } catch (err) {
    console.error('获取收藏失败:', err)
  } finally {
    loading.value = false
  }
}

// 移除收藏
const handleRemove = (id) => {
  ElMessageBox.confirm('确定要从收藏夹移除该商品吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const res = await deleteFavorite(id)
      ElMessage.success(res.message || '已取消收藏')
      // 更新本地列表，过滤掉已删除的
      favoriteList.value = favoriteList.value.filter(item => item.id !== id)
    } catch (err) {}
  })
}

const goDetail = (id) => router.push(`/product/${id}`)

onMounted(fetchFavorites)
</script>

<style scoped>
.favorites-container {
  max-width: 1000px;
  margin: 30px auto;
  padding: 0 20px;
}

.top-nav {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
}

.back-link { font-size: 15px; color: #666; }
.back-link:hover { color: #ff6600; }
.page-title { margin: 0; font-size: 20px; color: #333; }

.list-card {
  border-radius: 12px;
  border: none;
  min-height: 400px;
}

/* 收藏网格布局 */
.fav-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.fav-item {
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s;
  background: #fff;
}

.fav-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 15px rgba(0,0,0,0.1);
  border-color: #ff9838;
}

.prod-img {
  width: 100%;
  height: 180px;
  cursor: pointer;
  background: #f5f5f5;
}

.img-error {
  display: flex; align-items: center; justify-content: center;
  height: 100%; color: #ccc; font-size: 30px;
}

.prod-details {
  padding: 12px;
}

.prod-name {
  margin: 0 0 10px;
  font-size: 14px;
  color: #333;
  height: 40px;
  line-height: 20px;
  cursor: pointer;
  /* 两行截断 */
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.prod-name:hover { color: #ff6600; }

.price-action {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.price {
  font-size: 18px;
  font-weight: bold;
  color: #ff6600;
}

.btn-orange {
  background-color: #ff6600;
  border-color: #ff6600;
  color: white;
}
.btn-orange:hover { background-color: #ff8533; opacity: 0.9; }

/* 响应式适配 */
@media (max-width: 480px) {
  .fav-grid {
    grid-template-columns: 1fr 1fr; /* 手机端一行两个 */
    gap: 10px;
  }
  .prod-img { height: 140px; }
}
</style>