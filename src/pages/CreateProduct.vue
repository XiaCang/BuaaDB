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
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Plus } from '@element-plus/icons-vue'
import { createProduct, uploadFile } from '@/api/index'

const router = useRouter()
const productFormRef = ref(null)
const loading = ref(false)

const productForm = reactive({
  name: '',
  price: 0,
  image_url: '', // 测试时可以预填一个高图 URL 看看效果
  description: ''
})

const rules = {
  name: [{ required: true, message: '请输入商品名称', trigger: 'blur' }],
  price: [{ required: true, message: '请输入价格', trigger: 'blur' }],
  image_url: [{ required: true, message: '请上传商品图片', trigger: 'change' }], // 注意这里 trigger 改为 change
  description: [{ required: true, message: '请输入商品描述', trigger: 'blur' }]
}

// 处理图片上传
const handleImageUpload = async (options) => {
  const formData = new FormData()
  formData.append('file', options.file)
  formData.append('type', 'product')
  
  try {
    // 模拟上传延迟
    // await new Promise(r => setTimeout(r, 1000)) 
    const res = await uploadFile(formData)
    productForm.image_url = res.url
    ElMessage.success('图片上传成功')
    // 手动触发校验，消除必填红字
    productFormRef.value.validateField('image_url')
  } catch (error) {
    console.error(error)
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
        const res = await createProduct(productForm)
        ElMessage.success(res.message || '发布成功！')
        router.push('/')
      } catch (e) {
          // 接口报错已有拦截器处理
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.create-container {
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

.back-btn {
  font-size: 16px; color: #666;
}
.back-btn:hover { color: #ff6600; }
.title { font-size: 18px; font-weight: bold; }

/* --- 核心修复区域 Start --- */

/* 深度选择器，定位到 el-upload 内部实际的点击区域 div */
.upload-container :deep(.el-upload) {
  border: 2px dashed #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  width: 200px;      /* 固定宽度 */
  height: 200px;     /* 固定高度 */
  position: relative; /* 为内部绝对定位做准备 */
  overflow: hidden;  /* 【关键】隐藏溢出部分 */
  transition: border-color 0.3s;
  background-color: #fafafa;
}

.upload-container:hover :deep(.el-upload) {
  border-color: #ff6600;
}

/* 图片预览盒子的样式 */
.image-preview-box {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 图片本身的样式 */
.uploaded-img {
  width: 100%;
  height: 100%;
  /* 【关键修改】使用 contain，保证图片完整显示在框内，不会被裁剪，也不会溢出 */
  object-fit: contain; 
  /* 如果你希望填满格子允许裁剪，可以改回 cover，但因为上面加了 overflow:hidden，它不会再溢出框外了 */
  /* object-fit: cover; */
}

/* 上传占位符的样式（图标和文字） */
.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

.uploader-icon {
  font-size: 32px; color: #999;
}
.upload-tip {
  font-size: 12px; color: #999; margin-top: 8px;
}
/* --- 核心修复区域 End --- */

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
}
.btn-orange:hover { opacity: 0.9; }
</style>