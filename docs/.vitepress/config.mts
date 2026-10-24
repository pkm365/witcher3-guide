import { defineConfig } from 'vitepress'

export default defineConfig({
  title: '巫师三 · 全成就开荒',
  description: '杰洛特的全成就、毕业装备与最佳体验路线',
  base: '/witcher3-guide/',
  appearance: 'dark',
  themeConfig: {
    nav: [
      { text: '总览', link: '/' },
      { text: '最佳路线', link: '/roadmap' },
      { text: '全成就', link: '/achievements' },
      { text: '毕业装备', link: '/gear' },
      { text: '昆特牌', link: '/gwent' },
    ],
    sidebar: [
      {
        text: '开荒',
        items: [
          { text: '总览与策略', link: '/' },
          { text: '最佳体验路线', link: '/roadmap' },
        ],
      },
      {
        text: '目标',
        items: [
          { text: '全成就清单（78）', link: '/achievements' },
          { text: '毕业装备路线', link: '/gear' },
          { text: '昆特牌全收集', link: '/gwent' },
        ],
      },
    ],
    outline: { label: '本页目录' },
    docFooter: { prev: '上一页', next: '下一页' },
    darkModeSwitchLabel: '外观',
    sidebarMenuLabel: '菜单',
    returnToTopLabel: '回到顶部',
    search: { provider: 'local' },
  },
})
