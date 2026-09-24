export default function ReportView({ report }) {
  if (!report) return null

  if (report.status === 'pending') {
    return <div className="report-view status-pending">Still processing…</div>
  }

  if (report.status === 'failed') {
    return (
      <div className="report-view status-failed">
        <h3>Processing failed</h3>
        <p>{report.error_message || 'Something went wrong while analyzing this document.'}</p>
      </div>
    )
  }

  const r = report.full_report
  if (!r) return null

  return (
    <div className="report-view">
      <section className="report-summary">
        <h3>Report Summary</h3>
        <p>{r.report_summary}</p>
      </section>

      <section>
        <h4>Patient Information</h4>
        <KeyValueList data={r.patient_information} />
      </section>

      <ListSection title="Symptoms" items={r.symptoms} />
      <ListSection title="Diagnoses" items={r.diagnoses} />
      <ListSection title="Medications" items={r.medications} />

      <section>
        <h4>Vitals</h4>
        <KeyValueList data={r.vitals} />
      </section>

      <ListSection title="Allergies" items={r.allergies} />
      <ListSection title="Clinical Observations" items={r.clinical_observations} />
      <ListSection title="Clinical Concerns" items={r.clinical_concerns} warn />
      <ListSection title="Missing Information" items={r.missing_information} warn />
      <ListSection title="Potential Inconsistencies" items={r.potential_inconsistencies} warn />
      <ListSection title="Requires Review" items={r.requires_review} warn />
    </div>
  )
}

function ListSection({ title, items, warn }) {
  if (!items || items.length === 0) return null
  return (
    <section className={warn ? 'warn-section' : ''}>
      <h4>{title}</h4>
      <ul>
        {items.map((item, i) => (
          <li key={i}>{item}</li>
        ))}
      </ul>
    </section>
  )
}

function KeyValueList({ data }) {
  if (!data) return null
  const entries = Object.entries(data).filter(([, v]) => v)
  if (entries.length === 0) return <p className="muted">Not stated in the document.</p>
  return (
    <dl className="kv-list">
      {entries.map(([k, v]) => (
        <div key={k} className="kv-row">
          <dt>{k.replaceAll('_', ' ')}</dt>
          <dd>{v}</dd>
        </div>
      ))}
    </dl>
  )
}
