const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export async function submitDocument({ text, file }) {
  const formData = new FormData()
  if (text) formData.append('text', text)
  if (file) formData.append('file', file)

  const res = await fetch(`${API_URL}/api/analyze`, {
    method: 'POST',
    body: formData,
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail || `Request failed (${res.status})`)
  }
  return res.json()
}

export async function fetchReports() {
  const res = await fetch(`${API_URL}/api/reports`)
  if (!res.ok) throw new Error('Could not load previous reports.')
  return res.json()
}

export async function fetchReport(id) {
  const res = await fetch(`${API_URL}/api/reports/${id}`)
  if (!res.ok) throw new Error('Could not load this report.')
  return res.json()
}
