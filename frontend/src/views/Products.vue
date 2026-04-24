<template>
  <div class="products-page">
    <!-- 搜索栏 -->
    <div class="toolbar">
      <el-select v-model="filters.store_id" placeholder="选择店铺" clearable style="width: 200px;">
        <el-option v-for="s in stores" :key="s.id" :label="s.name" :value="s.id" />
      </el-select>
      <el-select v-model="filters.status" placeholder="选择状态" clearable style="width: 150px;">
        <el-option label="待处理" value="pending" />
        <el-option label="已优化" value="optimized" />
        <el-option label="已上传" value="uploaded" />
        <el-option label="已发布" value="published" />
      </el-select>
      <el-input
        v-model="filters.search"
        placeholder="搜索产品"
        clearable
        style="width: 300px;"
        @keyup.enter="loadProducts"
      />
      <el-button type="primary" @click="loadProducts">搜索</el-button>
    </div>

    <!-- 产品列表 -->
    <el-table :data="products" stripe v-loading="loading" @selection-change="onSelectionChange">
      <el-table-column type="selection" width="50" />
      <el-table-column prop="sku" label="SKU" width="150" />
      <el-table-column prop="original_title" label="标题" min-width="300">
        <template #default="{ row }">
          <div class="product-title">
            <div class="original">{{ row.original_title }}</div>
            <div v-if="row.optimized_title" class="optimized">
              <el-tag size="small" type="success">已优化</el-tag>
              {{ row.optimized_title }}
            </div>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="original_price" label="价格" width="100">
        <template #default="{ row }">
          {{ row.original_price ? `$${row.original_price}` : '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="source_type" label="来源" width="100">
        <template #default="{ row }">
          <el-tag size="small">{{ row.source_type }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="160">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="viewProduct(row)">查看</el-button>
          <el-button size="small" type="danger" @click="deleteProduct(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        @change="loadProducts"
      />
    </div>

    <!-- 批量操作 -->
    <div class="batch-actions" v-if="selectedProducts.length > 0">
      <span>已选择 {{ selectedProducts.length }} 个产品</span>
      <el-button type="success" @click="batchOptimize">批量优化</el-button>
      <el-button type="warning" @click="batchUpload">批量上传</el-button>
    </div>

    <!-- 产品详情对话框 -->
    <el-dialog v-model="showDetail" title="产品详情" width="700px">
      <el-descriptions :column="2" border v-if="currentProduct">
        <el-descriptions-item label="SKU">{{ currentProduct.sku }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentProduct.status)">
            {{ getStatusText(currentProduct.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="原始标题" :span="2">
          {{ currentProduct.original_title }}
        </el-descriptions-item>
        <el-descriptions-item label="优化标题" :span="2" v-if="currentProduct.optimized_title">
          {{ currentProduct.optimized_title }}
        </el-descriptions-item>
        <el-descriptions-item label="原始价格">{{ currentProduct.original_price }}</el-descriptions-item>
        <el-descriptions-item label="来源">{{ currentProduct.source_type }}</el-descriptions-item>
        <el-descriptions-item label="原始描述" :span="2">
          <div class="description">{{ currentProduct.original_description || '-' }}</div>
        </el-descriptions-item>
        <el-descriptions-item label="优化描述" :span="2" v-if="currentProduct.optimized_description">
          <div class="description">{{ currentProduct.optimized_description }}</div>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import { productApi, storeApi } from '@/api'

const router = useRouter()

const stores = ref<any[]>([])
const products = ref<any[]>([])
const loading = ref(false)
const selectedProducts = ref<any[]>([])
const showDetail = ref(false)
const currentProduct = ref<any>(null)

const filters = reactive({
  store_id: null as number | null,
  status: '',
  search: '',
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
})

const getStatusType = (status: string) => {
  const types: Record<string, string> = {
    pending: 'info',
    optimized: 'success',
    uploaded: 'warning',
    published: 'primary',
  }
  return types[status] || 'info'
}

const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    pending: '待处理',
    optimized: '已优化',
    uploaded: '已上传',
    published: '已发布',
  }
  return texts[status] || status
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleString('zh-CN')
}

const loadStores = async () => {
  try {
    stores.value = await storeApi.list()
  } catch (e) {
    console.error('加载店铺失败', e)
  }
}

const loadProducts = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ...filters,
    }
    const result = await productApi.list(params)
    products.value = result.items
    pagination.total = result.total
  } catch (e: any) {
    ElMessage.error(e.message)
  } finally {
    loading.value = false
  }
}

const onSelectionChange = (selection: any[]) => {
  selectedProducts.value = selection
}

const viewProduct = (product: any) => {
  currentProduct.value = product
  showDetail.value = true
}

const deleteProduct = async (product: any) => {
  try {
    await ElMessageBox.confirm('确定要删除该产品吗？', '提示', { type: 'warning' })
    await productApi.delete(product.id)
    ElMessage.success('删除成功')
    loadProducts()
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error(e.message)
  }
}

const batchOptimize = () => {
  router.push({
    path: '/optimize',
    query: { ids: selectedProducts.value.map(p => p.id).join(',') },
  })
}

const batchUpload = () => {
  ElMessage.info('批量上传功能开发中')
}

onMounted(() => {
  loadStores()
  loadProducts()
})
</script>

<style scoped>
.toolbar {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.product-title .original {
  color: #303133;
}

.product-title .optimized {
  color: #67C23A;
  margin-top: 4px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.batch-actions {
  margin-top: 20px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.description {
  max-height: 200px;
  overflow-y: auto;
  white-space: pre-wrap;
}
</style>