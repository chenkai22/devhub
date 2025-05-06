<template>
    <el-dropdown trigger="click">
        <span class="el-dropdown-link">
            <el-avatar shape="square" :size="40" :src="squareUrl" />
            &nbsp;&nbsp;{{ currentUser.username }}
            <el-icon class="el-icon--right">
                <arrow-down />
            </el-icon>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item @click="logout">安全退出</el-dropdown-item>
          </el-dropdown-menu>
        </template>
    </el-dropdown>
</template>
<script setup>
import { ArrowDown } from '@element-plus/icons-vue'
import { ref } from 'vue'
import router from '@/router'
import store from '@/stores'

const currentUser = ref(JSON.parse(sessionStorage.getItem('currentUser')) || {})

const menuList = JSON.parse(sessionStorage.getItem('menuList')) || []
const defaultAvatar = new URL('@/assets/default-avatar.png', import.meta.url).href
const squareUrl = menuList[0]?.children?.[0]?.img || defaultAvatar

const logout = () => {
    window.sessionStorage.clear()
    store.commit('RESET_TAB')
    router.replace('/login')
}
</script>

<style lang="scss" scoped>
.el-dropdown {
    position: relative;
    top: 8px;
}

.el-dropdown-link {
    cursor: pointer;
    color: #303133;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
}
</style>
