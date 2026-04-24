<template>
  <div class="stores-page">
    <!-- 操作栏 -->
    <div class="toolbar">
      <el-button type="primary" @click="showDialog = true">
        <el-icon><Plus /></el-icon>
        添加店铺
      </el-button>
    </div>

    <!-- 店铺列表 -->
    <el-table :data="stores" stripe v-loading="loading">
      <el-table-column prop="name" label="店铺名称" width="200" />
      <el-table-column prop="shop_url" label="店铺地址" />
      <el-table-column prop="is_active" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'">
            {{ row.is_active ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button size="small" @click="testConnection(row)">测试连接</el-button>
          <el-button size="small" type="primary" @click="editStore(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="deleteStore(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="showDialog"
      :title="editingStore ? '编辑店铺' : '添加店铺'"
      width="500px"
    >
      <el-form :model="form" label-width="100px">
        <el-form-item label="店铺名称" required>
          <el-input v-model="form.name" placeholder="请输入店铺名称" />
        </el-form-item>
        <el-form-item label="店铺地址" required>
          <el-input v-model="form.shop_url" placeholder="例如: your-store.myshopify.com" />
        </el-form-item>
        <el-form-item label="Access Token" required>
          <el-input
            v-model="form.access_token"
            type="password"
            placeholder="Shopify Admin API Access Token"
            show-password
          />
        </el-form-item>
        <el-form-item label="启用状态">
          <el-switch v-model="form.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="saveStore" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { storeApi } from '@/api'

interface Store {
  id: number
  name: string
  shop_url: string
  is_active: boolean
  created_at: string
}

const stores = ref<Store[]>([])
const loading = ref(false)
const showDialog = ref(false)
const saving = ref(false)
const editingStore = ref<Store | null>(null)

const form = ref({
  name: '',
  shop_url: '',
  access_token: '',
  is_active: true,
})

const formatDate = (date: string) => {
  return new Date(date).toLocaleString('zh-CN')
}

const loadStores = async () => {
  loading.value = true
  try {
    stores.value = await storeApi.list()
  } catch (e: any) {
    ElMessage.error(e.message)
  } finally {
    loading.value = false
  }
}

const editStore = (store: Store) => {
  editingStore.value = store
  form.value = {
    name: store.name,
    shop_url: store.shop_url,
    access_token: '',
    is_active: store.is_active,
  }
  showDialog.value = true
}

const saveStore = async () => {
  if (!form.value.name || !form.value.shop_url) {
    ElMessage.warning('请填写完整信息')
    return
  }

  saving.value = true
  try {
    if (editingStore.value) {
      await storeApi.update(editingStore.value.id, form.value)
      ElMessage.success('更新成功')
    } else {
      if (!form.value.access_token) {
        ElMessage.warning('请输入 Access Token')
        saving.value = false
        return
      }
      await storeApi.create(form.value)
      ElMessage.success('添加成功')
    }
    showDialog.value = false
    loadStores()
  } catch (e: any) {
    ElMessage.error(e.message)
  } finally {
    saving.value = false
  }
}

const deleteStore = async (store: Store) => {
  try {
    await ElMessageBox.confirm('确定要删除该店铺吗？', '提示', {
      type: 'warning',
    })
    await storeApi.delete(store.id)
    ElMessage.success('删除成功')
    loadStores()
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error(e.message)
    }
  }
}

const testConnection = async (store: Store) => {
  try {
    await storeApi.testConnection(store.id)
    ElMessage.success('连接成功')
  } catch (e: any) {
    ElMessage.error('连接失败: ' + e.message)
  }
}

onMounted(loadStores)
</script>

<style scoped>
.toolbar {
  margin-bottom: 20px;
}
</style>
