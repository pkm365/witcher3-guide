<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { withBase } from 'vitepress'

const p = ref<any>(null)
onMounted(async () => {
  try {
    const r = await fetch(withBase('/progress.json'))
    if (r.ok) p.value = await r.json()
  } catch {}
})
const pct = computed(() => {
  if (!p.value) return 0
  const a = p.value.achievements
  return a.total ? Math.round((a.unlocked / a.total) * 100) : 0
})
const hours = computed(() => {
  if (!p.value) return ''
  const m = p.value.playtime_minutes || 0
  return `${Math.floor(m / 60)} 小时 ${m % 60} 分`
})
</script>

<template>
  <div class="w3-banner" v-if="p">
    <div class="w3-banner-title">🐺 我的全成就进度</div>
    <div class="w3-bar"><div class="w3-fill" :style="'width:' + pct + '%'"></div></div>
    <div class="w3-stats">
      <span>成就 <b>{{ p.achievements.unlocked }}/{{ p.achievements.total }}</b>（{{ pct }}%）</span>
      <span>总时长 <b>{{ hours }}</b></span>
      <span class="w3-updated">同步于 {{ (p.updated_at || '').replace('T', ' ').slice(0, 16) }}</span>
    </div>
  </div>
</template>

<style scoped>
.w3-banner {
  margin: 20px 0 28px; padding: 18px 20px; border-radius: 14px;
  background: linear-gradient(135deg, rgba(180, 30, 30, 0.1), rgba(160, 170, 180, 0.06));
  border: 1px solid rgba(200, 205, 210, 0.25);
}
.w3-banner-title { font-size: 16px; font-weight: 700; margin-bottom: 12px; }
.w3-bar { height: 8px; border-radius: 4px; background: var(--vp-c-bg-mute); overflow: hidden; margin-bottom: 10px; }
.w3-fill { height: 100%; border-radius: 4px; background: linear-gradient(90deg, #8a939c, #d43a2f); transition: width 0.6s; }
.w3-stats { display: flex; gap: 20px; flex-wrap: wrap; font-size: 13px; color: var(--vp-c-text-2); }
.w3-stats b { color: var(--vp-c-text-1); }
.w3-updated { margin-left: auto; color: var(--vp-c-text-3); }
</style>
