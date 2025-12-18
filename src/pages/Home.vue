<template>
  <div class="home-layout">
    <header class="navbar">
      <div class="nav-content">
        <div class="brand" @click="activeTab = 'all'">
          <el-icon :size="28" color="#ff6600"><Shop /></el-icon>
          <span>校园二货</span>
        </div>
        
        <div class="search-bar">
          <el-input
            v-model="searchQuery"
            placeholder="搜索宝贝名称、描述..."
            prefix-icon="Search"
            clearable
          />
        </div>

        <div class="user-actions">
          <el-button class="btn-orange" icon="Plus" @click="handleCreate">发布商品</el-button>
          
          <el-badge :value="msgCount" :hidden="msgCount === 0" class="msg-badge">
            <el-button link class="icon-btn" @click="router.push('/messages')">
              <el-icon :size="22"><ChatDotRound /></el-icon>
            </el-button>
          </el-badge>

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
                <el-dropdown-item command="favorites">收藏夹</el-dropdown-item>
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
          <div class="product-grid" v-loading="loading">
            <el-row :gutter="20">
              <el-col v-for="item in filteredProducts" :key="item.id" :xs="12" :sm="8" :md="6" :lg="4.8">
                <ProductCard :item="item" @refresh="fetchData" />
              </el-col>
            </el-row>
            <el-empty v-if="filteredProducts.length === 0" description="暂无商品" />
          </div>
        </el-tab-pane>

        <el-tab-pane label="我发布的" name="mine">
          <div class="product-grid" v-loading="loading">
            <el-row :gutter="20">
              <el-col v-for="item in myProducts" :key="item.id" :xs="12" :sm="8" :md="6" :lg="4.8">
                <ProductCard :item="item" is-mine @refresh="fetchData" />
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
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Shop, Search, Plus, ChatDotRound } from '@element-plus/icons-vue'
import { getProducts, getMsgs } from '@/api/index'
import { useUserStore } from '@/stores/user'
import ProductCard from '@/components/ProductCard.vue' // 建议将卡片抽离

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const activeTab = ref('all')
const searchQuery = ref('')
const products = ref([])
const msgCount = ref(0)

// 获取数据
const fetchData = async () => {
  loading.value = true
  try {
    const [prodRes, msgRes] = await Promise.all([getProducts(), getMsgs()])
    products.value = prodRes.products || []
    msgCount.value = msgRes.messages?.length || 0
  } catch (err) {}
  loading.value = false
}

// 过滤全站商品
const filteredProducts = computed(() => {
  return products.value.filter(p => 
    p.name.includes(searchQuery.value) && p.status !== 'deleted'
  )
})

// 过滤“我的商品” (根据当前登录用户ID)
const myProducts = computed(() => {
  return products.value.filter(p => p.seller_id === userStore.userInfo.id)
})

const handleCommand = (c) => {
  if(c === 'logout') { userStore.logout(); router.push('/login'); }
  else router.push(`/${c}`)
}

const handleCreate = () => router.push('/create_product')

onMounted(fetchData)
</script>

<style scoped>
/* 统一橙色主题变量 */
:deep(:root) {
  --market-orange: #ff6600;
  --market-orange-light: #ff9838;
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

.msg-badge {
  margin-right: 15px;
  display: flex;
  align-items: center;
}

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

/* 选项卡样式覆盖 */
.market-tabs {
  margin-top: 20px;
}
:deep(.el-tabs__item.is-active) { color: #ff6600; font-size: 18px; font-weight: bold; }
:deep(.el-tabs__active-bar) { background-color: #ff6600; height: 3px; }
:deep(.el-tabs__nav-wrap::after) { background-color: transparent; }

.main-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px 40px;
}

.product-grid { margin-top: 20px; }
</style>