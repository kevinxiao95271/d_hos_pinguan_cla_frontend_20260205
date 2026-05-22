<template>
  <router-view />
</template>

<script setup>
import { onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const VERSION_KEY = 'app_version'

const checkVersion = async () => {
  try {
    const res = await fetch(`${import.meta.env.BASE_URL}version.txt?_=${Date.now()}`, { cache: 'no-store' })
    if (!res.ok) return
    const remote = (await res.text()).trim()
    const local = sessionStorage.getItem(VERSION_KEY)
    if (!local) {
      sessionStorage.setItem(VERSION_KEY, remote)
    } else if (local !== remote) {
      sessionStorage.setItem(VERSION_KEY, remote)
      window.location.reload(true)
    }
  } catch {
    // 网络异常不影响正常使用
  }
}

onMounted(checkVersion)
watch(() => route.path, checkVersion)
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  width: 100%;
  height: 100%;
  font-family: 'Microsoft YaHei', 'Helvetica Neue', Helvetica, Arial, sans-serif;
}
</style>
