import { useState } from 'react'

export default function SubmitForm({ onSubmit, loading }) {
  const [text, setText] = useState('')
  const [file, setFile] = useState(null)

  function handleTextChange(e) {
    setText(e.target.value)
    if (e.target.value) setFile(null) // keep text/file mutually exclusive
  }

  function handleFileChange(e) {
    const f = e.target.files[0]
    setFile(f || null)
    if (f) setText('')
  }

  function handleSubmit(e) {
    e.preventDefault()
    if (!text.trim() && !file) return
    onSubmit({ text: text.trim() || undefined, file: file || undefined })
  }

  return (
    <form className="submit-form" onSubmit={handleSubmit}>
      <label className="field-label">Clinical notes (text)</label>
      <textarea
        rows={8}
        placeholder="Paste or type clinical notes here..."
        value={text}
        onChange={handleTextChange}
        disabled={loading || !!file}
      />

      <div className="or-divider">OR</div>

      <label className="field-label">Upload an image or PDF</label>
      <input
        type="file"
        accept="image/jpeg,image/png,image/webp,application/pdf"
        onChange={handleFileChange}
        disabled={loading}
      />
      {file && <p className="file-name">Selected: {file.name}</p>}

      <button type="submit" disabled={loading || (!text.trim() && !file)}>
        {loading ? 'Processing…' : 'Submit for review'}
      </button>
    </form>
  )
}
