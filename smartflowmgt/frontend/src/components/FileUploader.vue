<script setup lang="ts">
import { ref } from 'vue'
import { createFileChunks, getFileHash } from '@/utils/fileUpload'
import api from '@/utils/api'
import { defineEmits } from 'vue'

const emit = defineEmits(['upload-success'])

const file = ref<File>()
const progress = ref(0)

const upload = async () => {
  if (!file.value) return

  // 生成唯一标识
  const fileHash = await getFileHash(file.value)
  const chunks = createFileChunks(file.value)

  // 创建上传任务
  const { data: { upload_id } } = await api.post('/api/uploads/', {
    filename: file.value.name,
    hash: fileHash,
    total_chunks: chunks.length
  })

  // 并行上传分片
  await Promise.all(chunks.map(async (chunk, index) => {
    const formData = new FormData()
    formData.append('chunk', chunk)
    formData.append('chunk_number', index.toString())

    await api.post(`/api/uploads/${upload_id}/chunks/`, formData, {
      onUploadProgress: e => {
        progress.value = Math.round((e.loaded / e.total!) * 100)
      }
    })
  }))

  // 完成上传
  const completeRes = await api.post(`/api/uploads/${upload_id}/complete/`)
  console.log(completeRes, "completeRes")
  if (completeRes.status === 200) {
    emit('upload-success', completeRes.data) // 触发自定义事件
  }
}
</script>

<template>
  <input type="file" @change="e => file = e.target.files?.[0]">
  <button @click="upload">上传</button>
  <progress :value="progress" max="100"></progress>
</template>