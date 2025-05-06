<template>
    <div class="app-container">
        <el-row :gutter="20">
            <!-- 待处理 -->
            <el-col :span="8">
                <el-card class="status-column" shadow="hover">
                    <template #header>
                        <span class="column-title">待处理（{{ pendingTickets.length }}）</span>
                    </template>
                    <div v-for="ticket in pendingTickets" :key="ticket.id" class="ticket-card">
                        <div class="ticket-header">
                            <span class="ticket-code">#{{ ticket.ticket_code }}</span>
                            <span class="ticket-title">{{ ticket.title }}</span>
                        </div>
                        <div class="countdown" :class="getCountdownClass(ticket)">
                            剩余时间：{{ formatCountdown(ticket.deadline) }}
                        </div>
                    </div>
                </el-card>
            </el-col>

            <!-- 处理中 -->
            <el-col :span="8">
                <el-card class="status-column" shadow="hover">
                    <template #header>
                        <span class="column-title">处理中（{{ processingTickets.length }}）</span>
                    </template>
                    <div v-for="ticket in processingTickets" :key="ticket.id" class="ticket-card">
                        <div class="ticket-header">
                            <span class="ticket-code">#{{ ticket.ticket_code }}</span>
                            <span class="ticket-title">{{ ticket.title }}</span>
                        </div>
                        <div class="countdown" :class="getCountdownClass(ticket)">
                            剩余时间：{{ formatCountdown(ticket.deadline) }}
                        </div>
                    </div>
                </el-card>
            </el-col>

            <!-- 已完成 -->
            <el-col :span="8">
                <el-card class="status-column" shadow="hover">
                    <template #header>
                        <span class="column-title">已完成（{{ completedTickets.length }}）</span>
                    </template>
                    <div v-for="ticket in completedTickets" :key="ticket.id" class="ticket-card">
                        <div class="ticket-header">
                            <span class="ticket-code">#{{ ticket.ticket_code }}</span>
                            <span class="ticket-title">{{ ticket.title }}</span>
                        </div>
                        <div class="completed-time">
                            完成时间：{{ formatDateTime(ticket.update_time) }}
                        </div>
                    </div>
                </el-card>
            </el-col>
        </el-row>
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import api from '@utils/api'
import { ElMessage } from 'element-plus'

// 数据获取
const tickets = ref([])
let refreshInterval

const fetchTickets = async () => {
    try {
        const res = await api.get('/ticket/kanban')
        tickets.value = res.data.map(ticket => ({
            ...ticket,
            update_time: ticket.update_time
        }))
    } catch (e) {
        ElMessage.error('看板数据加载失败')
    }
}

// 计算属性
const pendingTickets = computed(() =>
    tickets.value.filter(t => t.status === 'handle')
)

const processingTickets = computed(() =>
    tickets.value.filter(t => t.status === 'handling')
)

const completedTickets = computed(() =>
    tickets.value.filter(t => t.status === 'handled')
)

// 时间格式化
const formatDateTime = (timestamp) => {
    return new Date(timestamp).toLocaleString()
}

const formatCountdown = (deadline) => {
    const now = new Date()
    const end = new Date(deadline)
    const diff = end - now

    if (diff <= 0) return '已过期'

    const hours = Math.floor(diff / (1000 * 60 * 60))
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
    return `${hours}小时${minutes}分钟`
}

// 样式处理
const getCountdownClass = (ticket) => {
    const now = new Date()
    const end = new Date(ticket.deadline)
    const diffHours = (end - now) / (1000 * 60 * 60)

    if (diffHours < 1) return 'urgent'
    if (diffHours < 24) return 'warning'
    return 'normal'
}

// 自动刷新
onMounted(() => {
    fetchTickets()
    refreshInterval = setInterval(fetchTickets, 60000) // 每分钟刷新
})

onUnmounted(() => {
    clearInterval(refreshInterval)
})
</script>

<style scoped>
.status-column {
    height: calc(100vh - 180px);
    overflow-y: auto;
}

.column-title {
    font-size: 18px;
    font-weight: 600;
}

.ticket-card {
    margin-bottom: 15px;
    padding: 15px;
    border: 1px solid #ebeef5;
    border-radius: 4px;
}

.ticket-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 10px;
}

.ticket-code {
    color: #909399;
}

.countdown {
    font-size: 14px;

    &.urgent {
        color: #f56c6c;
    }

    &.warning {
        color: #e6a23c;
    }

    &.normal {
        color: #67c23a;
    }
}

.completed-time {
    color: #909399;
    font-size: 12px;
}
</style>