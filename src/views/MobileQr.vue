<template>
  <div class="qr-fullscreen">
    <div class="qr-card">
      <div class="qr-title">浙江省医院品管大赛</div>
      <div class="qr-subtitle">面谈评审专家请扫码登录</div>
      <qrcode-vue :value="mobileLoginUrl" :size="qrSize" level="H" class="qr-code" />
      <div class="qr-hint">使用手机扫描上方二维码，以专家账号登录后即可打分</div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import QrcodeVue from 'qrcode.vue'

const mobileLoginUrl = `${window.location.origin}${import.meta.env.BASE_URL}login`
const qrSize = computed(() => Math.min(window.innerWidth, window.innerHeight) * 0.38)
</script>

<style scoped>
.qr-fullscreen {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1a237e 0%, #283593 50%, #1565c0 100%);
}

.qr-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  padding: 52px 60px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 24px;
  backdrop-filter: blur(8px);
}

.qr-title {
  font-size: 32px;
  font-weight: 700;
  color: #fff;
  letter-spacing: 2px;
}

.qr-subtitle {
  font-size: 20px;
  color: #90caf9;
  letter-spacing: 1px;
}

.qr-code {
  background: #fff;
  padding: 16px;
  border-radius: 12px;
}

.qr-hint {
  font-size: 15px;
  color: rgba(255, 255, 255, 0.7);
  text-align: center;
  max-width: 360px;
  line-height: 1.6;
}

</style>
