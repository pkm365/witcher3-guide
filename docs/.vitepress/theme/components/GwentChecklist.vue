<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import cardsData from './gwent-cards.json'

interface GwentCard {
  id: number
  name: string
  faction: string
  set: 'base' | 'hos' | 'baw'
  how: string
  sources: string[]
  missable: boolean
}

const cards = cardsData as GwentCard[]
const LS_KEY = 'w3-gwent-collected'

const owned = ref<Set<number>>(new Set())
onMounted(() => {
  try {
    const raw = localStorage.getItem(LS_KEY)
    if (raw) owned.value = new Set(JSON.parse(raw))
  } catch {}
})

function save() {
  try { localStorage.setItem(LS_KEY, JSON.stringify([...owned.value])) } catch {}
}

function toggle(id: number) {
  const next = new Set(owned.value)
  if (next.has(id)) next.delete(id)
  else next.add(id)
  owned.value = next
  save()
}

function resetAll() {
  if (typeof confirm === 'function' && !confirm('清空全部勾选记录？')) return
  owned.value = new Set()
  save()
}

const setTab = ref<'base' | 'hos' | 'baw'>('base')
const filterMode = ref<'all' | 'missing' | 'owned'>('all')
const query = ref('')

const SETS = [
  { key: 'base', label: '本体 · 成就口径' },
  { key: 'hos', label: '石之心' },
  { key: 'baw', label: '血与酒' },
] as const

const FACTION_ORDER = ['中立', '北方领域', '尼弗迦德', '松鼠党', '怪物', '史凯利杰', '领袖']

function countOf(set: string) {
  const all = cards.filter((c) => c.set === set)
  return { got: all.filter((c) => owned.value.has(c.id)).length, total: all.length }
}

const baseCount = computed(() => countOf('base'))
const basePct = computed(() =>
  baseCount.value.total ? Math.round((baseCount.value.got / baseCount.value.total) * 100) : 0
)

const groups = computed(() => {
  const q = query.value.trim()
  let list = cards.filter((c) => c.set === setTab.value)
  if (filterMode.value === 'missing') list = list.filter((c) => !owned.value.has(c.id))
  if (filterMode.value === 'owned') list = list.filter((c) => owned.value.has(c.id))
  if (q) list = list.filter((c) => c.name.includes(q) || c.sources.some((s) => s.includes(q)))
  const byFaction = new Map<string, GwentCard[]>()
  for (const c of list) {
    if (!byFaction.has(c.faction)) byFaction.set(c.faction, [])
    byFaction.get(c.faction)!.push(c)
  }
  return FACTION_ORDER.filter((f) => byFaction.has(f)).map((f) => {
    const items = byFaction.get(f)!
    const all = cards.filter((c) => c.set === setTab.value && c.faction === f)
    return { faction: f, items, got: all.filter((c) => owned.value.has(c.id)).length, total: all.length }
  })
})

const missableLeft = computed(
  () => cards.filter((c) => c.missable && !owned.value.has(c.id)).length
)
</script>

<template>
  <div class="gw">
    <div class="gw-head">
      <div class="gw-progress-label">
        本体收集进度（「卡牌收藏家」成就口径）
        <strong>{{ baseCount.got }} / {{ baseCount.total }}</strong>
        <span v-if="baseCount.got === baseCount.total" class="gw-done">🎉 已集齐</span>
      </div>
      <div class="gw-bar"><div class="gw-bar-fill" :style="{ width: basePct + '%' }"></div></div>
      <div class="gw-sub">
        <span v-for="s in SETS" :key="s.key">{{ s.label }}：{{ countOf(s.key).got }}/{{ countOf(s.key).total }}</span>
        <span v-if="missableLeft" class="gw-warn">⚠ 还有 {{ missableLeft }} 张易错过卡未收集</span>
        <button class="gw-reset" @click="resetAll">清空勾选</button>
      </div>
    </div>

    <div class="gw-controls">
      <div class="gw-tabs">
        <button
          v-for="s in SETS"
          :key="s.key"
          :class="{ active: setTab === s.key }"
          @click="setTab = s.key"
        >{{ s.label }}</button>
      </div>
      <div class="gw-tabs">
        <button :class="{ active: filterMode === 'all' }" @click="filterMode = 'all'">全部</button>
        <button :class="{ active: filterMode === 'missing' }" @click="filterMode = 'missing'">未收集</button>
        <button :class="{ active: filterMode === 'owned' }" @click="filterMode = 'owned'">已收集</button>
      </div>
      <input class="gw-search" v-model="query" placeholder="搜卡名或地点…" />
    </div>

    <div v-for="g in groups" :key="g.faction" class="gw-group">
      <div class="gw-group-title">{{ g.faction }} <span>{{ g.got }}/{{ g.total }}</span></div>
      <div
        v-for="c in g.items"
        :key="c.id"
        class="gw-row"
        :class="{ owned: owned.has(c.id) }"
        @click="toggle(c.id)"
      >
        <span class="gw-check">{{ owned.has(c.id) ? '✓' : '' }}</span>
        <span class="gw-name">
          {{ c.name }}
          <span v-if="c.missable" class="gw-miss" title="窗口错过就没了">⚠易错过</span>
        </span>
        <span class="gw-how">{{ c.how }}</span>
        <span class="gw-src">{{ c.sources.join(' ／ ') }}</span>
      </div>
    </div>
    <p v-if="!groups.length" class="gw-empty">没有符合条件的卡。</p>
    <p class="gw-note">
      计数口径与游戏内《昆特牌奇迹指南》一致：每种卡有一张即算收集，同名多张不重复计。
      勾选只存在你这台设备的浏览器里，Steam 读不到游戏内卡牌，换设备/清缓存后需要重勾。
    </p>
  </div>
