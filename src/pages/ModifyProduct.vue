<template>
  <div class="modify-container">
    <el-card class="form-card" v-loading="pageLoading">
      <template #header>
        <div class="card-header-wrapper">
          <el-button link @click="router.back()" class="back-btn">
            <el-icon><ArrowLeft /></el-icon>
            <span>返回</span>
          </el-button>
          <span class="title">修改商品信息</span>
          <div style="width: 50px"></div>
        </div>
      </template>

      <el-form 
        :model="productForm" 
        :rules="rules" 
        ref="productFormRef" 
        label-position="top"
      >
        <el-form-item label="商品图片" prop="image_url">
          <el-upload
            class="upload-container"
            action="#"
            :show-file-list="false"
            :http-request="handleImageUpload"
          >
            <div v-if="productForm.image_url" class="image-preview-box">
               <img :src="productForm.image_url" class="uploaded-img" />
            </div>
            <div v-else class="upload-placeholder">
              <el-icon class="uploader-icon"><Plus /></el-icon>
              <div class="upload-tip">点击更换图片</div>
            </div>
          </el-upload>
        </el-form-item>

        <el-form-item label="商品名称" prop="name">
          <el-input v-model="productForm.name" placeholder="请输入商品名称" />
        </el-form-item>

        <el-form-item label="物品类别" prop="category_id">
          <el-select v-model="productForm.category_id" placeholder="请选择商品分类" style="width: 100%">
            <el-option label="未分类 / 不选择" value="" />
            <el-option 
              v-for="item in categoryList" 
              :key="item.category_id" 
              :label="item.category_name" 
              :value="item.category_id" 
            />
          </el-select>
        </el-form-item>

        <el-form-item label="商品价格 (元)" prop="price">
          <el-input-number 
            v-model="productForm.price" 
            :precision="2" 
            :min="0" 
            controls-position="right" 
            style="width: 100%;" 
          />
        </el-form-item>

        <el-form-item label="详细描述" prop="description">
          <el-input 
            v-model="productForm.description" 
            type="textarea" 
            :rows="5" 
            placeholder="请详细描述你的商品..." 
          />
        </el-form-item>

        <div class="form-footer">
          <el-button @click="router.back()">取消修改</el-button>
          <el-button 
            type="primary" 
            class="btn-orange" 
            @click="submitForm" 
            :loading="submitLoading"
          >
            保存并更新
          </el-button>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Plus } from '@element-plus/icons-vue'
import { getProductDetail, modifyProduct, uploadFile, getCategories } from '@/api/index'

const router = useRouter()
const route = useRoute()
const productFormRef = ref(null)
const pageLoading = ref(false) 
const submitLoading = ref(false)
const categoryList = ref([]) // 分类列表

// 表单数据，增加 category_id
const productForm = reactive({
  id: '', 
  name: '',
  price: 0,
  image_url: '',
  description: '',
  category_id: '' // 默认为空
})

const rules = {
  name: [{ required: true, message: '商品名称不能为空', trigger: 'blur' }],
  price: [{ required: true, message: '价格不能为空', trigger: 'blur' }],
  image_url: [{ required: true, message: '请上传商品图片', trigger: 'change' }],
  description: [{ required: true, message: '详细描述不能为空', trigger: 'blur' }]
}

// 获取分类列表
const fetchCategories = async () => {
  try {
    const res = await getCategories()
    categoryList.value = res.categories || []
  } catch (error) {
    console.error('获取分类失败', error)
  }
}

// 页面加载：获取旧数据并回填
const initData = async () => {
  const productId = route.params.id 
  if (!productId) {
    ElMessage.error('无效的商品ID')
    return router.back()
  }

  pageLoading.value = true
  try {
    // 并行获取分类和商品详情
    await fetchCategories()
    const res = await getProductDetail(productId)
    
    // 将获取到的详情填入表单
    productForm.id = res.id
    productForm.name = res.name
    productForm.price = res.price
    productForm.image_url = res.image_url
    productForm.description = res.description
    // 回填分类ID（如果后端返回了该字段）
    productForm.category_id = res.category_id || '' 
  } catch (error) {
    console.error('初始化数据失败', error)
  } finally {
    pageLoading.value = false
  }
}

// 处理图片更换
const handleImageUpload = async (options) => {
  const formData = new FormData()
  formData.append('file', options.file)
  formData.append('type', 'product')
  
  try {
    const res = await uploadFile(formData)
    productForm.image_url = res.url
    ElMessage.success('图片更换成功')
    productFormRef.value.validateField('image_url')
  } catch (error) {}
}

// 提交修改
const submitForm = async () => {
  if (!productFormRef.value) return
  await productFormRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        const res = await modifyProduct(productForm)
        ElMessage.success(res.message || '修改成功！')
        router.push('/') 
      } catch (e) {
      } finally {
        submitLoading.value = false
      }
    }
  })
}

onMounted(initData)
</script>

<style scoped>
.modify-container {
  padding: 30px 20px;
  background-color: #f8f9fa;
  min-height: calc(100vh - 70px);
  display: flex;
  justify-content: center;
}

.form-card {
  width: 100%;
  max-width: 700px;
  border-radius: 12px;
  border: none;
}

.card-header-wrapper {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.back-btn { font-size: 16px; color: #666; }
.back-btn:hover { color: #ff6600; }
.title { font-size: 18px; font-weight: bold; }

.upload-container :deep(.el-upload) {
  border: 2px dashed #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  width: 200px;
  height: 200px;
  position: relative;
  overflow: hidden;
  transition: border-color 0.3s;
  background-color: #fafafa;
}

.upload-container:hover :deep(.el-upload) { border-color: #ff6600; }

.image-preview-box {
  width: 100%; height: 100%;
  display: flex; justify-content: center; align-items: center;
}

.uploaded-img {
  width: 100%; height: 100%;
  object-fit: contain; 
}

.upload-placeholder {
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  width: 100%; height: 100%;
}

.uploader-icon { font-size: 32px; color: #999; }
.upload-tip { font-size: 12px; color: #999; margin-top: 8px; }

.form-footer {
  margin-top: 30px;
  display: flex;
  justify-content: flex-end;
  gap: 15px;
}

.btn-orange {
  background: linear-gradient(90deg, #ff9838, #ff6600);
  border: none;
  padding: 10px 30px;
  border-radius: 8px;
  color: white;
}
.btn-orange:hover { opacity: 0.9; }
</style>