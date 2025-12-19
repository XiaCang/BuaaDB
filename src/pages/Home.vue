<template>
  <div class="home-layout">
    <header class="navbar">
      <div class="nav-content">
        <div class="brand" @click="activeTab = 'all'">
          <el-icon :size="28" color="#ff6600"><Shop /></el-icon>
          <span>校园二货</span>
        </div>
        

        <div class="user-actions">
          <el-button class="btn-orange" icon="Plus" @click="handleCreate">发布商品</el-button>
          <el-button link class="icon-btn" @click="router.push('/messages')">
            <el-icon :size="22"><ChatDotRound /></el-icon>
          </el-button>
          <el-divider direction="vertical" />

          <el-dropdown @command="handleCommand">
            <span class="user-profile">
              <el-avatar :size="32" :src="userStore.userInfo.avatar_url" />
              <span class="nickname">{{ userStore.userInfo.nickname || '用户' }}</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人资料</el-dropdown-item>
                <el-dropdown-item command="orders">我的订单</el-dropdown-item>
                <el-dropdown-item command="favorite">收藏夹</el-dropdown-item>
                <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </header>

    <main class="main-container">
      <el-tabs v-model="activeTab" class="market-tabs">
        <el-tab-pane label="全站市场" name="all">
          <!-- 分类筛选区域 -->
          <div class="filter-container">
            <div class="filter-group">
              <el-select 
                v-model="categoryFilter" 
                placeholder="全部类别" 
                clearable
                class="filter-select"
              >
                <el-option 
                  v-for="category in categories" 
                  :key="category.category_id" 
                  :label="category.category_name" 
                  :value="category.category_id" 
                />
              </el-select>
              <el-input
                v-model="searchQuery"
                placeholder="搜索商品..."
                prefix-icon="Search"
                clearable
                class="filter-search"
              />
            </div>
            <div class="filter-status">
              <span class="total-text">共 {{ filteredProducts.length }} 个商品</span>
            </div>
          </div>

          <div class="product-grid" v-loading="loading">
            <el-row :gutter="20">
              <el-col v-for="item in filteredProducts" :key="item.id" :xs="12" :sm="8" :md="6" :lg="4.8">
                <ProductCard :item="item" @refresh="fetchData" @click="goToDetail(item.id)"/>
              </el-col>
            </el-row>
            <el-empty v-if="filteredProducts.length === 0" description="暂无商品" />
          </div>
        </el-tab-pane>

        <el-tab-pane label="我发布的" name="mine">
          <div class="filter-container">
            <div class="filter-status">
              <span class="total-text">共 {{ myProducts.length }} 个商品</span>
            </div>
          </div>
          
          <div class="product-grid" v-loading="loading">
            <el-row :gutter="20">
              <el-col v-for="item in myProducts" :key="item.id" :xs="12" :sm="8" :md="6" :lg="4.8">
                <ProductCard :item="item" is-mine @refresh="fetchData" @click="goToDetail(item.id)"/>
              </el-col>
            </el-row>
            <el-empty v-if="myProducts.length === 0" description="你还没有发布过商品哦" />
          </div>
        </el-tab-pane>
      </el-tabs>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Shop, Search, Plus, ChatDotRound } from '@element-plus/icons-vue'
import { getProducts, getMsgs ,getCategories} from '@/api/index'
import { useUserStore } from '@/stores/user'
import ProductCard from '@/components/ProductCard.vue'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const activeTab = ref('all')
const searchQuery = ref('')
const products = ref([])
const msgCount = ref(0)
const categories = ref([])
const categoryFilter = ref('')

// 监听 tab 切换，重置筛选条件
watch(() => activeTab.value, (newTab) => {
  if (newTab === 'all') {
    // 保留全站市场的筛选条件
  } else {
    // 切换到"我发布的"时清空筛选
    searchQuery.value = ''
    categoryFilter.value = ''
  }
})

// 获取数据
const fetchData = async () => {
  loading.value = true
  try {
    const [prodRes, msgRes] = await Promise.all([getProducts(), getMsgs()])
    products.value = prodRes.products || []
    
    const categoriesRes = await getCategories()
    categories.value = categoriesRes.categories || []
    
    // 添加"全部"选项到分类列表开头
    categories.value.unshift({ 
      category_id: '', 
      category_name: '全部类别' 
    })
    
    msgCount.value = msgRes.messages?.length || 0
  } catch (err) {
    console.error('获取数据失败:', err)
  }
  loading.value = false
}

