import { defineStore } from 'pinia'

export const useThemeStore = defineStore('theme', {
  state: () => ({
    dark: localStorage.getItem('theme') === 'dark'
  }),
  actions: {
    toggle() {
      this.dark = !this.dark
      localStorage.setItem('theme', this.dark ? 'dark' : 'light')
      document.documentElement.setAttribute('data-theme', this.dark ? 'dark' : 'light')
    },
    init() {
      if (this.dark) {
        document.documentElement.setAttribute('data-theme', 'dark')
      }
    }
  }
})