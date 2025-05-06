<template>
    <div class="app-container">
        <el-card class="warning-settings" header="工单时效预警设置">
            <el-form :model="warningSettings" label-width="200px">
                <!-- 预警设置 -->
                <el-form-item label="初级预警（提前）：">
                    <el-input-number v-model="warningSettings.xHours" :min="0" controls-position="right" />
                    <span class="unit-text">小时</span>
                </el-form-item>

                <el-form-item label="中级警告（临近）：">
                    <el-input-number v-model="warningSettings.yHours" :min="0" controls-position="right" />
                    <span class="unit-text">小时</span>
                </el-form-item>

                <el-form-item label="最终通报（超时）：">
                    <el-input-number v-model="warningSettings.zHours" :min="0" controls-position="right" />
                    <span class="unit-text">小时</span>
                </el-form-item>

                <!-- 操作按钮 -->
                <el-form-item>
                    <el-button type="primary" @click="saveSettings">保存设置</el-button>
                    <el-button @click="resetForm">恢复默认</el-button>
                </el-form-item>
            </el-form>
        </el-card>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@utils/api'

// 默认值
const defaultSettings = {
    xHours: 72,  // 3天前预警
    yHours: 24,  // 1天前警告
    zHours: 2     // 超时2小时通报
}

// 响应式数据
const warningSettings = ref({ ...defaultSettings })

// 加载保存的设置
const loadSettings = async () => {
    try {
        const res = await api.get('/ticket/settings')
        warningSettings.value = res.data
    } catch (e) {
        ElMessage.error('设置加载失败，使用默认配置')
    }
}

// 保存设置
const saveSettings = async () => {
    try {
        await api.post('/ticket/settings', warningSettings.value)
        ElMessage.success('设置保存成功')
    } catch (e) {
        ElMessage.error('设置保存失败')
    }
}

// 重置表单
const resetForm = () => {
    warningSettings.value = { ...defaultSettings }
    ElMessage.info('已恢复默认设置')
}

// 初始化加载
onMounted(loadSettings)
</script>

<style scoped>
.warning-settings {
    max-width: 800px;
    margin: 20px auto;
}

.unit-text {
    margin-left: 10px;
    color: #606266;
}

.el-input-number {
    width: 200px;
}
</style>