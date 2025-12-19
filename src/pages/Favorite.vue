<template>
  <div class="favorites-container">
    <div class="top-nav">
      <el-button link @click="router.back()" class="back-link">
        <el-icon><ArrowLeft /></el-icon>
        返回
      </el-button>
      <h2 class="page-title">我的收藏夹</h2>
    </div>

    <el-card class="list-card" shadow="never">
      <div v-loading="loading" class="content-wrapper">
        <div v-if="favoriteList.length > 0" class="fav-grid">
          <div v-for="item in favoriteList" :key="item.id" class="fav-item">
            <div class="img-container">
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
              <div v-if="item.status === 'sold'" class="sold-status-tag">
                已售出
              </div>
            </div>

            <div class="prod-details">
              <h4 class="prod-name" @click="goDetail(item.id)">{{ item.name }}</h4>
              <div class="price-action">
                <span 
                  class="price" 
                  :class="{ 'is-sold': item.status === 'sold' }"
                >
                  ¥{{ item.price }}
                </span>
                
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
// ... (script 部分逻辑保持不变)
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, Picture, Delete } from '@element-plus/icons-vue'
import { getFavorites, getProductDetail, deleteFavorite } from '@/api/index'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const loading = ref(false)
const favoriteList = ref([])

const fetchFavorites = async () => {
  loading.value = true
  try {
    const res = await getFavorites()
    const favIds = res.favorites || []
    
    // 如果后端能直接返回带有 status 的商品简版列表会更好
    const detailPromises = favIds.map(item => getProductDetail(item.product_id))
    const details = await Promise.all(detailPromises)
    
    favoriteList.value = details
  } catch (err) {
    console.error('获取收藏失败:', err)
  } finally {
    loading.value = false
  }
}

const handleRemove = (id) => {
  ElMessageBox.confirm('确定要从收藏夹移除该商品吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const res = await deleteFavorite(id)
      ElMessage.success(res.message || '已取消收藏')
      favoriteList.value = favoriteList.value.filter(item => item.id !== id)
    } catch (err) {}
  })
}

const goDetail = (id) => router.push(`/product/${id}`)

onMounted(fetchFavorites)
</script>

<style scoped>
/* --- 样式部分修改与新增 --- */

.img-container {
  position: relative;
  width: 100%;
  height: 180px;
  overflow: hidden;
}

.prod-img {
  width: 100%;
  height: 100%;
  cursor: pointer;
  background: #f5f5f5;
  transition: filter 0.3s;
}

/* 如果售罄，图片可以加一点淡化滤镜 */
.is-sold-img {
  filter: grayscale(0.5);
}

.sold-status-tag {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.3); /* 半透明遮罩 */
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 16px;
  letter-spacing: 2px;
  pointer-events: none; /* 穿透点击，让图片依然可点去详情页 */
}

/* 核心价格样式 */
.price {
  font-size: 18px;
  font-weight: bold;
  color: #ff6600;
  transition: all 0.3s;
}

.price.is-sold {
  color: #999 !important;
  text-decoration: line-through; /* 删除线 */
}

/* --- 其余原有样式保持 --- */
.favorites-container { max-width: 1000px; margin: 30px auto; padding: 0 20px; }
.top-nav { display: flex; align-items: center; gap: 20px; margin-bottom: 20px; }
.back-link { font-size: 15px; color: #666; }
.page-title { margin: 0; font-size: 20px; color: #333; }
.list-card { border-radius: 12px; border: none; min-height: 400px; }
.fav-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 20px; }
.fav-item { border: 1px solid #f0f0f0; border-radius: 8px; overflow: hidden; transition: all 0.3s; background: #fff; position: relative;}
.fav-item:hover { transform: translateY(-5px); box-shadow: 0 6px 15px rgba(0,0,0,0.1); border-color: #ff9838; }
.prod-details { padding: 12px; }
.prod-name { margin: 0 0 10px; font-size: 14px; color: #333; height: 40px; line-height: 20px; cursor: pointer; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.price-action { display: flex; justify-content: space-between; align-items: center; }
.btn-orange { background-color: #ff6600; border-color: #ff6600; color: white; }
</style>