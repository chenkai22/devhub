<template>
    <div class="app-container">
        <el-card header="工单处理排行榜">
            <el-table :data="rankingData" stripe>
                <el-table-column label="排名" width="80">
                    <template #default="scope">
                        <el-tag v-if="scope.$index < 3" type="danger">{{ scope.$index + 1 }}</el-tag>
                        <el-tag v-else type="info">{{ scope.$index + 1 }}</el-tag>
                    </template>
                </el-table-column>

                <el-table-column label="处理人">
                    <template #default="{ row }">
                        <div class="user-info">
                            <el-avatar :size="32" :src="row.avatar || defaultAvatar" />
                            <span class="name">{{ row.username }}</span>
                        </div>
                    </template>
                </el-table-column>

                <el-table-column prop="count" label="处理数量" sortable />
                <el-table-column label="平均用时">
                    <template #default="{ row }">{{ row.avgTime }} 小时</template>
                </el-table-column>
            </el-table>
        </el-card>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@utils/api'

const defaultAvatar = new URL('@/assets/default-avatar.png', import.meta.url).href
const rankingData = ref([])

const loadData = async () => {
    const res = await api.get('/ticket/ranking')
    rankingData.value = res.data.map(item => ({
        ...item,
        avgTime: (item.totalTime / item.count || 0).toFixed(1)
    }))
}

onMounted(loadData)
</script>

<style scoped>
.user-info {
    display: flex;
    align-items: center;
    gap: 12px;
}

.name {
    font-weight: 500;
}
</style>