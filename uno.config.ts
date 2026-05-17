import { defineConfig, presetUno, presetAttributify, presetIcons } from 'unocss'

export default defineConfig({
  presets: [
    presetUno(),
    presetAttributify(),
    presetIcons({
      scale: 1.2,
    }),
  ],
  theme: {
    colors: {
      // 八种属性主题色（火水风雷光暗 + 剑/弓系等），后续可以扩展
      element: {
        fire: '#E74C3C',
        ice: '#3498DB',
        lightning: '#F1C40F',
        wind: '#1ABC9C',
        light: '#F39C12',
        dark: '#8E44AD',
      },
    },
  },
})
