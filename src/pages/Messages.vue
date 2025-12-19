<template>
  <div class="messages-container">
    <el-card class="chat-card" :body-style="{ padding: '0px' }">
      <div class="chat-layout">
        <!-- 左侧联系人列表 -->
        <div class="contact-list">
          <div class="list-header">
            <h3>消息中心</h3>
          </div>
          <el-scrollbar class="contact-scrollbar">
            <div 
              v-for="contact in processedContactList" 
              :key="contact.userId" 
              class="contact-item"
              :class="{ 
                active: currentTargetId === contact.userId,
                'has-unread': contact.unreadCount > 0
              }"
              @click="selectContact(contact.userId)"
            >
              <el-avatar 
                :size="40" 
                class="contact-avatar"
                :src="contact.avatar || contact.sender_avatar"
              >
                {{ contact.nickname?.charAt(0) || contact.userId?.charAt(0) }}
              </el-avatar>
              <div class="contact-info">
                <div class="name-time">
                  <span class="name">
                    {{ contact.nickname || contact.sender_nickname || `用户 ${contact.userId}` }}
                    <span v-if="contact.unreadCount > 0" class="unread-badge">
                      {{ contact.unreadCount > 99 ? '99+' : contact.unreadCount }}
                    </span>
                  </span>
                  <span class="time">{{ formatTimeShort(contact.lastTime) }}</span>
                </div>
                <div class="last-msg">{{ contact.lastMsg }}</div>
              </div>
            </div>
            <el-empty 
              v-if="processedContactList.length === 0" 
              description="暂无消息" 
              :image-size="80"
            />
          </el-scrollbar>
        </div>

        <!-- 右侧聊天窗口 -->
        <div class="chat-window">
          <template v-if="currentTargetId">
            <div class="chat-header">
              <el-avatar 
                :size="32" 
                :src="currentContactInfo?.avatar || currentContactInfo?.sender_avatar"
                class="header-avatar"
              >
                {{ currentContactInfo?.nickname?.charAt(0) || currentTargetId?.charAt(0) }}
              </el-avatar>
              <div class="header-info">
                <strong>{{ currentContactInfo?.nickname || currentContactInfo?.sender_nickname || `用户 ${currentTargetId}` }}</strong>
                <span class="online-status" v-if="currentContactInfo?.online">在线</span>
              </div>
            </div>

            <!-- 消息显示区域 -->
            <el-scrollbar 
              ref="msgScroll" 
              class="msg-display"
              @scroll="handleScroll"
            >
              <div v-if="loadingHistory" class="loading-more">
                <el-icon class="is-loading"><Loading /></el-icon>
                加载中...
              </div>
              <div class="msg-content-inner">
                <div 
                  v-for="(msg, index) in currentChatHistory" 
                  :key="msg.message_id || index" 
                  class="msg-row"
                  :class="{ 
                    'is-me': isMyMessage(msg),
                    'is-system': msg.sender_id === 'system'
                  }"
                >
                  <template v-if="!isSystemMessage(msg)">
                    <el-avatar 
                      :size="32" 
                      class="msg-avatar"
                      :src="isMyMessage(msg) ? userStore.userInfo.avatar_url : (msg.sender_avatar || currentContactInfo?.sender_avatar)"
                    >
                      {{ isMyMessage(msg) ? '我' : (msg.sender_nickname?.charAt(0) || msg.sender_id?.charAt(0)) }}
                    </el-avatar>
                  </template>
                  <div class="msg-bubble" :class="{ 'system-bubble': isSystemMessage(msg) }">
                    <div class="text">
                      <span v-if="isSystemMessage(msg)">{{ msg.content }}</span>
                      <span v-else>{{ msg.content }}</span>
                    </div>
                    <div class="msg-time">{{ formatTimeFull(msg.time) }}</div>
                    <div v-if="isMyMessage(msg)" class="msg-status">
                      <el-icon v-if="msg.status === 'sending'" class="sending-icon"><Loading /></el-icon>
                      <el-icon v-else-if="msg.status === 'failed'" class="failed-icon"><CircleClose /></el-icon>
                      <el-icon v-else class="success-icon"><CircleCheck /></el-icon>
                    </div>
                  </div>
                </div>
              </div>
            </el-scrollbar>

            <!-- 输入区域 -->
            <div class="input-area">
              <el-input
                v-model="inputMsg"
                type="textarea"
                :rows="3"
                placeholder="输入消息..."
                @keyup.enter.exact="handleSend"
                @keyup.enter.shift.exact="inputMsg += '\n'"
                resize="none"
                :disabled="sending"
                class="msg-input"
              />
              <div class="send-bar">
                <span class="tip">Enter 发送，Shift+Enter 换行</span>
                <el-button 
                  type="primary" 
                  class="btn-orange" 
                  @click="handleSend" 
                  :loading="sending"
                  :disabled="!inputMsg.trim()"
                >
                  发送
                </el-button>
              </div>
            </div>
          </template>

          <!-- 未选择联系人的状态 -->
          <div v-else class="empty-chat">
            <div class="empty-illustration">
              <el-icon :size="80" color="#e0e0e0"><ChatLineRound /></el-icon>
            </div>
            <h3>欢迎来到消息中心</h3>
            <p>选择左侧的联系人开始聊天</p>
            <p class="empty-tip">或通过搜索找到你想联系的人</p>
            <div class="empty-actions">
              <el-input
                v-model="searchUser"
                placeholder="搜索用户..."
                class="search-input"
                :prefix-icon="Search"
              />
              <el-button type="primary" class="btn-orange" :icon="Plus">
                新建聊天
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick, watch, onUnmounted } from 'vue'
import { 
  ChatDotRound, 
  ChatLineRound, 
  Search, 
  Plus, 
  Picture, 
  Microphone,
  Loading,
  CircleCheck,
  CircleClose
} from '@element-plus/icons-vue'
import { getMsgs, sendMsg } from '@/api/index'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// 状态管理
const rawMessages = ref([])
const inputMsg = ref('')
const sending = ref(false)
const msgScroll = ref(null)
const searchUser = ref('')
const loadingHistory = ref(false)
const page = ref(1)
const pageSize = 20
const hasMore = ref(true)

