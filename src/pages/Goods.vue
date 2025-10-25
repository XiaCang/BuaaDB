<template>
  <div class="goods-page">
    <!-- 搜索与分类栏 -->
    <div class="top-bar">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索商品名称或描述"
        class="search-input"
        clearable
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
        <template #append>
          <el-button type="primary" @click="onSearch">搜索</el-button>
        </template>
      </el-input>

      <el-tabs v-model="activeCategory" type="card" class="category-tabs">
        <el-tab-pane label="全部" name="all" />
        <el-tab-pane label="电子产品" name="electronics" />
        <el-tab-pane label="书籍" name="books" />
        <el-tab-pane label="服饰" name="clothes" />
        <el-tab-pane label="生活用品" name="life" />
        <el-tab-pane label="其他" name="other" />
      </el-tabs>
    </div>

    <!-- 商品卡片展示区 -->
    <div class="goods-grid">
      <el-card
        v-for="(item, index) in dummyGoods"
        :key="index"
        class="goods-card"
        shadow="hover"
      >
        <img :src="item.image" class="goods-img" />
        <div class="goods-info">
          <h3 class="goods-name">{{ item.name }}</h3>
          <p class="goods-desc">{{ item.desc }}</p>
          <div class="goods-footer">
            <span class="goods-price">￥{{ item.price }}</span>
            <el-button size="small" type="primary">
              <el-icon><ShoppingCart /></el-icon>
              加入购物车
            </el-button>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue"
import { Search, ShoppingCart } from "@element-plus/icons-vue"

// 搜索与分类
const searchKeyword = ref("")
const activeCategory = ref("all")

// 模拟商品数据
const dummyGoods = ref([
  {
    name: "二手iPhone 13",
    desc: "95新，128GB，性能完好",
    price: 3500,
    image: "https://via.placeholder.com/250x200?text=iPhone+13",
  },
  {
    name: "编程书籍《深入理解计算机系统》",
    desc: "正版书籍，笔记较少",
    price: 60,
    image: "https://via.placeholder.com/250x200?text=CSAPP",
  },
  {
    name: "蓝牙耳机",
    desc: "续航6小时，音质清晰",
    price: 120,
    image: "https://via.placeholder.com/250x200?text=Earbuds",
  },
  {
    name: "运动外套",
    desc: "男女同款，M码，九成新",
    price: 90,
    image: "https://via.placeholder.com/250x200?text=Jacket",
  },
])

// 空事件
function onSearch() {
  console.log("搜索关键词：", searchKeyword.value)
}
</script>

<style scoped>
.goods-page {
  min-height: 100vh;
  background-color: #0b1e3a;
  color: white;
  padding: 40px 60px;
  box-sizing: border-box;
}

/* 顶部搜索与分类栏 */
.top-bar {
  margin-bottom: 30px;
}

.search-input {
  max-width: 600px;
  margin-bottom: 20px;
}

.category-tabs {
  color: white;
}

/* 商品卡片区 */
.goods-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 25px;
}

.goods-card {
  background-color: #102c58;
  color: white;
  border: none;
  border-radius: 12px;
  overflow: hidden;
  transition: transform 0.25s ease;
}

.goods-card:hover {
  transform: translateY(-5px);
}

.goods-img {
  width: 100%;
  height: 180px;
  object-fit: cover;
  border-bottom: 1px solid #1e3a8a;
}

.goods-info {
  padding: 15px;
}

.goods-name {
  font-size: 18px;
  margin: 0 0 5px 0;
  color: #f1f5f9;
}

.goods-desc {
  font-size: 14px;
  color: #a0aec0;
  margin: 0 0 10px 0;
  height: 36px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.goods-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.goods-price {
  font-size: 18px;
  font-weight: bold;
  color: #60a5fa;
}
</style>
