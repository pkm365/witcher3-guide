<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { withBase } from 'vitepress'

interface Ach { api: string; name: string; desc: string; icon: string; icongray: string; group: string; group_name: string; flags: string[] }

const achs = ref<Ach[]>([])
const unlocked = ref<Map<string, string>>(new Map())
const filter = ref<'all' | 'got' | 'todo' | 'missable'>('all')

onMounted(async () => {
  try {
    const r = await fetch(withBase('/achievements.json'))
    if (r.ok) achs.value = await r.json()
  } catch {}
  try {
    const r = await fetch(withBase('/progress.json'))
    if (r.ok) {
      const p = await r.json()
      unlocked.value = new Map((p.unlocked_all ?? []).map((u: any) => [u.api, u.unlocktime_str]))
    }
  } catch {}
})

const isGot = (api: string) => unlocked.value.has(api)
const gotCount = computed(() => achs.value.filter(a => isGot(a.api)).length)

const groups = computed(() => {
  const order = ['主线剧情', '难度通关', '战斗技巧与刷量', '收集与成长', '昆特牌', '石之心 DLC', '血与酒 DLC']
  return order.map(name => ({
    name,
    items: achs.value.filter(a => a.group_name === name && match(a)),
  })).filter(g => g.items.length)
})

function match(a: Ach) {
  if (filter.value === 'got') return isGot(a.api)
  if (filter.value === 'todo') return !isGot(a.api)
  if (filter.value === 'missable') return a.flags.includes('missable') || a.flags.includes('choice')
  return true
}
const flagLabel: Record<string, string> = { missable: '易错过', choice: '结局互斥', grind: '刷量' }
</script>

<template>
  <div class="ag-wrap" v-if="achs.length">
    <div class="ag-head">
      <span class="ag-count">已解锁 {{ gotCount }}/{{ achs.length }}</span>
      <div class="ag-filters">
        <button :class="{ on: filter === 'all' }" @click="filter = 'all'">全部</button>
        <button :class="{ on: filter === 'got' }" @click="filter = 'got'">已解锁</button>
        <button :class="{ on: filter === 'todo' }" @click="filter = 'todo'">未解锁</button>
        <button :class="{ on: filter === 'missable' }" @click="filter = 'missable'">⚠ 易错过/互斥</button>
      </div>
    </div>
    <div v-for="g in groups" :key="g.name" class="ag-group">
      <h3 class="ag-group-name">{{ g.name }}</h3>
      <div class="ag-grid">
        <div v-for="a in g.items" :key="a.api" class="ag-item" :class="{ got: isGot(a.api) }"
             :title="a.desc || a.name">
          <img :src="isGot(a.api) ? a.icon : a.icongray" :alt="a.name" loading="lazy" />
          <div class="ag-info">
            <span class="ag-name">{{ a.name }} <span v-if="isGot(a.api)" class="ag-check">✓</span></span>
            <span class="ag-desc">{{ a.desc }}</span>
            <span class="ag-meta">
              <span v-for="f in a.flags" :key="f" class="ag-flag" :class="f">{{ flagLabel[f] }}</span>
              <span v-if="isGot(a.api)" class="ag-time">{{ unlocked.get(a.api) }}</span>
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div v-else class="ag-loading">成就数据加载中…</div>
</template>

<style scoped>
.ag-wrap { margin: 16px 0 32px; }
.ag-head { display: flex; gap: 14px; align-items: center; flex-wrap: wrap; margin-bottom: 6px; }
.ag-count { font-weight: 700; }
.ag-filters { display: flex; gap: 8px; flex-wrap: wrap; }
.ag-filters button {
  padding: 6px 14px; border-radius: 999px; cursor: pointer; font-size: 13px;
  border: 1px solid var(--vp-c-divider); background: transparent; color: var(--vp-c-text-2);
}
.ag-filters button.on { border-color: #d43a2f; color: #e05545; background: rgba(212, 58, 47, 0.08); font-weight: 600; }
.ag-group { margin-top: 22px; }
.ag-group-name { font-size: 15px; margin-bottom: 10px; }
.ag-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 10px; }
.ag-item {
  display: flex; gap: 10px; padding: 10px; border-radius: 10px;
  border: 1px solid var(--vp-c-divider); background: var(--vp-c-bg-soft);
}
.ag-item img { width: 44px; height: 44px; border-radius: 8px; flex-shrink: 0; }
.ag-item:not(.got) img { filter: grayscale(1); opacity: 0.55; }
.ag-info { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.ag-name { font-size: 13px; font-weight: 600; }
.ag-check { color: #d43a2f; }
.ag-desc { font-size: 12px; color: var(--vp-c-text-3); line-height: 1.4; }
.ag-meta { display: flex; gap: 6px; align-items: center; flex-wrap: wrap; margin-top: 2px; }
.ag-flag { font-size: 10px; padding: 1px 7px; border-radius: 999px; border: 1px solid; }
.ag-flag.missable { color: #e0a02f; border-color: rgba(224, 160, 47, 0.5); }
.ag-flag.choice { color: #e05545; border-color: rgba(224, 85, 69, 0.5); }
.ag-flag.grind { color: #7aa2e0; border-color: rgba(122, 162, 224, 0.5); }
.ag-time { font-size: 10px; color: var(--vp-c-text-3); }
.ag-loading { text-align: center; color: var(--vp-c-text-3); padding: 24px 0; }
</style>
