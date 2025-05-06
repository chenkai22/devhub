<template>
    <el-icon>
        <HomeFilled />
    </el-icon>
    <el-breadcrumb separator="/">
        <el-breadcrumb-item v-for="(item, index) in breadcrumbList"><span>{{ item.name
                }}</span></el-breadcrumb-item>
    </el-breadcrumb>
</template>

<script setup>
import { HomeFilled } from '@element-plus/icons-vue'
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
const route = useRoute()

const breadcrumbList = ref([])

const initBreadcrumbList = () => {
    breadcrumbList.value = route.matched;
    console.log("匹配的路由是", route.matched)
}

watch(route, () => {
    initBreadcrumbList()
}, { deep: true, immediate: true })
</script>

<style lang="scss" scoped></style>