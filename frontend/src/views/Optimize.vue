<template>
  <div class="optimize-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>AI 优化设置</span>
        </div>
      </template>

      <el-form label-width="120px">
        <el-form-item label="优化选项">
          <el-checkbox v-model="options.title">标题优化</el-checkbox>
          <el-checkbox v-model="options.description">描述生成</el-checkbox>
          <el-checkbox v-model="options.seo">SEO 优化</el-checkbox>
          <el-checkbox v-model="options.images">图片处理</el-checkbox>
        </el-form-item>
        <el-form-item label="AI 模型">
          <el-select v-model="options.model" style="width: 200px;">
            <el-option label="GPT-4 Turbo" value="gpt-4-turbo-preview" />
            <el-option label="GPT-3.5 Turbo" value="gpt-3.5-turbo" />
          </el-select>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 待优化产品 -->
    <el-card class="products-card">
      <template #header>
        <div class="card-header">
          <span>待优化产品</span>
          <el-button type="primary" @click="batchOptimize" :loading="optimizing">
            批量优化
          </el-button>
        </div>
      </template>

      <el-table :data="products" v-loading="loading" @selection-change="onSelectionChange">
        <el-table-column type="selection" width="50" />
        <el-table-column prop="sku" label="SKU" width="150" />
        <el-table-column prop="original_title" label="原始标题" />
        <el-table-column label="优化预览" width="300">
          <template #default="{ row }">
            <div v-if="row.preview" class="preview">
              <div class="preview-title">{{ row.preview.title }}</div>
              <el-tag size="small" type="success">已预览</el-tag>
            </div>
            <el-button v-else size="small" @click="previewOptimize(row)">预览</el-button>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'optimized' ? 'success' : 'info'">
              {{ row.status === 'optimized' ? '已优化' : '待处理' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 预览对话框 -->
    <el-dialog v-model="showPreview" title="优化预览" width="700px">
      <div v-if="currentPreview" class="preview-content">
        <el-divider>标题对比</el-divider>
        <div class="compare">
          <div class="original">
            <h4>原始标题</h4>
            <p>{{ currentPreview.original_title }}</p>
          </div>
          <div class="optimized">
            <h4>优化标题</h4>
            <p>{{ currentPreview.title }}</p>
          </div>
        </div>

        <el-divider>SEO 信息</el-divider>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="Meta Title">
            {{ currentPreview.meta_title }}
          </el-descriptions-item>
          <el-descriptions-item label="Meta Description">
            {{ currentPreview.meta_description }}
          </el-descriptions-item>
          <el-descriptions-item label="URL Handle">
            {{ currentPreview.url_handle }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoute } from 'vue-router'
import { productApi, optimizeApi } from '@/api'

const route = useRoute()
const products = ref<any[]>([])
const loading = ref(false)
const optimizing = ref(false)
const selectedProducts = ref<any[]>([])
const showPreview = ref(false)
const currentPreview = ref<any>(null)

const options = reactive({
  title: true,
  description: true,
  seo: true,
  images: false,
  model: 'gpt-4-turbo-preview',
})

const loadProducts = async () => {
  loading.value = true
  try {
    const result = await productApi.list({ status: 'pending', page_size: 50 })
    products.value = result.items
  } catch (e: any) {
    ElMessage.error(e.message)
  } finally {
    loading.value = false
  }
}

const onSelectionChange = (selection: any[]) => {
  selectedProducts.value = selection
}

const previewOptimize = async (product: any) => {
  try {
    const preview = await optimizeApi.preview(product.id)
    product.preview = preview
    currentPreview.value = { ...product, ...preview }
    showPreview.value = true
  } catch (e: any) {
    ElMessage.error(e.message)
  }
}

const batchOptimize = async () => {
  if (selectedProducts.value.length === 0) {
    ElMessage.warning('请选择要优化的产品')
    return
  }

  optimizing.value = true
  try {
    const ids = selectedProducts.value.map(p => p.id)
    await optimizeApi.batchOptimize(ids, options)
    ElMessage.success(`成功优化 ${ids.length} 个产品`)
    loadProducts()
  } catch (e: any) {
    ElMessage.error(e.message)
  } finally {
    optimizing.value = false
  }
}

onMounted(() => {
  // 支持从产品页面跳转过来
  const ids = route.query.ids as string
  if (ids) {
    // 预选中指定产品
  }
  loadProducts()
})
</script>

<style scoped>
.optimize-page {
  max-width: 1200px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.products-card {
  margin-top: 20px;
}

.preview {
  display: flex;
  align-items: center;
  gap: 10px;
}

.preview-title {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.preview-content {
  padding: 0 20px;
}

.compare {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.compare h4 {
  margin-bottom: 8px;
  color: #909399;
}

.compare p {
  color: #303133;
  line-height: 1.6;
}

.optimized p {
  color: #67C23A;
}
</style>