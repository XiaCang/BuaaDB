<template>
  <div>
    <el-card class="p-card" :body-style="{ padding: '0px' }" shadow="hover">
      <div class="img-box">
        <el-image :src="item.image_url" fit="cover" />
        <div v-if="item.status === 'sold'" class="overlay">已售出</div>
      </div>
      
      <div class="content">
        <div class="price-tag" :class="{ 'is-sold': item.status === 'sold' }">¥{{ item.price }}</div>
        <h4 class="title">{{ item.name }}</h4>
        
        <div class="footer">
          <template v-if="!isMine">
            <span class="seller">ID: {{ item.seller_id }}</span>
            <el-button size="small" class="btn-favor" @click.stop="handleFavor(item)">收藏</el-button>
            <el-button size="small" class="btn-buy" @click.stop="handleBuy" :disabled="item.status !== 'active'">{{ item.status === 'active' ? '购买' : '已售出' }}</el-button>
          </template>
          
          <template v-else>
            <el-button size="small" class="btn-edit" plain type="primary" @click.stop="handleEdit" :disabled="item.status !== 'active'">编辑</el-button>
            <el-button size="small" class="btn-delete" plain type="danger" @click.stop="handleDelete">删除</el-button>
          </template>
        </div>
      </div>
    </el-card>

  <el-dialog
    v-model="favorDialogVisible"
    width="360px"
    class="favor-dialog"
  >
    <template #header>
      <div class="favor-header">
        <el-icon size="20"><Star /></el-icon>
        <span>收藏商品</span>
      </div>
    </template>
      <div class="favor-body">
        <p class="favor-tip">请选择要收藏到的收藏夹</p>

        <el-select
          v-model="selectedFolderId"
          placeholder="选择收藏夹"
          size="large"
          style="width: 100%"
          @click.stop
        >
          <el-option
            v-for="f in folders"
            :key="f.id"
            :label="f.name"
            :value="f.id"
          />
        </el-select>
      </div>

      <template #footer>
  <el-button @click.stop="favorDialogVisible = false">取消</el-button>
  <el-button
    type="primary"
    size="large"
    @click.stop="confirmFavor"
  >
    收藏
  </el-button>
</template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  buyProduct,
  deleteProduct,
  favoriteProduct,
  getFavoriteFolders
} from '@/api/index'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { Star } from '@element-plus/icons-vue'


const userStore = useUserStore()
const router = useRouter()

const props = defineProps({
  item: Object,
  isMine: Boolean
})
const emit = defineEmits(['refresh'])

const favorDialogVisible = ref(false)
const folders = ref([])
const selectedFolderId = ref(null)
const currentProductId = ref(null)

const handleBuy = async () => {
  ElMessageBox.confirm(
    `确认以 ¥${props.item.price} 的价格购买此商品吗？`,
    '购买确认',
    { confirmButtonText: '确认支付', cancelButtonText: '取消', type: 'warning' }
  ).then(async () => {
    await buyProduct(props.item.id)
    ElMessage.success('购买成功！')
    emit('refresh')
  })
}

const handleDelete = () => {
  ElMessageBox.confirm('确定要删除这件商品吗？', '警告', { type: 'error' })
    .then(async () => {
      await deleteProduct(props.item.id)
      ElMessage.success('已删除')
      emit('refresh')
    })
}

const handleEdit = () => {
  router.push(`/modify_product/${props.item.id}`)
}

const handleFavor = async (item) => {
  if (!userStore.token) {
    router.push('/login')
    return
  }

  currentProductId.value = item.id
  selectedFolderId.value = null

  const res = await getFavoriteFolders()
  folders.value = res.folders || []

  favorDialogVisible.value = true
}

const confirmFavor = async () => {
  if (!selectedFolderId.value) {
    ElMessage.warning('请选择一个收藏夹')
    return
  }

  await favoriteProduct({
    product_id: currentProductId.value,
    folder_id: selectedFolderId.value
  })

  ElMessage.success('收藏成功')
  favorDialogVisible.value = false
}

</script>

<style scoped>
.is-sold {
  color: #999 !important;
  text-decoration: line-through;
}
.p-card {
  border-radius: 12px;
  margin-bottom: 20px;
  border: none;  
  cursor: pointer;
}
.p-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  border: 1px solid #ff4d4f;
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
.favor-dialog :deep(.el-dialog) {
  border-radius: 14px;
}

.favor-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #ff6600;
}

.favor-body {
  padding: 10px 0 5px;
}

.favor-tip {
  font-size: 13px;
  color: #888;
  margin-bottom: 10px;
}

</style>