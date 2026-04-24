/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

declare module '@/api' {
  export const storeApi: any
  export const productApi: any
  export const importApi: any
  export const optimizeApi: any
}
