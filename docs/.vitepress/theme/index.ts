import DefaultTheme from 'vitepress/theme'
import type { Theme } from 'vitepress'
import WitcherBanner from './components/WitcherBanner.vue'
import AchGallery from './components/AchGallery.vue'
import './style.css'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('WitcherBanner', WitcherBanner)
    app.component('AchGallery', AchGallery)
  },
} satisfies Theme
