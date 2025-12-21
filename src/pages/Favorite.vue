<template>
  <div class="favorites-container">
    <div class="top-nav">
      <el-button link @click="router.back()" class="back-link">
        <el-icon><ArrowLeft /></el-icon> 返回
      </el-button>
      <h2 class="page-title">我的收藏夹</h2>
      <el-button type="primary" class="btn-orange" size="small" @click="handleCreateFolder">
        + 新建收藏夹
      </el-button>
    </div>

    <el-tabs 
      v-model="activeFolderId" 
      type="card" 
      class="folder-tabs" 
      @tab-change="handleTabChange"
      closable
      @tab-remove="handleDeleteFolder"
    >
      <el-tab-pane
        v-for="folder in folders"
        :key="folder.id"
        :label="folder.name"
        :name="folder.id"
      >
        <template #label>
          <span class="custom-tab-label">
            {{ folder.name }}
            <el-icon class="edit-icon" @click.stop="handleRenameFolder(folder)"><EditPen /></el-icon>
          </span>
        </template>

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
                  <div v-if="item.status === 'sold'" class="sold-status-tag">已售出</div>
                </div>

                <div class="prod-details">
                  <h4 class="prod-name" @click="goDetail(item.id)">{{ item.name }}</h4>
                  <div class="price-action">
                    <span class="price" :class="{ 'is-sold': item.status === 'sold' }">
                      ¥{{ item.price }}
                    </span>
                    <el-button 
                      type="danger" icon="Delete" circle size="small" plain
                      @click="handleRemoveProduct(item.id)"
                    />
                  </div>
                </div>
              </div>
            </div>
            <el-empty v-else description="该收藏夹还没有商品~" />
          </div>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, Picture, Delete, EditPen } from '@element-plus/icons-vue'
import { 
  getFavoriteFolders, createFavoriteFolder, modifyFavoriteFolder, 
  deleteFavoriteFolder, getFavorites, getProductDetail, deleteFavorite 
} from '@/api/index'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const loading = ref(false)
const folders = ref([])
const activeFolderId = ref(null)
const favoriteList = ref([])

const fetchFolders = async () => {
  try {
    const res = await getFavoriteFolders()
    folders.value = res.folders || []
    if (folders.value.length > 0 && !activeFolderId.value) {
      activeFolderId.value = folders.value[0].id
      fetchFavorites(activeFolderId.value)
    }
  } catch (err) {
    ElMessage.error('获取收藏夹列表失败')
  }
}

const fetchFavorites = async (folderId) => {
  if (!folderId) return
  loading.value = true
  try {
    const res = await getFavorites(folderId)
    const favIds = res.favorites || []
    
    const details = await Promise.all(
      favIds.map(item => getProductDetail(item.product_id))
    )
    favoriteList.value = details
  } catch (err) {
    console.error('获取商品详情失败', err)
  } finally {
    loading.value = false
  }
}

const handleTabChange = (folderId) => {
  fetchFavorites(folderId)
}

// --- 收藏夹管理逻辑 ---

const handleCreateFolder = () => {
  ElMessageBox.prompt('请输入新收藏夹名称', '新建收藏夹', {
    confirmButtonText: '创建',
    cancelButtonText: '取消',
    inputPattern: /\S+/,
    inputErrorMessage: '名称不能为空'
  }).then(async ({ value }) => {
    await createFavoriteFolder({ name: value })
    ElMessage.success('创建成功')
    fetchFolders()
  })
}

const handleRenameFolder = (folder) => {
  ElMessageBox.prompt('重命名收藏夹', '修改名称', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    inputValue: folder.name,
    inputPattern: /\S+/,
    inputErrorMessage: '名称不能为空'
  }).then(async ({ value }) => {
    await modifyFavoriteFolder({ id: folder.id, name: value }) 
    ElMessage.success('修改成功')
    fetchFolders()
  })
}

const handleDeleteFolder = (folderId) => {
  ElMessageBox.confirm('确定删除该收藏夹及其下的所有收藏吗？', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'error'
  }).then(async () => {
    await deleteFavoriteFolder(folderId)
    ElMessage.success('已删除收藏夹')
    activeFolderId.value = null
    fetchFolders()
  })
}

const handleRemoveProduct = (productId) => {
  ElMessageBox.confirm('确定要移除该商品吗？', '提示').then(async () => {
    try {
      await deleteFavorite(activeFolderId.value, productId)
      ElMessage.success('已移除')
      favoriteList.value = favoriteList.value.filter(item => item.id !== productId)
    } catch (err) {}
  })
}

const goDetail = (id) => router.push(`/product/${id}`)

onMounted(fetchFolders)
</script>

<style scoped>
.favorites-container { max-width: 1100px; margin: 30px auto; padding: 0 20px; }
.top-nav { display: flex; align-items: center; gap: 20px; margin-bottom: 25px; }
.back-link { font-size: 15px; color: #666; }
.page-title { margin: 0; font-size: 22px; color: #333; flex-grow: 1; }

.folder-tabs { background: #fff; padding: 10px; border-radius: 8px; }

.custom-tab-label {
  display: flex;
  align-items: center;
  gap: 8px;
}
.edit-icon {
  font-size: 14px;
  color: #999;
  transition: color 0.3s;
}
.edit-icon:hover { color: #ff6600; }

.list-card { border: none; min-height: 400px; margin-top: -1px; }
.fav-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 20px; }

.fav-item { 
  border: 1px solid #f0f0f0; 
  border-radius: 8px; 
  overflow: hidden; 
  transition: all 0.3s;
}
.fav-item:hover { transform: translateY(-5px); box-shadow: 0 6px 15px rgba(0,0,0,0.1); }

.img-container { position: relative; height: 160px; }
.prod-img { width: 100%; height: 100%; cursor: pointer; }
.sold-status-tag {
  position: absolute; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0, 0, 0, 0.3); color: #fff;
  display: flex; align-items: center; justify-content: center; font-weight: bold;
}

.prod-details { padding: 10px; }
.prod-name { 
  margin: 0 0 8px; font-size: 13px; color: #333; height: 36px; 
  line-height: 18px; cursor: pointer;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; 
}
.price-action { display: flex; justify-content: space-between; align-items: center; }
.price { font-size: 16px; font-weight: bold; color: #ff6600; }
.price.is-sold { color: #999; text-decoration: line-through; }

.btn-orange { background-color: #ff6600; border-color: #ff6600; }
</style>