<template>
  <div class="profile-container">
    <div class="top-nav">
      <el-button link @click="router.back()" class="back-link">
        <el-icon><ArrowLeft /></el-icon>
        返回主页
      </el-button>
    </div>

    <el-card class="profile-card">
      <div class="profile-layout">
        <div class="side-info">
          <div class="avatar-wrapper">
            <el-avatar :size="120" :src="userInfo.avatar_url" />
            <el-upload class="avatar-edit-btn" action="#" :show-file-list="false" :http-request="handleAvatarUpdate">
              <el-icon><Camera /></el-icon>
            </el-upload>
          </div>
          <h2 class="nickname-display">{{ userInfo.nickname || '未设置' }}</h2>
          <el-tag type="warning" effect="dark" round>普通用户</el-tag>

          <p class="register-time">注册时间: {{ userInfo.create_time }}</p>
        </div>

        <div class="main-form">
          <h3 class="section-title">基本设置</h3>
          <el-form :model="editForm" label-width="80px">
            <el-form-item label="昵称">
              <el-input v-model="editForm.nickname" />
            </el-form-item>
            <el-form-item label="手机号">
              <el-input v-model="editForm.phone" />
            </el-form-item>
            <el-form-item label="个人简介">
              <el-input v-model="editForm.intro" type="textarea" :rows="3" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" class="btn-orange" @click="saveProfile" :loading="saving">
                保存资料
              </el-button>
            </el-form-item>
          </el-form>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ArrowLeft, Camera } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
const router = useRouter()
import { ref, onMounted, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { getSelfInfo, updateUserInfo, uploadFile } from '@/api/index'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const userInfo = ref({})
const saving = ref(false)

const editForm = reactive({
  nickname: '',
  phone: '',
  intro: '',
  avatar_url: ''
})


const loadData = async () => {
  try {
    const res = await getSelfInfo()
    userInfo.value = res
    console.log("In Profile : userInfo = " , userInfo.value);

    Object.assign(editForm, {
      nickname: res.nickname,
      phone: res.phone,
      intro: res.intro,
      avatar_url: res.avatar_url
    })
    userStore.setUserInfo(res)
  } catch (err) {}
}


const handleAvatarUpdate = async (options) => {
  const formData = new FormData()
  formData.append('file', options.file)
  formData.append('type', 'avatar')
  
  try {
    const res = await uploadFile(formData)
    editForm.avatar_url = res.url
    await saveProfile()
    ElMessage.success('头像已更新')
  } catch (err) {}
}


const saveProfile = async () => {
  saving.value = true
  try {
    const res = await updateUserInfo(editForm)
    ElMessage.success(res.message || '资料更新成功')
    await loadData() 
  } finally {
    saving.value = false
  }
}

const formatDate = (str) => str ? new Date(str).toLocaleDateString() : 'N/A'

onMounted(loadData)
</script>

<style scoped>
.top-nav {
  margin-bottom: 20px;
}

.back-link {
  font-size: 15px;
  color: #666;
  display: flex;
  align-items: center;
  gap: 4px;
}

.back-link:hover {
  color: #ff6600;
}

.profile-container {
  max-width: 900px;
  margin: 20px auto; 
  padding: 0 20px;
}

.profile-card {
  border-radius: 16px;
  border: none;
}

.profile-layout {
  display: flex;
  gap: 50px;
}

.side-info {
  width: 250px;
  display: flex;
  flex-direction: column;
  align-items: center;
  border-right: 1px solid #f0f0f0;
  padding-right: 30px;
}

.avatar-wrapper {
  position: relative;
  margin-bottom: 20px;
}

.avatar-edit-btn {
  position: absolute;
  bottom: 0;
  right: 0;
  background: #ff6600;
  color: white;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}

.nickname-display {
  margin: 10px 0;
  font-size: 22px;
}

.meta-info {
  margin-top: 30px;
  width: 100%;
  color: #999;
  font-size: 13px;
  line-height: 2;
}

.main-form {
  flex: 1;
}

.section-title {
  margin-bottom: 25px;
  font-size: 18px;
  color: #333;
}

.btn-orange {
  background: linear-gradient(90deg, #ff9838, #ff6600);
  border: none;
  border-radius: 20px;
  padding: 10px 25px;
}

@media (max-width: 768px) {
  .profile-layout { flex-direction: column; }
  .side-info { width: 100%; border-right: none; border-bottom: 1px solid #f0f0f0; padding: 0 0 30px 0; }
}
</style>