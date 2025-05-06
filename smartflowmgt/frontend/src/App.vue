<template>
  <RouterView />
</template>

<script setup>
import { RouterLink, RouterView } from 'vue-router'
import HelloWorld from './components/HelloWorld.vue'
import { watch } from 'vue'
import { useRoute } from 'vue-router'
import store from '@/stores'

const route = useRoute()

watch(route, (newRoute) => {
  if (newRoute.name === '个人中心') {
    let obj = {
      name: newRoute.name,
      path: newRoute.path
    }
    store.commit('ADD_TABS', obj)
  }
})
</script>

<style scoped>
html,
body,
#app {
  height: 100%;
  width: 100%;
}

.app-container {
  padding: 20px
}
</style>
