import { useEffect, useState } from 'react'
import { fetchReport, fetchReports, submitDocument } from './api.js'
import ReportsList from './components/ReportsList.jsx'
import ReportView from './components/ReportView.jsx'
import SubmitForm from './components/SubmitForm.jsx'

export default function App() {
  const [reports, setReports] = useState([])
  const [selected, setSelected] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadReports()
  }, [])

  async function loadReports() {
    try {
      setReports(await fetchReports())
    } catch (e) {
      // history failing to load shouldn't block the rest of the app
      console.error(e)
    }
  }

  async function handleSubmit(payload) {
    setLoading(true)
    setError(null)
    try {
      const result = await submitDocument(payload)
      setSelected(result)
      loadReports()
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  async function handleSelect(id) {
    setError(null)
    try {
      setSelected(await fetchReport(id))
    } catch (e) {
      setError(e.message)
    }
  }

 return (
    <div className="app">
      <header>
        <h1>AI Clinical Document Reviewer</h1>
        <p className="subtitle">All data used here is synthetic — for demonstration only.</p>
      </header>

      <main>
        <div className="column">
          <SubmitForm onSubmit={handleSubmit} loading={loading} />
          {error && <div className="error-banner">{error}</div>}

          <h3>Previous reports</h3>
          <ReportsList reports={reports} onSelect={handleSelect} />
        </div>

        <div className="column">
          {selected ? (
            <ReportView report={selected} />
          ) : (
            <p className="muted">Submit or select a report to see it here.</p>
          )}
        </div>
      </main>
    </div>
  )
}
