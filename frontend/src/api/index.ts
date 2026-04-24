import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 响应拦截器
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message = error.response?.data?.detail || error.message || '请求失败'
    return Promise.reject(new Error(message))
  }
)

// 店铺 API
export const storeApi = {
  list: () => api.get('/stores/'),
  get: (id: number) => api.get(`/stores/${id}`),
  create: (data: any) => api.post('/stores/', data),
  update: (id: number, data: any) => api.put(`/stores/${id}`, data),
  delete: (id: number) => api.delete(`/stores/${id}`),
  testConnection: (id: number) => api.post(`/stores/${id}/test`),
}

// 产品 API
export const productApi = {
  list: (params?: any) => api.get('/products/', { params }),
  get: (id: number) => api.get(`/products/${id}`),
  create: (data: any) => api.post('/products/', data),
  delete: (id: number) => api.delete(`/products/${id}`),
  getBySku: (sku: string, storeId: number) => 
    api.get(`/products/sku/${sku}`, { params: { store_id: storeId } }),
}

// 导入 API
export const importApi = {
  uploadExcel: (storeId: number, file: File, mapping?: any) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('store_id', storeId.toString())
    if (mapping) {
      formData.append('column_mapping', JSON.stringify(mapping))
    }
    return api.post('/imports/excel', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  scrapeUrls: (storeId: number, urls: string[]) => 
    api.post('/imports/scrape', { store_id: storeId, urls }),
  getStatus: (batchId: string) => api.get(`/imports/status/${batchId}`),
  listHistory: (params?: any) => api.get('/imports/history', { params }),
}

// 优化 API
export const optimizeApi = {
  optimize: (productId: number, options?: any) => 
    api.post(`/optimize/${productId}`, options),
  batchOptimize: (productIds: number[], options?: any) => 
    api.post('/optimize/batch', { product_ids: productIds, options }),
  preview: (productId: number) => api.get(`/optimize/${productId}/preview`),
}

export default api
