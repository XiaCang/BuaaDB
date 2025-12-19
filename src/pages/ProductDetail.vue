<template>
  <div class="detail-container" v-loading="pageLoading">
    <div class="top-nav">
      <el-button link @click="router.back()" class="back-link">
        <el-icon><ArrowLeft /></el-icon>
        返回上一页
      </el-button>
    </div>

    <el-row :gutter="30" v-if="product.id">
      <el-col :xs="24" :md="14" :lg="16">
        <el-card class="image-card" shadow="never">
          <div class="image-wrapper">
            <el-image :src="product.image_url" fit="contain" class="product-img">
               <template #error>
                  <div class="image-slot">
                    <el-icon><Picture /></el-icon>
                    <span>图片加载失败</span>
                  </div>
               </template>
            </el-image>
            <div v-if="product.status !== 'active'" class="status-overlay">
              {{ statusMap[product.status] }}
            </div>
          </div>
        </el-card>

        <el-card class="seller-card" shadow="hover">
          <div class="seller-info">
            <el-avatar :size="50" :src="seller_avatar" />
            <div class="seller-text">
              <div class="seller-name">{{ seller.nickname }}</div>
              <div class="seller-meta">卖家 ID: {{ product.seller_id }}</div>
            </div>
            <el-button type="primary" plain round size="small" icon="ChatDotRound" @click="handleContactSeller">
              联系卖家
            </el-button>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :md="10" :lg="8">
        <el-card class="info-card" shadow="never">
          <h1 class="product-title">{{ product.name }}</h1>
          
          <div class="price-box">
            <span class="currency">¥</span>
            <span class="price-num">{{ product.price }}</span>
          </div>

          <div class="meta-info">
            <span>发布于: {{ formatDate(product.created_at) }}</span>
            <el-divider direction="vertical" />
            <span>状态: <el-tag size="small" :type="statusColor[product.status]">{{ statusMap[product.status] }}</el-tag></span>
          </div>

          <el-divider content-position="left">商品详情</el-divider>
          
          <div class="description-box">
            <p>{{ product.description }}</p>
          </div>

          <div class="action-buttons">
            <el-button 
              class="buy-btn btn-orange-gradient" 
              size="large" 
              :disabled="product.status !== 'active'"
              :loading="buyLoading"
              @click="handleBuy"
            >
              {{ product.status === 'active' ? '立即购买' : statusMap[product.status] }}
            </el-button>
            <el-button 
              class="fav-btn" 
              size="large" 
              icon="Star" 
              plain
              @click="handleFavorite"
            >
              收藏
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="comment-section" shadow="never" v-if="product.id">
      <template #header>
        <div class="comment-header">
          <span>互动评论 ({{ comments.length }})</span>
        </div>
      </template>

      <div class="comment-input-box">
        <el-input
          v-model="commentContent"
          type="textarea"
          :rows="3"
          placeholder="对这件宝贝有疑问？问问卖家吧..."
          maxlength="200"
          show-word-limit
        />
        <div class="submit-bar">
          <el-button type="primary" class="btn-orange" size="small" :loading="commentLoading" @click="handlePublishComment">
            发布评论
          </el-button>
        </div>
      </div>

      <el-divider />

        <div class="comment-list">
        <el-empty v-if="comments.length === 0" description="还没有人评论，快来抢沙发~" />
        
        <div v-else>
            <div v-for="(comment, index) in comments" :key="comment.comment_id">
            <div class="comment-item">
                <div class="comment-left">
                <el-avatar :size="40" :src="comment.avatar_url" class="comment-avatar">
                    {{ comment.nickname?.charAt(0) }}
                </el-avatar>
                </div>

                <div class="comment-right">
                <div class="comment-meta">
                    <span class="comment-nickname">{{ comment.nickname || '匿名用户' }}</span>
                    <span class="comment-time">{{ formatDate(comment.created_at) }}</span>
                </div>
                <div class="comment-content">
                    {{ comment.content }}
                </div>
                </div>
            </div>
            
            <el-divider v-if="index !== comments.length - 1" class="comment-divider" />
            </div>
        </div>
        </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Star, ChatDotRound, Picture } from '@element-plus/icons-vue'
