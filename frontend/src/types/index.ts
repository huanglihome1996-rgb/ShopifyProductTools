// 店铺相关类型
export interface Store {
  id: number
  name: string
  shop_url: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface StoreCreate {
  name: string
  shop_url: string
  access_token: string
  is_active?: boolean
}

// 产品相关类型
export interface Product {
  id: number
  store_id: number
  sku: string
  shopify_id?: string
  original_title: string
  original_description?: string
  original_price?: number
  original_images?: string
  optimized_title?: string
  optimized_description?: string
  meta_title?: string
  meta_description?: string
  url_handle?: string
  status: 'pending' | 'optimized' | 'uploaded' | 'published'
  is_draft: boolean
  source_type: string
  source_url?: string
  tags?: string
  category?: string
  created_at: string
  updated_at: string
}

export interface Variant {
  id: number
  product_id: number
  sku: string
  title: string
  option1?: string
  option2?: string
  option3?: string
  price: number
  compare_at_price?: number
  quantity: number
  image_url?: string
}

// 导入历史
export interface ImportHistory {
  id: number
  batch_id: string
  source_type: string
  source_name: string
  total_count: number
  success_count: number
  skip_count: number
  fail_count: number
  status: 'processing' | 'completed' | 'failed'
  error_log?: string
  started_at: string
  finished_at?: string
}

// API 响应类型
export interface PaginatedResponse<T> {
  total: number
  page: number
  page_size: number
  items: T[]
}

export interface MessageResponse {
  success: boolean
  message: string
}
