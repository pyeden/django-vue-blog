const ABSOLUTE = /^(?:https?:)?\/\//i

export function mediaUrl(path) {
  if (!path) return ''
  if (/^(data|blob):/i.test(path)) return path
  if (ABSOLUTE.test(path)) {
    // Protocol-relative URLs are uncommon here; normalise for <img src>.
    return path.startsWith('//') ? `https:${path}` : path
  }
  const base = (import.meta.env.VITE_MEDIA_BASE || '').replace(/\/+$/, '')
  if (base) {
    return `${base}/${String(path).replace(/^\/+/, '')}`
  }
  return path
}

function toDate(value) {
  if (!value) return null
  const date = value instanceof Date ? value : new Date(value)
  return Number.isNaN(date.getTime()) ? null : date
}

export function formatDate(value) {
  const date = toDate(value)
  if (!date) return ''
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(date)
}

export function formatShortDate(value) {
  const date = toDate(value)
  if (!date) return ''
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  })
    .format(date)
    .replace(/\//g, '.')
}

export function formatDateTime(value) {
  const date = toDate(value)
  if (!date) return ''
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
}

export function fromNow(value) {
  const date = toDate(value)
  if (!date) return ''
  const diff = Math.round((date.getTime() - Date.now()) / 1000)
  const abs = Math.abs(diff)
  const units = [
    [60, 'second'],
    [60, 'minute'],
    [24, 'hour'],
    [7, 'day'],
    [4.345, 'week'],
    [12, 'month'],
    [Number.POSITIVE_INFINITY, 'year'],
  ]
  let amount = diff
  let unit = 'second'
  for (const [step, label] of units) {
    if (Math.abs(amount) < step) {
      unit = label
      break
    }
    amount = amount / step
  }
  const rounded = Math.round(amount)
  if (Math.abs(rounded) < 1) return '刚刚'
  const formatter = new Intl.RelativeTimeFormat('zh-CN', { numeric: 'auto' })
  return formatter.format(rounded, unit)
}

export function initials(name) {
  const text = String(name || '?').trim()
  if (!text) return '?'
  // For CJK names the last character usually reads better as an avatar mark.
  if (/[\u3400-\u9fff]/.test(text)) return text.slice(-1)
  return text.slice(0, 1).toUpperCase()
}

export function avatarTone(name) {
  const text = String(name || '')
  let hash = 0
  for (let i = 0; i < text.length; i += 1) {
    hash = (hash * 31 + text.charCodeAt(i)) % 360
  }
  return hash
}

export function plainText(value, limit = 0) {
  const text = String(value || '')
    .replace(/<[^>]*>/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
  if (limit > 0 && text.length > limit) return `${text.slice(0, limit)}…`
  return text
}

export function pluralCount(count, unit = '篇') {
  return `${Number(count) || 0} ${unit}`
}