</template>

<style scoped>
.gw { margin: 16px 0; }
.gw-head { border: 1px solid var(--vp-c-divider); border-radius: 10px; padding: 14px 16px; background: var(--vp-c-bg-soft); }
.gw-progress-label { font-size: 14px; display: flex; gap: 8px; align-items: baseline; flex-wrap: wrap; }
.gw-progress-label strong { font-size: 20px; color: #c8a24a; }
.gw-done { color: #7bc47f; font-weight: 600; }
.gw-bar { height: 8px; border-radius: 4px; background: var(--vp-c-divider); margin: 10px 0; overflow: hidden; }
.gw-bar-fill { height: 100%; background: linear-gradient(90deg, #8a6d2f, #c8a24a); transition: width .3s; }
.gw-sub { display: flex; gap: 14px; flex-wrap: wrap; font-size: 12.5px; color: var(--vp-c-text-2); align-items: center; }
.gw-warn { color: #e0a458; }
.gw-reset { margin-left: auto; font-size: 12px; color: var(--vp-c-text-3); background: none; border: 1px solid var(--vp-c-divider); border-radius: 6px; padding: 2px 8px; cursor: pointer; }
.gw-reset:hover { color: #e06c5f; border-color: #e06c5f; }
.gw-controls { display: flex; gap: 10px; flex-wrap: wrap; margin: 14px 0 6px; align-items: center; }
.gw-tabs { display: flex; gap: 4px; }
.gw-tabs button { font-size: 13px; padding: 4px 12px; border-radius: 999px; border: 1px solid var(--vp-c-divider); background: none; color: var(--vp-c-text-2); cursor: pointer; }
.gw-tabs button.active { background: #c8a24a; border-color: #c8a24a; color: #1a1405; font-weight: 600; }
.gw-search { flex: 1; min-width: 140px; font-size: 13px; padding: 5px 12px; border-radius: 999px; border: 1px solid var(--vp-c-divider); background: var(--vp-c-bg-soft); color: var(--vp-c-text-1); }
.gw-group { margin-top: 14px; }
.gw-group-title { font-weight: 700; font-size: 15px; margin-bottom: 6px; }
.gw-group-title span { color: var(--vp-c-text-3); font-size: 12.5px; font-weight: 400; margin-left: 6px; }
.gw-row { display: flex; gap: 10px; align-items: baseline; padding: 6px 10px; border-radius: 8px; cursor: pointer; }
.gw-row:hover { background: var(--vp-c-bg-soft); }
.gw-check { flex: 0 0 18px; width: 18px; height: 18px; border: 1.5px solid var(--vp-c-text-3); border-radius: 5px; text-align: center; line-height: 16px; font-size: 13px; color: #1a1405; align-self: center; }
.gw-row.owned .gw-check { background: #c8a24a; border-color: #c8a24a; }
.gw-name { font-weight: 600; font-size: 14px; white-space: nowrap; }
.gw-row.owned .gw-name { color: var(--vp-c-text-3); }
.gw-miss { color: #e0a458; font-size: 11.5px; font-weight: 600; margin-left: 4px; }
.gw-how { flex: 0 0 auto; font-size: 11.5px; color: var(--vp-c-text-2); border: 1px solid var(--vp-c-divider); padding: 0 7px; border-radius: 999px; white-space: nowrap; }
.gw-src { font-size: 12.5px; color: var(--vp-c-text-2); }
.gw-row.owned .gw-src, .gw-row.owned .gw-how { color: var(--vp-c-text-3); }
.gw-empty { color: var(--vp-c-text-3); font-size: 13px; }
.gw-note { font-size: 12.5px; color: var(--vp-c-text-3); margin-top: 14px; }
@media (max-width: 640px) {
  .gw-row { flex-wrap: wrap; }
  .gw-src { flex-basis: 100%; padding-left: 28px; }
}
</style>
