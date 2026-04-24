<template>
  <div class="import-page">
    <el-tabs v-model="activeTab">
      <!-- Excel 导入 -->
      <el-tab-pane label="Excel 导入" name="excel">
        <el-card>
          <el-form label-width="100px">
            <el-form-item label="选择店铺">
              <el-select v-model="excelForm.store_id" placeholder="选择目标店铺">
                <el-option v-for="s in stores" :key="s.id" :label="s.name" :value="s.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="上传文件">
              <el-upload
                ref="uploadRef"
                :auto-upload="false"
                :limit="1"
                accept=".xlsx,.xls"
                :on-change="handleFileChange"
              >
                <el-button type="primary">选择文件</el-button>
                <template #tip>
                  <div class="el-upload__tip">支持 .xlsx, .xls 格式，最多 100 条数据</div>
                </template>
              </el-upload>
            </el-form-item>
            <el-form-item>
              <el-button type="success" @click="importExcel" :loading="importing">
                开始导入
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <!-- 网页爬取 -->
      <el-tab-pane label="网页爬取" name="scrape">
        <el-card>
          <el-form label-width="100px">
            <el-form-item label="选择店铺">
              <el-select v-model="scrapeForm.store_id" placeholder="选择目标店铺">
                <el-option v-for="s in stores" :key="s.id" :label="s.name" :value="s.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="平台类型">
              <el-radio-group v-model="scrapeForm.platform">
                <el-radio label="auto">自动检测</el-radio>
                <el-radio label="amazon">Amazon</el-radio>
                <el-radio label="aliexpress">AliExpress</el-radio>
                <el-radio label="1688">1688</el-radio>
                <el-radio label="website">独立站</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="产品链接">
              <el-input
                v-model="scrapeForm.urls"
                type="textarea"
                :rows="8"
                placeholder="每行一个产品链接，例如：&#10;https://www.amazon.com/dp/xxx&#10;https://www.aliexpress.com/item/xxx"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="success" @click="startScrape" :loading="scraping">
                开始爬取
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <!-- 导入进度 -->
    <el-card class="progress-card" v-if="importProgress.show">
      <template #header>
        <span>导入进度</span>
      </template>
      <el-progress
        :percentage="importProgress.percentage"
        :status="importProgress.status"
      />
      <div class="progress-info">
        <span>成功: {{ importProgress.success }}</span>
        <span>跳过: {{ importProgress.skip }}</span>
        <span>失败: {{ importProgress.fail }}</span>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { storeApi, importApi } from '@/api'

const activeTab = ref('excel')
const stores = ref<any[]>([])
const importing = ref(false)
const scraping = ref(false)
const selectedFile = ref<File | null>(null)

const excelForm = reactive({
  store_id: null as number | null,
})

const scrapeForm = reactive({
  store_id: null as number | null,
  platform: 'auto',
  urls: '',
})

const importProgress = reactive({
  show: false,
  percentage: 0,
  status: '' as '' | 'success' | 'exception',
  success: 0,
  skip: 0,
  fail: 0,
})

const loadStores = async () => {
  try {
    stores.value = await storeApi.list()
  } catch (e) {
    console.error('加载店铺失败', e)
  }
}

const handleFileChange = (file: any) => {
  selectedFile.value = file.raw
}

const importExcel = async () => {
  if (!excelForm.store_id) {
    ElMessage.warning('请选择目标店铺')
    return
  }
  if (!selectedFile.value) {
    ElMessage.warning('请选择要导入的文件')
    return
  }

  importing.value = true
  importProgress.show = true
  importProgress.percentage = 0
  importProgress.status = ''

  try {
    const result = await importApi.uploadExcel(excelForm.store_id, selectedFile.value)
    ElMessage.success(`导入完成，成功 ${result.success_count} 条`)
    importProgress.percentage = 100
    importProgress.status = 'success'
    importProgress.success = result.success_count
    importProgress.skip = result.skip_count
    importProgress.fail = result.fail_count
  } catch (e: any) {
    ElMessage.error(e.message)
    importProgress.status = 'exception'
  } finally {
    importing.value = false
  }
}

const startScrape = async () => {
  if (!scrapeForm.store_id) {
    ElMessage.warning('请选择目标店铺')
    return
  }
  const urls = scrapeForm.urls.split('\n').filter(u => u.trim())
  if (urls.length === 0) {
    ElMessage.warning('请输入产品链接')
    return
  }

  scraping.value = true
  importProgress.show = true
  importProgress.percentage = 0
  importProgress.status = ''

  try {
    const result = await importApi.scrapeUrls(scrapeForm.store_id, urls)
    ElMessage.success(`爬取完成，成功 ${result.success_count} 条`)
    importProgress.percentage = 100
    importProgress.status = 'success'
    importProgress.success = result.success_count
    importProgress.fail = result.fail_count
  } catch (e: any) {
    ElMessage.error(e.message)
    importProgress.status = 'exception'
  } finally {
    scraping.value = false
  }
}

onMounted(loadStores)
</script>

<style scoped>
.import-page {
  max-width: 900px;
}

.progress-card {
  margin-top: 20px;
}

.progress-info {
  margin-top: 10px;
  display: flex;
  gap: 20px;
  color: #606266;
}
</style>