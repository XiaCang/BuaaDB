<template>
  <div class="messages-container">
    <el-card class="chat-card" :body-style="{ padding: '0px' }">
      <div class="chat-layout">
        <div class="contact-list">
          <div class="list-header">
            <h3>消息中心</h3>
          </div>
          <el-scrollbar>
            <div 
              v-for="contact in contactList" 
              :key="contact.userId" 
              class="contact-item"
              :class="{ active: currentTargetId === contact.userId }"
              @click="selectContact(contact.userId)"
            >
              <el-avatar :size="40" class="contact-avatar">{{ contact.userId }}</el-avatar>
              <div class="contact-info">
                <div class="name-time">
                  <span class="name">用户 {{ contact.userId }}</span>
                  <span class="time">{{ formatTimeShort(contact.lastTime) }}</span>
                </div>
                <div class="last-msg">{{ contact.lastMsg }}</div>
              </div>
            </div>
            <el-empty v-if="contactList.length === 0" description="暂无消息" />
          </el-scrollbar>
        </div>

        <div class="chat-window">
          <template v-if="currentTargetId">
            <div class="chat-header">
              <span>与 <strong>用户 {{ currentTargetId }}</strong> 的对话</span>
            </div>

            <el-scrollbar ref="msgScroll" class="msg-display">
              <div class="msg-content-inner">
                <div 
                  v-for="(msg, index) in currentChatHistory" 
                  :key="index" 
                  class="msg-row"
                  :class="{ 'is-me': msg.sender_id === userStore.userInfo.id }"
                >
                  <el-avatar :size="32" class="msg-avatar">
                    {{ msg.sender_id === userStore.userInfo.id ? '我' : msg.sender_id }}
                  </el-avatar>
                  <div class="msg-bubble">
                    <div class="text">{{ msg.content }}</div>
                    <div class="msg-time">{{ formatTimeFull(msg.created_at) }}</div>
                  </div>
                </div>
              </div>
            </el-scrollbar>

            <div class="input-area">
              <el-input
                v-model="inputMsg"
                type="textarea"
                :rows="3"
                placeholder="输入消息..."
                @keyup.enter.exact="handleSend"
                resize="none"
              />
              <div class="send-bar">
                <span class="tip">Enter 发送</span>
                <el-button type="primary" class="btn-orange" @click="handleSend" :loading="sending">发送</el-button>
              </div>
            </div>
          </template>

          <div v-else class="empty-chat">
            <el-icon :size="60" color="#e0e0e0"><ChatDotRound /></el-icon>
            <p>请选择一个联系人开始聊天</p>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick } from 'vue'
import { ChatDotRound } from '@element-plus/icons-vue'
import { getMsgs, sendMsg } from '@/api/index'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

const userStore = useUserStore()
const rawMessages = ref([])
const currentTargetId = ref(null)
const inputMsg = ref('')
const sending = ref(false)
const msgScroll = ref(null)

// 1. 获取消息并聚合联系人
const fetchMsgs = async () => {
  try {
    const res = await getMsgs()
    rawMessages.value = res.messages || []
    // 聚合逻辑：找出所有和我聊天的人的ID
    // 如果没有选定对象，且有消息，默认选第一个
    if (!currentTargetId.value && contactList.value.length > 0) {
      currentTargetId.value = contactList.value[0].userId
    }
    scrollToBottom()
  } catch (err) {}
}

// 2. 计算属性：处理联系人列表
const contactList = computed(() => {
  const contacts = {}
  const myId = userStore.userInfo.id

  rawMessages.value.forEach(m => {
    // 对方的ID（如果是发出的，则是接收者；如果是收到的，则是发送者）
    // 注意：你的get_msgs返回只有sender_id，所以需要判断 sender_id 是否是我
    const otherId = m.sender_id === myId ? m.receiver_id : m.sender_id // 假设后端返回包含receiver_id
    // 如果后端只给 sender_id，则只能聚拢收到的消息。这里假设逻辑完整：
    const peerId = m.sender_id === myId ? m.receiver_id : m.sender_id
    
    if (!contacts[peerId]) {
      contacts[peerId] = { userId: peerId, lastMsg: m.content, lastTime: m.created_at }
    } else if (new Date(m.created_at) > new Date(contacts[peerId].lastTime)) {
      contacts[peerId].lastMsg = m.content
      contacts[peerId].lastTime = m.created_at
    }
  })
  
  return Object.values(contacts).sort((a, b) => new Date(b.lastTime) - new Date(a.lastTime))
})