// 过滤全站商品
const filteredProducts = computed(() => {
  return products.value.filter(p => {
    // 过滤已删除商品
    if (p.status === 'deleted') return false
    
    // 搜索关键词过滤
    const searchMatch = !searchQuery.value || 
      (p.name && p.name.includes(searchQuery.value)) ||
      (p.description && p.description.includes(searchQuery.value))
    
    // 分类过滤
    const categoryMatch = !categoryFilter.value || 
      p.category_id === categoryFilter.value
    
    return searchMatch && categoryMatch
  })
})

// 过滤"我的商品"
const myProducts = computed(() => {
  return products.value.filter(p => 
    p.seller_id === userStore.userInfo.user_name && 
    p.status !== 'deleted'
  )
})

const handleCommand = (c) => {
  if(c === 'logout') { 
    userStore.logout(); 
    router.push('/login'); 
  } else {
    router.push(`/${c}`)
  }
}

const handleCreate = () => router.push({ name: 'create_product' })
const goToDetail = (id) => router.push(`/product/${id}`)

onMounted(fetchData)
</script>

<style scoped>
  
/* 统一橙色主题变量 */
:root {
  --market-orange: #ff6600;
  --market-orange-light: #ff9838;
  --market-gray-light: #f5f5f5;
  --market-border: #e8e8e8;
}

.home-layout {
  background-color: #fcfcfc;
  min-height: 100vh;
}

/* 导航栏 */
.navbar {
  background: #fff;
  height: 70px;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 12px rgba(0,0,0,0.04);
  position: sticky;
  top: 0;
  z-index: 1000;
  
}

.nav-content {
  width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  padding: 0 20px;
  justify-content: space-between;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  font-size: 22px;
  font-weight: bold;
  color: #ff6600;
  min-width: 150px;
}

.search-bar {
  flex: 1;
  padding: 0 50px;
}

.user-actions {
  display: flex;
  align-items: center;
  flex-direction: row;
}

/* 统一按钮样式 */
.btn-orange {
  background: linear-gradient(90deg, #ff9838, #ff6600);
  border: none;
  color: white;
  border-radius: 20px;
  padding: 8px 20px;
  transition: all 0.3s;
}

.btn-orange:hover {
  opacity: 0.9;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(255, 102, 0, 0.3);
}

.icon-btn {
  color: #666;
  margin: 0 10px;
}

.icon-btn:hover { color: #ff6600; }

/* 用户信息 */
.user-profile {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 5px 12px;
  border-radius: 25px;
}
.user-profile:hover { background: #fff5e6; }

/* 选项卡样式 */
.market-tabs {
  margin-top: 20px;
}
:deep(.el-tabs__item.is-active) { 
  color: #ff6600; 
  font-size: 18px; 
  font-weight: bold; 
}
:deep(.el-tabs__active-bar) { 
  background-color: #ff6600; 
  height: 3px; 
}
:deep(.el-tabs__nav-wrap::after) { 
  background-color: transparent; 
}

/* 主容器 */
.main-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px 40px;
}

/* 筛选区域样式 */
.filter-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 20px 0;
  padding: 15px 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.filter-group {
  display: flex;
  gap: 15px;
  align-items: center;
}

.filter-select {
  width: 200px;
}

.filter-search {
  width: 300px;
}

/* 自定义搜索框样式 */
:deep(.custom-search .el-input__wrapper),
:deep(.filter-search .el-input__wrapper) {
  border-radius: 20px;
  border: 1px solid var(--market-border);
  background: var(--market-gray-light);
}

:deep(.filter-select .el-input__wrapper) {
  border-radius: 20px;
  border: 1px solid var(--market-border);
  background: white;
}

:deep(.filter-select .el-input__wrapper:hover),
:deep(.filter-search .el-input__wrapper:hover) {
  border-color: var(--market-orange-light);
}

:deep(.filter-select .el-input__wrapper.is-focus),
:deep(.filter-search .el-input__wrapper.is-focus) {
  border-color: var(--market-orange);
  box-shadow: 0 0 0 1px var(--market-orange-light);
}

/* 状态文本 */
.filter-status {
  display: flex;
  align-items: center;
}

.total-text {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

/* 商品网格 */
.product-grid { 
  margin-top: 20px; 
}

:deep(.el-empty__description) {
  color: #999;
  margin-top: 10px;
}
</style>