import { getProductDetail, buyProduct, favoriteProduct, getComments, publishComment, getUserInfo } from '@/api/index'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const pageLoading = ref(true)
const buyLoading = ref(false)
const commentLoading = ref(false)
const product = ref({})
const comments = ref([])
const commentContent = ref('')
const seller = ref({})

const seller_avatar = ref('https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png')

const statusMap = {
  active: '在售',
  inactive: '已下架',
  deleted: '已删除',
  sold: '已售出'
}

const statusColor = {
  active: 'success',
  inactive: 'info',
  deleted: 'danger',
  sold: 'warning'
}

// 初始化数据
const initData = async () => {
  const productId = route.params.id
  if (!productId) return
  
  pageLoading.value = true
  try {
    // 并行请求商品详情和评论
    const [prodRes, commentRes] = await Promise.all([
      getProductDetail(productId),
      getComments(productId)
    ])
    product.value = prodRes

    console.log("In ProductDetail : product = " , product.value);
    // 请求卖家信息
    const sellerId = product.value.seller_id
    const sellerRes = await getUserInfo(sellerId)

    console.log("In ProductDetail : seller = " , sellerRes);
    
    seller.value = sellerRes
    seller_avatar.value = sellerRes.avatar_url

    comments.value = commentRes.comments || [];

    console.log("In ProductDetail : comments = " , comments.value);
  } catch (error) {
    console.error('加载失败', error)
    ElMessage.error('商品信息加载失败')
  } finally {
    pageLoading.value = false
  }
}

// 购买操作
const handleBuy = () => {
  if (!userStore.token) {
     ElMessage.warning('请先登录')
     return router.push('/login')
  }

  ElMessageBox.confirm(
    `确认以 ¥${product.value.price} 的价格购买此商品吗？`,
    '购买确认',
    { confirmButtonText: '确认支付', cancelButtonText: '取消', type: 'warning' }
  ).then(async () => {
    buyLoading.value = true
    try {
      const res = await buyProduct(product.value.id)
      ElMessage.success(res.message || '购买成功！')
      initData() // 刷新状态
    } finally {
      buyLoading.value = false
    }
  })
}

// 收藏操作
const handleFavorite = async () => {
  if (!userStore.token) return router.push('/login')
  try {
    const res = await favoriteProduct(product.value.id)
    ElMessage.success(res.message || '已加入收藏夹')
  } catch (e) {}
}

// 发布评论
const handlePublishComment = async () => {
  if (!userStore.token) return router.push('/login')
  if (!commentContent.value.trim()) return ElMessage.warning('请输入评论内容')

  commentLoading.value = true
  try {
    const res = await publishComment({
      product_id: product.value.id,
      content: commentContent.value
    })
    ElMessage.success(res.message || '评论发布成功')
    commentContent.value = '' // 清空输入框
    // 重新加载评论列表
    const commentRes = await getComments(product.value.id)
    comments.value = commentRes.comments || []
  } finally {
    commentLoading.value = false
  }
}

// 联系卖家 (TODO)
const handleContactSeller = () => {
  if (!userStore.token) return router.push('/login')
  ElMessage.info('私信功能开发中，敬请期待！')
  // 未来实现：跳转到消息页面并选中该卖家
  // router.push({ path: '/messages', query: { targetId: product.value.seller_id }})
}

const formatDate = (str) => {
  if(!str) return ''
  return new Date(str).toLocaleString()
}

onMounted(initData)
</script>

<style scoped>
.detail-container {
  max-width: 1100px;
  margin: 20px auto;
  padding: 0 20px 40px;
}