// 当前聊天对象ID（从路由参数获取）
const currentTargetId = computed(() => route.params.id || null)

// 处理后的联系人列表
const processedContactList = computed(() => {
  const contacts = {}
  const myId = userStore.userInfo.user_name
  
  rawMessages.value.forEach(msg => {
    // 确定对方ID
    const otherId = msg.sender_id === myId ? msg.receiver_id : msg.sender_id
    
    if (!contacts[otherId]) {
      contacts[otherId] = {
        userId: otherId,
        nickname: msg.sender_nickname,
        avatar: msg.sender_avatar,
        sender_nickname: msg.sender_nickname,
        sender_avatar: msg.sender_avatar,
        lastMsg: msg.content,
        lastTime: msg.time,
        unreadCount: msg.sender_id === otherId ? 1 : 0, // 假设未读消息
        lastMessageId: msg.message_id
      }
    } else {
      // 更新最新消息
      const currentTime = new Date(msg.time)
      const lastTime = new Date(contacts[otherId].lastTime)
      
      if (currentTime > lastTime) {
        contacts[otherId].lastMsg = msg.content
        contacts[otherId].lastTime = msg.time
        contacts[otherId].lastMessageId = msg.message_id
        
        // 如果是对方发来的消息，增加未读数
        if (msg.sender_id === otherId) {
          contacts[otherId].unreadCount += 1
        }
      }
    }
  })
  
  // 转换为数组并按时间排序
  return Object.values(contacts).sort((a, b) => 
    new Date(b.lastTime) - new Date(a.lastTime)
  )
})

// 当前联系人信息
const currentContactInfo = computed(() => {
  if (!currentTargetId.value) return null
  return processedContactList.value.find(c => c.userId === currentTargetId.value)
})

// 当前聊天历史
const currentChatHistory = computed(() => {
  if (!currentTargetId.value) return []
  
  const myId = userStore.userInfo.user_name

  console.log("myId = " , myId , "currentTargetId = " , currentTargetId.value);
  

  return rawMessages.value
    .filter(msg => 
      (msg.sender_id === myId && msg.receiver_id === currentTargetId.value) ||
      (msg.sender_id === currentTargetId.value && msg.receiver_id === myId)
    )
    .sort((a, b) => new Date(a.time) - new Date(b.time))
})

