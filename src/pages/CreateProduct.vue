<template>
  <div class="create-container">
    <el-card class="form-card">
      <template #header>
        <div class="card-header-wrapper">
          <el-button link @click="router.back()" class="back-btn">
            <el-icon><ArrowLeft /></el-icon>
            <span>返回</span>
          </el-button>
          <span class="title">发布我的宝贝</span>
          <div style="width: 50px"></div>
        </div>
      </template>

      <el-form :model="productForm" :rules="rules" ref="productFormRef" label-position="top">
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
              <div class="upload-tip">点击上传商品主图</div>
            </div>
          </el-upload>
        </el-form-item>

        <el-form-item label="商品名称" prop="name">
          <el-input v-model="productForm.name" placeholder="起个吸引人的名字吧" />
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
          <el-input-number v-model="productForm.price" :precision="2" :min="0" controls-position="right" style="width: 100%;" />
        </el-form-item>

        <el-form-item label="详细描述" prop="description">
          <el-input v-model="productForm.description" type="textarea" :rows="5" placeholder="描述一下商品的细节..." />
        </el-form-item>

        <div class="form-footer">
          <el-button @click="router.back()">取消</el-button>
          <el-button type="primary" class="btn-orange" @click="submitForm" :loading="loading">
            确认发布
          </el-button>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Plus } from '@element-plus/icons-vue'
import { createProduct, uploadFile, getCategories } from '@/api/index'

const router = useRouter()
const productFormRef = ref(null)
const loading = ref(false)
const categoryList = ref([]) // 存储分类列表

const productForm = reactive({
  name: '',
  price: 0,
  image_url: '',
  description: '',
  category_id: '' // 默认为空字符串
})

const rules = {
  name: [{ required: true, message: '请输入商品名称', trigger: 'blur' }],
  price: [{ required: true, message: '请输入价格', trigger: 'blur' }],
  image_url: [{ required: true, message: '请上传商品图片', trigger: 'change' }],
  description: [{ required: true, message: '请输入商品描述', trigger: 'blur' }]
  // category_id 通常非必填，若必填可在此添加规则
}

// 初始化获取分类
const fetchCategories = async () => {
  try {
    const res = await getCategories()
    // 注意：根据你之前的 API 定义，返回结构是 res.categories = [{id, name}]
    console.log(res);
    
    categoryList.value = res.categories || []
  } catch (error) {
    console.error('获取分类失败', error)
  }
}

// 处理图片上传
const handleImageUpload = async (options) => {
  const formData = new FormData()
  formData.append('file', options.file)
  formData.append('type', 'product')
  
  try {
    const res = await uploadFile(formData)
    productForm.image_url = res.url
    ElMessage.success('图片上传成功')
    productFormRef.value.validateField('image_url')
  } catch (error) {
    ElMessage.error('上传失败，请重试')
  }
}

// 提交表单
const submitForm = async () => {
  if (!productFormRef.value) return
  await productFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        // 直接提交 productForm，包含 category_id
        const res = await createProduct(productForm)
        ElMessage.success(res.message || '发布成功！')
        router.push('/')
      } catch (e) {
      } finally {
        loading.value = false
      }
    }
  })
}

onMounted(fetchCategories)
</script>

<style scoped>
/* 样式部分保持你之前的设置即可 */
.create-container {
  padding: 30px 20px;
  background-color: #f8f9fa;
  min-height: calc(100vh - 70px);
  display: flex;
  justify-content: center;
}
.form-card { width: 100%; max-width: 700px; border-radius: 12px; border: none; }
.card-header-wrapper { display: flex; align-items: center; justify-content: space-between; }
.back-btn { font-size: 16px; color: #666; }
.back-btn:hover { color: #ff6600; }
.title { font-size: 18px; font-weight: bold; }

/* 上传框样式 */
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
.image-preview-box { width: 100%; height: 100%; display: flex; justify-content: center; align-items: center; }
.uploaded-img { width: 100%; height: 100%; object-fit: contain; }
.upload-placeholder { display: flex; flex-direction: column; align-items: center; justify-content: center; width: 100%; height: 100%; }
.uploader-icon { font-size: 32px; color: #999; }
.upload-tip { font-size: 12px; color: #999; margin-top: 8px; }

.form-footer { margin-top: 30px; display: flex; justify-content: flex-end; gap: 15px; }
.btn-orange {
  background: linear-gradient(90deg, #ff9838, #ff6600);
  border: none;
  padding: 10px 30px;
  border-radius: 8px;
  color: white;
}
.btn-orange:hover { opacity: 0.9; }
</style>