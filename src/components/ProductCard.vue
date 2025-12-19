<template>
  <el-card class="p-card" :body-style="{ padding: '0px' }" shadow="hover">
    <div class="img-box">
      <el-image :src="item.image_url" fit="cover" />
      <div v-if="item.status === 'sold'" class="overlay">已售出</div>
    </div>
    
    <div class="content">
      <div class="price-tag">¥{{ item.price }}</div>
      <h4 class="title">{{ item.name }}</h4>
      
      <div class="footer">
        <template v-if="!isMine">
          <span class="seller">ID: {{ item.seller_id }}</span>
          <el-button size="small" class="btn-favor" @click.stop="handleFavor(item)">收藏</el-button>
          <el-button size="small" class="btn-buy" @click.stop="handleBuy">购买</el-button>
        </template>
        
        <template v-else>
          <el-button size="small" class="btn-edit" plain type="primary" @click.stop="handleEdit">编辑</el-button>
          <el-button size="small" class="btn-delete" plain type="danger" @click.stop="handleDelete">删除</el-button>
        </template>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { ElMessage, ElMessageBox } from 'element-plus'
import { buyProduct, deleteProduct, favoriteProduct } from '@/api/index'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
const userStore = useUserStore()
const router = useRouter()
const props = defineProps({
  item: Object,
  isMine: Boolean // 是否为“我的商品”模式
})
const emit = defineEmits(['refresh'])

const handleBuy = async () => {
  try {
    await buyProduct(props.item.id)
    ElMessage.success('购买成功！')
    emit('refresh')
  } catch (e) {}
}

const handleDelete = () => {
  ElMessageBox.confirm('确定要删除这件商品吗？', '警告', { type: 'error' }).then(async () => {
    await deleteProduct(props.item.id)
    ElMessage.success('已删除')
    emit('refresh')
  })
}

const handleEdit = () => {
  router.push(`/modify_product/${props.item.id}`)
}

const handleFavor = async (item) => {
  if (!userStore.token) return router.push('/login')
  try {
    const res = await favoriteProduct(item.id)
    ElMessage.success(res.message || '已加入收藏夹')
  } catch (e) {
    
  }
}
</script>

<style scoped>
.p-card {
  border-radius: 12px;
  margin-bottom: 20px;
  border: none;  
  cursor: pointer; /* 鼠标悬停变手型 */;
}
.p-card:hover {
  transform: translateY(-5px); /* 悬停浮起效果 */
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  border : 1px solid #ff4d4f;
}
.product-card:hover {
  transform: translateY(-5px); /* 悬停浮起效果 */
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.img-box {
  height: 180px;
  position: relative;
  background: #f5f5f5;
}
.img-box .el-image { width: 100%; height: 100%; }
.overlay {
  position: absolute; top:0; left:0; right:0; bottom:0;
  background: rgba(0,0,0,0.4); color:white;
  display:flex; align-items:center; justify-content:center;
}
.content { padding: 12px; }
.price-tag { color: #ff4d4f; font-size: 18px; font-weight: bold; }
.title {
  margin: 8px 0; font-size: 14px; color: #333;
  height: 40px; overflow: hidden;
}
.footer {
  display: flex; justify-content: space-between; align-items: center;
  margin-top: 10px; padding-top: 10px; border-top: 1px dashed #eee;
}
.seller { font-size: 12px; color: #999; }
.btn-buy {
  background-color: #ff6600; border: none; color: white; border-radius: 15px;
}
.btn-favor { border-color: #ff6600; color: #ff6600; border-radius: 15px; margin-left: 30%; }
.btn-buy:hover { background-color: #ff8533; }

.btn-edit { border-color: #ff6600; color: #ff6600; border-radius: 15px; }
.btn-delete { border-color: #ff6600; color: #ff6600; border-radius: 15px; }

</style>