// 工具函数
const isMyMessage = (msg) => {
  return msg.sender_id === userStore.userInfo.user_name
}

const isSystemMessage = (msg) => {
  return msg.sender_id === 'system'
}

// 选择联系人
const selectContact = (userId) => {
  // 如果已经是当前联系人，不重复跳转
  if (currentTargetId.value === userId) return
  
  // 清除该联系人的未读消息计数
  const contact = processedContactList.value.find(c => c.userId === userId)
  if (contact) {
    contact.unreadCount = 0
  }
  
  // 跳转到该联系人的聊天页面
  router.push(`/messages/${userId}`)
}

// 发送消息
const handleSend = async () => {
  const message = inputMsg.value.trim()
  if (!message || sending.value || !currentTargetId.value) return
  
  sending.value = true
  
  try {
    // 先添加临时消息到列表
    const tempMsg = {
      message_id: `temp_${Date.now()}`,
      sender_id: userStore.userInfo.user_name,
      sender_nickname: userStore.userInfo.nickname,
      sender_avatar: userStore.userInfo.avatar_url,
      receiver_id: currentTargetId.value,
      content: message,
      time: new Date().toISOString(),
      status: 'sending'
    }
    
    rawMessages.value.push(tempMsg)
    inputMsg.value = ''
    scrollToBottom()
    
    // 发送到服务器
    await sendMsg({
      receiver_id: currentTargetId.value,
      content: message
    })
    
    // 更新消息状态
    const index = rawMessages.value.findIndex(m => m.message_id === tempMsg.message_id)
    if (index !== -1) {
      rawMessages.value[index].status = 'success'
    }
    
    // 重新获取消息列表
    await fetchMsgs()
    
  } catch (error) {
    // 标记发送失败
    const index = rawMessages.value.findIndex(m => m.message_id?.startsWith('temp_'))
    if (index !== -1) {
      rawMessages.value[index].status = 'failed'
    }
    
    ElMessage.error('发送失败：' + (error.message || '网络错误'))
  } finally {
    sending.value = false
  }
}

// 滚动处理
const handleScroll = ({ scrollTop }) => {
  if (scrollTop <= 100 && hasMore.value && !loadingHistory.value) {
    loadMoreHistory()
  }
}

const scrollToBottom = () => {
  nextTick(() => {
    if (msgScroll.value) {
      const scrollContainer = msgScroll.value.$el.querySelector('.el-scrollbar__wrap')
      if (scrollContainer) {
        scrollContainer.scrollTop = scrollContainer.scrollHeight
      }
    }
  })
}

// 加载更多历史消息
const loadMoreHistory = async () => {
  if (!currentTargetId.value || !hasMore.value || loadingHistory.value) return
  
  loadingHistory.value = true
  try {
    // TODO: 实现分页加载历史消息的API
    // const res = await getHistoryMessages({
    //   target_id: currentTargetId.value,
    //   page: page.value + 1,
    //   pageSize
    // })
    
    // if (res.messages && res.messages.length > 0) {
    //   rawMessages.value = [...res.messages, ...rawMessages.value]
    //   page.value++
    // }
    
    // hasMore.value = res.hasMore
  } catch (error) {
    console.error('加载历史消息失败:', error)
  } finally {
    loadingHistory.value = false
  }
}

// 时间格式化
const formatTimeShort = (time) => {
  if (!time) return ''
  const date = new Date(time)
  const now = new Date()
  const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24))
  
  if (diffDays === 0) {
    return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
  } else if (diffDays === 1) {
    return '昨天'
  } else if (diffDays < 7) {
    const days = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
    return days[date.getDay()]
  } else {
    return `${date.getMonth() + 1}/${date.getDate()}`
  }
}

