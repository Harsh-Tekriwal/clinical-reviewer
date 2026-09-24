export default function ReportsList({ reports, onSelect }) {
  if (reports.length === 0) {
    return <p className="muted">No reports yet — submit a document to get started.</p>
  }

  return (
    <ul className="reports-list">
      {reports.map((r) => (
        <li key={r.id} onClick={() => onSelect(r.id)}>
          <span className={`status-dot status-${r.status}`} />
          <div>
            <div className="reports-list-title">
              {r.report_summary ? truncate(r.report_summary, 80) : `${r.input_type} — ${r.status}`}
            </div>
            <div className="reports-list-meta">
              {new Date(r.created_at).toLocaleString()} · {r.input_type}
            </div>
          </div>
        </li>
      ))}
    </ul>
  )
}

function truncate(str, n) {
  return str.length > n ? str.slice(0, n) + '…' : str
}
