<template>
    <div class="app-wrapper">
        <el-container>
            <el-aside width="200px" class="sidebar-container">
                <Menu />
            </el-aside>
            <el-container>
                <el-header>
                    <Header />
                </el-header>
                <el-main>
                    <Tabs /><router-view />
                </el-main>
            </el-container>
        </el-container>
    </div>
</template>


<script setup>
import Menu from '@/layout/menu/index.vue'
import Header from '@/layout/header/index.vue'
import Tabs from '@/layout/tabs/index.vue'
import Footer from '@/layout/footer/index.vue'
</script>

<style scoped>
.app-wrapper {
    position: relative;
    width: 100%;
    height: 100vh;
    display: flex;
    flex-direction: column;
}

.sidebar-container {
    background-color: #2d3a4b;
    height: 135vh;
}

.el-header,
.el-footer {
    background-color: #B3C0D1;
    color: #333;
    text-align: center;
    line-height: 60px;
}

.el-aside {
    background-color: #D3DCE6;
    color: #333;
    text-align: center;
    line-height: 200px;
}

.el-main {
    color: #333;
}

body>.el-container {
    margin-bottom: 40px;
}

.el-container:nth-child(5) .el-aside,
.el-container:nth-child(6) .el-aside {
    line-height: 260px;
}

.el-container:nth-child(7) .el-aside {
    line-height: 320px;
}
</style>