import { marked } from 'marked'
import DOMPurify from 'dompurify'

marked.setOptions({
  gfm: true,
  breaks: false,
})

const PURIFY_OPTIONS = {
  ADD_ATTR: ['target', 'rel', 'id', 'loading'],
  FORBID_TAGS: ['style', 'form', 'input', 'button'],
}

export function sanitizeHtml(html) {
  return DOMPurify.sanitize(html || '', PURIFY_OPTIONS)
}

export function renderMarkdown(source) {
  if (!source) return ''
  const html = marked.parse(String(source))
  return sanitizeHtml(html)
}

export function slugifyHeading(text) {
  return String(text || '')
    .trim()
    .toLowerCase()
    .replace(/[\s]+/g, '-')
    .replace(/[^\w\u3400-\u9fff-]/g, '')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '')
}