const formatTimeFull = (time) => {
  if (!time) return ''
  const date = new Date(time)
  return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}:${date.getSeconds().toString().padStart(2, '0')}`
}

// 获取消息列表
const fetchMsgs = async () => {
  try {
    const res = await getMsgs()
    rawMessages.value = res.messages || []
    
    console.log("In Messages : rawMessages = " , rawMessages.value);
    

    // 如果当前有聊天对象，滚动到底部
    if (currentTargetId.value) {
      scrollToBottom()
    }
  } catch (err) {
    ElMessage.error('获取消息列表失败')
    console.error(err)
  }
}

// WebSocket 或定时刷新（可选）
let refreshInterval = null

// 监听路由变化
watch(() => route.params.id, (newId) => {
  if (newId) {
    // 清除该联系人的未读消息计数
    const contact = processedContactList.value.find(c => c.userId === newId)
    if (contact) {
      contact.unreadCount = 0
    }
    
    // 滚动到底部
    nextTick(() => {
      scrollToBottom()
    })
  }
})

// 组件生命周期
onMounted(() => {
  fetchMsgs()
  
  // 定时刷新消息（每30秒）
  refreshInterval = setInterval(fetchMsgs, 30000)
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>

<style scoped lang="scss">
.messages-container {
  max-width: 1200px;
  margin: 20px auto;
  padding: 0 20px;
  height: calc(100vh - 100px);
  min-height: 600px;
}

.chat-card {
  height: 100%;
  border-radius: 12px;
  border: none;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.chat-layout {
  display: flex;
  height: 100%;
}

/* 左侧联系人列表 */
.contact-list {
  width: 300px;
  border-right: 1px solid #f0f0f0;
  display: flex;
  flex-direction: column;
  background: #fafafa;
}

.list-header {
  padding: 20px;
  border-bottom: 1px solid #f0f0f0;
  background: white;
  
  h3 {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
    color: #333;
  }
}

.contact-scrollbar {
  flex: 1;
  height: 0;
}

.contact-item {
  display: flex;
  padding: 15px;
  gap: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  border-bottom: 1px solid #f5f5f5;
  background: white;
  position: relative;
  
  &:hover {
    background: #f9f9f9;
  }
  
  &.active {
    background: linear-gradient(135deg, #fff8f0 0%, #fff0e6 100%);
    border-right: 3px solid #ff6600;
    
    &::before {
      content: '';
      position: absolute;
      left: 0;
      top: 0;
      bottom: 0;
      width: 3px;
      background: #ff6600;
    }
  }
  
  &.has-unread {
    .name {
      font-weight: 600;
    }
  }
}

.contact-avatar {
  flex-shrink: 0;
  background: linear-gradient(135deg, #ff9838 0%, #ff6600 100%);
  font-weight: bold;
}

.contact-info {
  flex: 1;
  min-width: 0;
  overflow: hidden;
}

.name-time {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.name {
  font-weight: 500;
  font-size: 14px;
  color: #333;
  display: flex;
  align-items: center;
  gap: 6px;
}

.unread-badge {
  background: #ff4d4f;
  color: white;
  font-size: 10px;
  padding: 1px 5px;
  border-radius: 10px;
  min-width: 16px;
  text-align: center;
  line-height: 1;
}

.time {
  font-size: 12px;
  color: #999;
  flex-shrink: 0;
}

.last-msg {
  font-size: 13px;
  color: #666;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 右侧聊天窗口 */
.chat-window {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
}

.chat-header {
  padding: 15px 25px;
  background: white;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  z-index: 1;
  
  .header-avatar {
    background: linear-gradient(135deg, #36c 0%, #63f 100%);
  }
  
  .header-info {
    flex: 1;
    
    strong {
      font-size: 16px;
      color: #333;
      display: block;
    }
    
    .online-status {
      font-size: 12px;
      color: #52c41a;
    }
  }
}

.msg-display {
  flex: 1;
  padding: 20px;
  background: #f9f9f9;
}

.loading-more {
  text-align: center;
  padding: 10px;
  color: #999;
  font-size: 14px;
  
  .el-icon {
    margin-right: 8px;
    animation: rotating 2s linear infinite;
  }
}

.msg-content-inner {
  padding: 10px;
}

.msg-row {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  transition: all 0.3s ease;
  
  &:hover {
    .msg-bubble {
      box-shadow: 0 3px 8px rgba(0, 0, 0, 0.1);
    }
  }
  
  &.is-me {
    flex-direction: row-reverse;
  }
  
  &.is-system {
    justify-content: center;
    
    .msg-bubble {
      background: rgba(255, 102, 0, 0.1);
      border: 1px solid rgba(255, 102, 0, 0.2);
      
      .text {
        color: #ff6600;
        font-size: 13px;
      }
      
      .msg-time {
        display: none;
      }
    }
  }
}

.msg-avatar {
  flex-shrink: 0;
  align-self: flex-start;
  background: linear-gradient(135deg, #36c 0%, #63f 100%);
  font-weight: bold;
}

.msg-bubble {
  max-width: 60%;
  min-width: 60px;
  padding: 10px 15px;
  border-radius: 18px;
  background: white;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
  position: relative;
  
  .text {
    font-size: 14px;
    line-height: 1.6;
    color: #333;
    word-break: break-word;
    white-space: pre-wrap;
  }
  
  .msg-time {
    font-size: 11px;
    color: #ccc;
    margin-top: 4px;
    text-align: right;
  }
  
  .msg-status {
    position: absolute;
    right: -20px;
    bottom: 2px;
    
    .el-icon {
      font-size: 14px;
      
      &.sending-icon {
        color: #999;
        animation: rotating 1s linear infinite;
      }
      
      &.failed-icon {
        color: #ff4d4f;
      }
      
      &.success-icon {
        color: #52c41a;
      }
    }
  }
}

.is-me {
  .msg-bubble {
    background: linear-gradient(135deg, #ff9838 0%, #ff6600 100%);
    border-radius: 18px 18px 4px 18px;
    
    .text {
      color: white;
    }
    
    .msg-time {
      color: rgba(255, 255, 255, 0.7);
    }
  }
  
  .msg-avatar {
    background: #666;
  }
}

/* 输入区域 */
.input-area {
  padding: 20px;
  background: white;
  border-top: 1px solid #f0f0f0;
}

.input-tools {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
  
  .el-button {
    color: #666;
    
    &:hover {
      color: #ff6600;
    }
  }
}

.msg-input {
  :deep(.el-textarea__inner) {
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 12px;
    font-size: 14px;
    transition: all 0.3s;
    
    &:focus {
      border-color: #ff6600;
      box-shadow: 0 0 0 2px rgba(255, 102, 0, 0.1);
    }
    
    &:disabled {
      background: #f9f9f9;
      cursor: not-allowed;
    }
  }
}

.send-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
}

.tip {
  font-size: 12px;
  color: #999;
}

.btn-orange {
  background: linear-gradient(135deg, #ff9838 0%, #ff6600 100%);
  border: none;
  border-radius: 8px;
  padding: 8px 25px;
  font-weight: 500;
  transition: all 0.3s;
  
  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(255, 102, 0, 0.3);
  }
  
  &:active {
    transform: translateY(0);
  }
  
  &:disabled {
    background: #ccc;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
  }
}

/* 空状态 */
.empty-chat {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  text-align: center;
  
  .empty-illustration {
    margin-bottom: 20px;
    opacity: 0.6;
  }
  
  h3 {
    margin: 0 0 10px 0;
    font-size: 20px;
    color: #333;
    font-weight: 500;
  }
  
  p {
    margin: 0 0 8px 0;
    color: #666;
    font-size: 14px;
  }
  
  .empty-tip {
    color: #999;
    font-size: 13px;
  }
  
  .empty-actions {
    margin-top: 30px;
    width: 300px;
    display: flex;
    flex-direction: column;
    gap: 15px;
  }
  
  .search-input {
    width: 100%;
  }
}

/* 动画 */
@keyframes rotating {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .messages-container {
    padding: 0 10px;
    height: calc(100vh - 80px);
  }
  
  .contact-list {
    width: 100%;
    border-right: none;
  }
  
  .chat-window {
    display: none;
    
    &.active {
      display: flex;
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      z-index: 1000;
    }
  }
  
  .msg-bubble {
    max-width: 75%;
  }
}
</style>