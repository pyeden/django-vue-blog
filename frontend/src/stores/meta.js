import { defineStore } from 'pinia'
import { fetchColumns, fetchTags } from '../api'

function normaliseTag(tag) {
  if (!tag) return null
  if (typeof tag === 'string') return { name: tag, slug: tag, count: null }
  return {
    ...tag,
    name: tag.name ?? tag.title ?? tag.tag ?? '',
    slug: tag.slug ?? tag.name ?? tag.title ?? '',
  }
}

export const useMetaStore = defineStore('meta', {
  state: () => ({
    columns: [],
    tags: [],
    loaded: false,
    loading: false,
  }),
  actions: {
    async load(force = false) {
      if (this.loaded && !force) return
      if (this.loading) return
      this.loading = true
      const [columnsResult, tagsResult] = await Promise.allSettled([
        fetchColumns(),
        fetchTags(),
      ])
      if (columnsResult.status === 'fulfilled') {
        this.columns = columnsResult.value
      }
      if (tagsResult.status === 'fulfilled') {
        this.tags = tagsResult.value.map(normaliseTag).filter(Boolean)
      }
      this.loaded = true
      this.loading = false
    },
    columnBySlug(slug) {
      return this.columns.find((column) => column.slug === slug) || null
    },
    tagBySlug(slug) {
      return this.tags.find((tag) => tag.slug === slug || tag.name === slug) || null
    },
  },
})