// 3. 计算属性：当前选中联系人的聊天历史
const currentChatHistory = computed(() => {
  const myId = userStore.userInfo.id
  return rawMessages.value.filter(m => 
    (m.sender_id === myId && m.receiver_id === currentTargetId.value) ||
    (m.sender_id === currentTargetId.value && m.receiver_id === myId)
  ).sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
})

const selectContact = (id) => {
  currentTargetId.value = id
  scrollToBottom()
}

// 4. 发送消息
const handleSend = async () => {
  if (!inputMsg.value.trim() || sending.value) return
  
  sending.value = true
  try {
    await sendMsg({
      receiver_id: currentTargetId.value,
      content: inputMsg.value
    })
    inputMsg.value = ''
    await fetchMsgs() // 重新拉取消息
  } catch (err) {
  } finally {
    sending.value = false
  }
}

const scrollToBottom = () => {
  nextTick(() => {
    if (msgScroll.value) {
      const inner = msgScroll.value.$el.querySelector('.el-scrollbar__wrap')
      inner.scrollTop = inner.scrollHeight
    }
  })
}

const formatTimeShort = (t) => {
  const d = new Date(t)
  return `${d.getHours()}:${String(d.getMinutes()).padStart(2, '0')}`
}

const formatTimeFull = (t) => new Date(t).toLocaleString()

onMounted(fetchMsgs)
</script>

<style scoped>
.messages-container {
  max-width: 1100px;
  margin: 30px auto;
  padding: 0 20px;
  height: calc(100vh - 150px);
}

.chat-card {
  height: 100%;
  border-radius: 12px;
  border: none;
  overflow: hidden;
}

.chat-layout {
  display: flex;
  height: 100%;
}

/* 左侧列表 */
.contact-list {
  width: 280px;
  border-right: 1px solid #f0f0f0;
  display: flex;
  flex-direction: column;
}

.list-header {
  padding: 20px;
  border-bottom: 1px solid #f0f0f0;
}
.list-header h3 { margin: 0; font-size: 18px; }

.contact-item {
  display: flex;
  padding: 15px;
  gap: 12px;
  cursor: pointer;
  transition: background 0.2s;
}

.contact-item:hover { background-color: #f9f9f9; }
.contact-item.active { background-color: #fff5e6; }

.contact-avatar { background: #ff9838; flex-shrink: 0; }

.contact-info {
  flex: 1;
  overflow: hidden;
}

.name-time {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}

.name { font-weight: bold; font-size: 14px; }
.time { font-size: 11px; color: #bbb; }

.last-msg {
  font-size: 12px;
  color: #999;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 右侧聊天窗 */
.chat-window {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #fdfdfd;
}

.chat-header {
  padding: 15px 25px;
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  font-size: 15px;
}

.msg-display {
  flex: 1;
  padding: 20px;
}

.msg-content-inner {
  padding: 20px;
}

.msg-row {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.msg-bubble {
  max-width: 70%;
  padding: 10px 15px;
  border-radius: 2px 12px 12px 12px;
  background: #fff;
  box-shadow: 0 2px 6px rgba(0,0,0,0.05);
  position: relative;
}

.text { font-size: 14px; line-height: 1.6; color: #333; }
.msg-time { font-size: 10px; color: #ccc; margin-top: 5px; }

/* 我的消息样式 */
.msg-row.is-me {
  flex-direction: row-reverse;
}

.is-me .msg-bubble {
  background: #ff6600;
  color: #fff;
  border-radius: 12px 2px 12px 12px;
}
.is-me .text { color: #fff; }
.is-me .msg-time { color: rgba(255,255,255,0.7); }
.is-me .msg-avatar { background: #444; }

/* 输入区 */
.input-area {
  padding: 20px;
  background: #fff;
  border-top: 1px solid #f0f0f0;
}

.send-bar {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 15px;
  margin-top: 10px;
}

.tip { font-size: 12px; color: #bbb; }

.btn-orange {
  background: #ff6600;
  border: none;
  padding: 8px 25px;
}

.empty-chat {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #ccc;
}
</style>