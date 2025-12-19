<template>
  <div class="orders-container">
    <div class="top-nav">
      <el-button link @click="router.back()" class="back-link">
        <el-icon><ArrowLeft /></el-icon>
        返回个人中心
      </el-button>
      <h2 class="page-title">我的订单</h2>
    </div>

    <el-card class="order-list-card" shadow="never">
      <el-tabs v-model="statusFilter" class="order-tabs">
        <el-tab-pane label="全部订单" name="all" />
        <el-tab-pane label="进行中" name="active" />
        <el-tab-pane label="已完成" name="completed" />
      </el-tabs>

      <div v-loading="loading" class="list-wrapper">
        <div v-if="filteredOrders.length > 0">
          <div v-for="order in filteredOrders" :key="order.order_id" class="order-row">
            <div class="order-header">
              <span class="order-id">订单号: {{ order.order_id }}</span>
              <span class="order-time">{{ formatDate(order.created_at) }}</span>
            </div>
            
            <div class="order-body">
              <el-image 
                class="prod-img" 
                :src="order.img_url" 
                fit="cover"
              >
                <template #error>
                  <div class="img-error"><el-icon><Picture /></el-icon></div>
                </template>
              </el-image>

              <div class="prod-info">
                <h4 class="prod-name">{{ order.product_title || '商品名称加载中...' }}</h4>
                <p class="seller-id">卖家 ID: {{ order.seller_id }}</p>
              </div>

              <div class="order-price">
                <span class="price-label">实付款</span>
                <span class="price-val">¥{{ order.price }}</span>
              </div>

              <div class="order-status">
                <el-tag :type="getStatusTag(order.status)" effect="light">
                  {{ getStatusText(order.status) }}
                </el-tag>
              </div>

              <div class="order-actions">
                <el-button size="small" @click="goDetail(order.product_id)">查看详情</el-button>
                <el-button 
                  v-if="order.status === 'active'" 
                  size="small" 
                  type="primary" 
                  plain
                  @click="handleContact(order.seller_id)"
                >联系卖家</el-button>
              </div>
            </div>
          </div>
        </div>

        <el-empty v-else :description="statusFilter === 'all' ? '暂无订单记录' : '没有相关的订单'" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, Picture } from '@element-plus/icons-vue'
import { getOrders } from '@/api/index'
import { ElMessage } from 'element-plus'

const router = useRouter()
const loading = ref(false)
const orders = ref([])
const statusFilter = ref('all')

// 获取数据
const fetchOrders = async () => {
  loading.value = true
  try {
    const res = await getOrders()
    orders.value = res.orders || []

    console.log("In MyOrder : orders = " , orders.value);
    
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

// 筛选逻辑
const filteredOrders = computed(() => {
  if (statusFilter.value === 'all') return orders.value
  return orders.value.filter(o => o.order_status === statusFilter.value)
})

// 状态展示逻辑
const getStatusText = (status) => {
  const map = { active: '进行中', completed: '已完成', cancelled: '已取消' }
  return map[status] || status
}

const getStatusTag = (status) => {
  const map = { active: 'warning', completed: 'success', cancelled: 'info' }
  return map[status] || ''
}

const formatDate = (str) => str ? new Date(str).toLocaleString() : ''

const goDetail = (id) => router.push(`/product/${id}`)

const handleContact = (sellerId) => {
  ElMessage.info(`正在连接卖家 ${sellerId} ...`)
}

onMounted(fetchOrders)
</script>

<style scoped>
.orders-container {
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

.order-list-card {
  border-radius: 12px;
  border: none;
}

/* 订单行样式 */
.order-row {
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  margin-bottom: 20px;
  transition: all 0.3s;
}

.order-row:hover {
  border-color: #ff9838;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

.order-header {
  background-color: #fafafa;
  padding: 10px 20px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: #999;
}

.order-body {
  padding: 20px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
}

.prod-img {
  width: 80px;
  height: 80px;
  border-radius: 6px;
  background: #f5f5f5;
  flex-shrink: 0;
}

.img-error {
  display: flex; align-items: center; justify-content: center;
  height: 100%; color: #ccc; font-size: 24px;
}

.prod-info {
  flex: 1;
  padding: 0 20px;
  min-width: 200px;
}

.prod-name {
  margin: 0 0 8px;
  font-size: 16px;
  color: #333;
  /* 文本截断 */
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.seller-id { font-size: 12px; color: #999; margin: 0; }

.order-price {
  width: 120px;
  text-align: center;
  border-left: 1px solid #f0f0f0;
  border-right: 1px solid #f0f0f0;
}

.price-label { display: block; font-size: 12px; color: #999; }
.price-val { font-size: 18px; font-weight: bold; color: #333; }

.order-status {
  width: 120px;
  text-align: center;
}

.order-actions {
  width: 180px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: center;
}

/* 选项卡颜色覆盖 */
:deep(.el-tabs__item.is-active) { color: #ff6600; }
:deep(.el-tabs__active-bar) { background-color: #ff6600; }

/* 响应式适配 */
@media (max-width: 768px) {
  .order-price, .order-status {
    border: none;
    width: 50%;
    margin-top: 15px;
  }
  .order-actions {
    width: 100%;
    margin-top: 15px;
    flex-direction: row;
    justify-content: center;
  }
}
</style>