<script setup>
import api from '@/utils/api'
import { ref, watchEffect, onUnmounted } from 'vue'

const props = defineProps(['modelValue', 'fileIds'])
const previewUrl = ref('')
const loading = ref(false)

// 获取文件预览URL
watchEffect(async () => {
    if (props.fileIds?.length) {
        loading.value = true
        try {
            const { data } = await api.get(`/api/files/${props.fileIds[0]}/preview`, {
                responseType: 'blob'
            })
            previewUrl.value = URL.createObjectURL(data)
        } catch (error) {
            console.error('文件加载失败:', error)
            previewUrl.value = ''
        } finally {
            loading.value = false
        }
    }
})

// 清理内存
onUnmounted(() => {
    if (previewUrl.value) {
        URL.revokeObjectURL(previewUrl.value)
    }
})
</script>

<template>
    <el-dialog :model-value="modelValue" @close="$emit('update:modelValue', false)" width="70%">
        <template #header>
            <div class="dialog-header">
                <span>附件预览</span>
                <el-button type="danger" @click="$emit('update:modelValue', false)" circle plain size="small">
                    ×
                </el-button>
            </div>
        </template>

        <div v-loading="loading" class="preview-container">
            <embed v-if="previewUrl" :src="previewUrl" type="application/pdf" width="100%" height="600px">
            <el-empty v-else description="无法预览该文件" />
        </div>
    </el-dialog>
</template>

<style scoped>
.preview-container {
    height: 70vh;
    display: flex;
    justify-content: center;
    align-items: center;
}
</style>