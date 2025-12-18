<template>
  <div class="create-container">
    <el-card class="form-card">
      <template #header>
        <div class="card-header">
          <span class="title">发布我的宝贝</span>
        </div>
      </template>

      <el-form :model="productForm" :rules="rules" ref="productFormRef" label-position="top">
        <el-form-item label="商品图片" prop="image_url">
          <el-upload
            class="product-uploader"
            action="#"
            :show-file-list="false"
            :http-request="handleImageUpload"
          >
            <img v-if="productForm.image_url" :src="productForm.image_url" class="uploaded-img" />
            <el-icon v-else class="uploader-icon"><Plus /></el-icon>
            <div class="upload-tip">点击上传商品主图</div>
          </el-upload>
        </el-form-item>

        <el-form-item label="商品名称" prop="name">
          <el-input v-model="productForm.name" placeholder="起个吸引人的名字吧（例如：九成新耳机）" />
        </el-form-item>

        <el-form-item label="商品价格 (元)" prop="price">
          <el-input-number 
            v-model="productForm.price" 
            :precision="2" 
            :step="1" 
            :min="0" 
            controls-position="right"
          />
        </el-form-item>

        <el-form-item label="详细描述" prop="description">
          <el-input
            v-model="productForm.description"
            type="textarea"
            :rows="5"
            placeholder="描述一下商品的成色、购买渠道、转手原因等..."
          />
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
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { createProduct, uploadFile } from '@/api/index'

const router = useRouter()
const productFormRef = ref(null)
const loading = ref(false)

const productForm = reactive({
  name: '',
  price: 0,
  image_url: '',
  description: ''
})

const rules = {
  name: [{ required: true, message: '请输入商品名称', trigger: 'blur' }],
  price: [{ required: true, message: '请输入价格', trigger: 'blur' }],
  image_url: [{ required: true, message: '请上传商品图片', trigger: 'change' }],
  description: [{ required: true, message: '请输入商品描述', trigger: 'blur' }]
}

// 处理图片上传
const handleImageUpload = async (options) => {
  const formData = new FormData()
  formData.append('file', options.file)
  formData.append('type', 'product') // 对应接口要求的 type
  
  try {
    const res = await uploadFile(formData)
    productForm.image_url = res.url
    ElMessage.success('图片上传成功')
  } catch (error) {
    console.error(error)
  }
}

// 提交表单
const submitForm = async () => {
  if (!productFormRef.value) return
  await productFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const res = await createProduct(productForm)
        ElMessage.success(res.message || '发布成功！')
        router.push('/') // 返回首页
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.create-container {
  padding: 40px 20px;
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

.title {
  font-size: 20px;
  font-weight: bold;
  color: #333;
}

/* 上传框样式 */
.product-uploader {
  border: 2px dashed #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  width: 200px;
  height: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  transition: border-color 0.3s;
}

.product-uploader:hover {
  border-color: #ff6600;
}

.uploader-icon {
  font-size: 32px;
  color: #999;
}

.uploaded-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 8px;
}

.upload-tip {
  font-size: 12px;
  color: #999;
  margin-top: 8px;
}

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
}
</style>