<template>
    <el-menu default-active="2" class="el-menu-vertical-demo" @open="handleOpen" @close="handleClose"
        style="height:100%;border-right:none" background-color="#2d3a4b" text-color="#b0bac5" active-text-color="#fff"
        router :default-active="'/index'">
        <el-menu-item index="/index" @click="openTab({ name: '首页', path: '/index' })">
            <i class="el-icon-s-home"></i>
            <span slot="title">首页</span>
        </el-menu-item>
        <el-sub-menu :index="menu.path" v-for="menu in menuList">
            <template #title>
                <el-icon>
                    <location />
                </el-icon>
                <span>{{ menu.name }}</span>
            </template>
            <el-menu-item-group>
                <el-menu-item :index="item.path" v-for="item in menu.children"  @click="openTab(item)">{{ item.name }}</el-menu-item>
            </el-menu-item-group>
        </el-sub-menu>
    </el-menu>
</template>

<script setup>
import store from '@/stores'
import { Location } from '@element-plus/icons-vue'

const menuList = JSON.parse(sessionStorage.getItem('menuList'))
const openTab = (item) => {
    store.commit('ADD_TABS', item)
}
</script>

<style lang="scss" scoped></style>