.top-nav { margin-bottom: 20px; }
.back-link { font-size: 15px; color: #666; }
.back-link:hover { color: #ff6600; }

/* 左侧样式 */
.image-card {
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 20px;
  background: #f8f9fa;
  border: none;
}

.image-wrapper {
  position: relative;
  height: 450px; /* 固定高度，适配不同比例图片 */
  display: flex;
  align-items: center;
  justify-content: center;
}

.product-img {
  width: 100%;
  height: 100%;
}

.image-slot {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: #999;
  font-size: 14px;
}
.image-slot .el-icon { font-size: 40px; margin-bottom: 10px; }

.status-overlay {
  position: absolute;
  top: 20px; left: 20px;
  background: rgba(0,0,0,0.7);
  color: white;
  padding: 5px 15px;
  border-radius: 20px;
  font-weight: bold;
}

.seller-card {
  border-radius: 12px;
  border: none;
}

.seller-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.seller-text { flex: 1; }
.seller-name { font-weight: bold; font-size: 16px; color: #333; }
.seller-meta { font-size: 12px; color: #999; margin-top: 4px; }

/* 右侧样式 */
.info-card {
  border-radius: 12px;
  border: none;
  height: 100%; /* 让它和左侧等高 */
  display: flex;
  flex-direction: column;
}

.product-title {
  margin: 0 0 20px;
  font-size: 24px;
  line-height: 1.4;
  color: #333;
}

.price-box {
  color: #ff6600;
  margin-bottom: 20px;
  display: flex;
  align-items: baseline;
}

.currency { font-size: 24px; font-weight: bold; margin-right: 4px;}
.price-num { font-size: 48px; font-weight: 800; line-height: 1;}

.meta-info {
  color: #999;
  font-size: 13px;
  margin-bottom: 25px;
}

.description-box {
  color: #666;
  line-height: 1.8;
  font-size: 15px;
  white-space: pre-wrap; /* 保留换行符 */
  flex: 1; /* 占满剩余空间 */
  margin-bottom: 30px;
}

.action-buttons {
  display: flex;
  gap: 15px;
}

.buy-btn {
  flex: 2;
  font-size: 18px;
  border-radius: 8px;
  border: none;
}

.fav-btn {
  flex: 1;
  font-size: 18px;
  border-radius: 8px;
}
.fav-btn:hover {
  color: #ff6600;
  border-color: #ff6600;
  background-color: #fff5e6;
}

/* 评论区样式 */
.comment-section {
  margin-top: 30px;
  border-radius: 12px;
  border: none;
}

.comment-header { font-size: 18px; font-weight: bold; }

.comment-input-box { margin-bottom: 20px; }
.submit-bar {
  display: flex;
  justify-content: flex-end;
  margin-top: 10px;
}


.comment-item-card {
  border: none;
  background: #fcfcfc;
}

.comment-user {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
  font-size: 14px;
}

.comment-sender-id { color: #666; font-weight: 500; }

.comment-content {
  margin: 0;
  color: #333;
  line-height: 1.6;
}

.comment-list {
  padding: 20px 0;
}

.comment-item {
  display: flex;
  gap: 16px; /* 头像和内容之间的间距 */
  padding: 10px 0;
}

/* 左侧头像固定宽度 */
.comment-left {
  flex-shrink: 0;
}

.comment-avatar {
  background-color: #ff9838;
  border: 1px solid #fff2e6;
}

/* 右侧内容自适应 */
.comment-right {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.comment-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.comment-nickname {
  font-size: 15px;
  font-weight: 600;
  color: #333;
}

.comment-time {
  font-size: 12px;
  color: #999;
}

.comment-content {
  font-size: 14px;
  line-height: 1.6;
  color: #555;
  word-break: break-all; /* 防止长文本撑破布局 */
}

/* 分割线样式微调 */
.comment-divider {
  margin: 15px 0;
  border-top-color: #e3e1e1;
}

/* 响应式调整：手机端头像稍微缩小 */
@media (max-width: 480px) {
  .comment-item {
    gap: 12px;
  }
  .comment-nickname {
    font-size: 14px;
  }
}

/* 通用主题色类 */
.btn-orange-gradient {
  background: linear-gradient(90deg, #ff9838, #ff6600);
  color: white;
}
.btn-orange-gradient:hover {
  opacity: 0.9;
  color: white;
}
.btn-orange {
  background-color: #ff6600; border-color: #ff6600;
}
.btn-orange:hover {
  background-color: #ff8533; border-color: #ff8533;
}

/* 响应式调整 */
@media (max-width: 992px) {
  .image-wrapper { height: 350px; }
  .info-card { margin-top: 20px; height: auto; }
  .price-num { font-size: 36px; }
}
</style>