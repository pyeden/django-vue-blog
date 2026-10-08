<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import CoverUpload from './CoverUpload.vue'
import MarkdownBody from './MarkdownBody.vue'
import TagInput from './TagInput.vue'
import { createArticle, updateArticle, uploadArticleCover } from '../api'
import { apiError } from '../api/client'
import { renderMarkdown } from '../utils/markdown'
import { useMetaStore } from '../stores/meta'
import { useToastStore } from '../stores/toast'

const props = defineProps({
  article: { type: Object, default: null },
})
const emit = defineEmits(['saved'])

const router = useRouter()
const meta = useMetaStore()
const toast = useToastStore()
const textarea = ref(null)
const saving = ref(false)
const coverFile = ref(null)

const form = reactive({
  title: '',
  body: '',
  column: '',
  tags: [],
})

const isEdit = computed(() => Boolean(props.article?.slug))
const previewHtml = computed(() => renderMarkdown(form.body))
const existingCover = computed(() => props.article?.cover || '')

watch(
  () => props.article,
  (value) => {
    if (!value) return
    form.title = value.title || ''
    form.body = value.body || ''
    form.column = value.column?.slug || ''
    form.tags = (value.tags || []).map((tag) => (typeof tag === 'string' ? tag : tag.name))
  },
  { immediate: true }
)

function wrap(before, after = '') {
  const el = textarea.value
  if (!el) return
  const start = el.selectionStart
  const end = el.selectionEnd
  const selected = form.body.slice(start, end)
  form.body = `${form.body.slice(0, start)}${before}${selected}${after}${form.body.slice(end)}`
  requestAnimationFrame(() => {
    el.focus()
    el.selectionStart = start + before.length
    el.selectionEnd = end + before.length
  })
}

function insertBlock(block) {
  const el = textarea.value
  const at = el ? el.selectionStart : form.body.length
  const prefix = form.body && !form.body.endsWith('\n') ? '\n\n' : ''
  form.body = `${form.body.slice(0, at)}${prefix}${block}\n${form.body.slice(at)}`
}

async function save() {
  if (!form.title.trim()) {
    toast.error('标题不能为空')
    return
  }
  if (!form.body.trim()) {
    toast.error('正文不能为空')
    return
  }
  saving.value = true
  try {
    const payload = {
      title: form.title.trim(),
      body: form.body,
      column: form.column || null,
      tags: form.tags,
    }
    const saved = isEdit.value
      ? await updateArticle(props.article.slug, payload)
      : await createArticle(payload)
    if (coverFile.value) {
      await uploadArticleCover(saved.slug, coverFile.value)
    }
    toast.success(isEdit.value ? '文章已更新' : '文章已发布')
    emit('saved', saved)
    router.push({ name: 'article', params: { slug: saved.slug } })
  } catch (error) {
    toast.error(apiError(error, '保存失败'))
  } finally {
    saving.value = false
  }
}

onMounted(() => meta.load())
</script>

<template>
  <div>
    <div class="editor-grid">
      <section class="editor-pane">
        <div class="editor-toolbar">
          <button type="button" @click="wrap('# ', '\n')">H1</button>
          <button type="button" @click="wrap('## ', '\n')">H2</button>
          <button type="button" @click="wrap('**', '**')"><b>B</b></button>
          <button type="button" @click="wrap('*', '*')"><i>I</i></button>
          <button type="button" @click="wrap('[链接文字](', ')')">链接</button>
          <button type="button" @click="insertBlock('```\n代码\n```')">代码块</button>
          <button type="button" @click="insertBlock('> 引用')">引用</button>
          <button type="button" @click="insertBlock('- 列表项\n- 列表项')">列表</button>
        </div>
        <div class="editor-pane-inner">
          <div>
            <label class="form-label">标题</label>
            <input v-model="form.title" class="form-control" maxlength="200" placeholder="给文章起一个标题" />
          </div>

          <div class="row g-2">
            <div class="col-sm-6">
              <label class="form-label">栏目</label>
              <select v-model="form.column" class="form-select form-select-sm">
                <option value="">未分类</option>
                <option v-for="column in meta.columns" :key="column.slug" :value="column.slug">
                  {{ column.title }}
                </option>
              </select>
            </div>
            <div class="col-sm-6">
              <label class="form-label">封面</label>
              <CoverUpload v-model="coverFile" :existing="existingCover" />
            </div>
          </div>

          <div>
            <label class="form-label">标签</label>
            <TagInput v-model="form.tags" />
          </div>

          <div>
            <label class="form-label">正文（Markdown）</label>
            <textarea
              ref="textarea"
              v-model="form.body"
              class="editor-textarea"
              placeholder="# 从这里开始写&#10;&#10;支持 Markdown：标题、列表、代码块、表格、引用。"
            ></textarea>
          </div>
        </div>
      </section>

      <section class="preview-pane">
        <div class="preview-head">实时预览</div>
        <div class="preview-body">
          <h1 v-if="form.title" class="article-title" style="font-size:1.7rem">{{ form.title }}</h1>
          <MarkdownBody v-if="form.body" :html="previewHtml" />
          <div v-else class="about-mini">左侧开始输入，这里会实时渲染。</div>
        </div>
      </section>
    </div>

    <div class="d-flex justify-content-end gap-2 mt-3">
      <button class="btn btn-ghost" type="button" @click="router.back()">取消</button>
      <button class="btn btn-accent" type="button" :disabled="saving" @click="save">
        {{ saving ? '保存中…' : isEdit ? '保存修改' : '发布文章' }}
      </button>
    </div>
  </div>
</template>
