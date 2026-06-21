import { useCallback, useEffect, useState } from 'react'

// Preset metric types with their default unit.
const METRIC_TYPES = [
  { type: 'steps', unit: 'count' },
  { type: 'weight', unit: 'kg' },
  { type: 'heart_rate', unit: 'bpm' },
  { type: 'sleep_hours', unit: 'hours' },
]

export default function App() {
  const [health, setHealth] = useState(null)
  const [metrics, setMetrics] = useState([])
  const [source, setSource] = useState(null)
  const [form, setForm] = useState({ type: 'steps', value: '', unit: 'count' })
  const [error, setError] = useState(null)
  const [saving, setSaving] = useState(false)

  const loadHealth = useCallback(async () => {
    try {
      const res = await fetch('/api/health')
      const data = await res.json()
      setHealth({ ok: res.ok, ...data })
    } catch (e) {
      setHealth({ ok: false, checks: { error: String(e) } })
    }
  }, [])

  const loadMetrics = useCallback(async () => {
    try {
      const res = await fetch('/api/metrics')
      const data = await res.json()
      setMetrics(data.metrics || [])
      setSource(data.source)
    } catch (e) {
      setError(String(e))
    }
  }, [])

  useEffect(() => {
    loadHealth()
    loadMetrics()
    const id = setInterval(loadHealth, 10000)
    return () => clearInterval(id)
  }, [loadHealth, loadMetrics])

  const onTypeChange = (type) => {
    const preset = METRIC_TYPES.find((m) => m.type === type)
    setForm((f) => ({ ...f, type, unit: preset ? preset.unit : f.unit }))
  }

  const submit = async (e) => {
    e.preventDefault()
    setError(null)
    setSaving(true)
    try {
      const res = await fetch('/api/metrics', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type: form.type,
          value: Number(form.value),
          unit: form.unit,
        }),
      })
      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        throw new Error(err.error || `HTTP ${res.status}`)
      }
      setForm((f) => ({ ...f, value: '' }))
      await loadMetrics()
    } catch (e) {
      setError(e.message)
    } finally {
      setSaving(false)
    }
  }

  const healthy = health?.ok
  const checks = health?.checks || {}

  return (
    <div className="page">
      <header className="header">
        <h1>
          <span className="logo">❤</span> HealthTrack
        </h1>
        <div className={`badge ${healthy ? 'ok' : 'bad'}`}>
          {health ? (healthy ? 'API healthy' : 'API degraded') : 'checking…'}
        </div>
      </header>

      <section className="checks">
        {Object.entries(checks).map(([name, value]) => (
          <span key={name} className={`chip ${value === 'ok' ? 'ok' : 'bad'}`}>
            {name}: {value}
          </span>
        ))}
      </section>

      <main className="grid">
        <section className="card">
          <h2>Log a metric</h2>
          <form onSubmit={submit} className="form">
            <label>
              Type
              <select
                value={form.type}
                onChange={(e) => onTypeChange(e.target.value)}
              >
                {METRIC_TYPES.map((m) => (
                  <option key={m.type} value={m.type}>
                    {m.type}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Value
              <input
                type="number"
                step="any"
                required
                placeholder="e.g. 8421"
                value={form.value}
                onChange={(e) => setForm((f) => ({ ...f, value: e.target.value }))}
              />
            </label>
            <label>
              Unit
              <input
                type="text"
                value={form.unit}
                onChange={(e) => setForm((f) => ({ ...f, unit: e.target.value }))}
              />
            </label>
            <button type="submit" disabled={saving}>
              {saving ? 'Saving…' : 'Add metric'}
            </button>
            {error && <p className="error">{error}</p>}
          </form>
        </section>

        <section className="card">
          <div className="card-head">
            <h2>Recorded metrics</h2>
            <div className="meta">
              {source && <span className="source">source: {source}</span>}
              <button className="ghost" onClick={loadMetrics}>
                Refresh
              </button>
            </div>
          </div>
          {metrics.length === 0 ? (
            <p className="empty">No metrics yet — log one to get started.</p>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>#</th>
                  <th>Type</th>
                  <th>Value</th>
                  <th>Unit</th>
                  <th>Recorded</th>
                </tr>
              </thead>
              <tbody>
                {metrics.map((m) => (
                  <tr key={m.id}>
                    <td>{m.id}</td>
                    <td>{m.type}</td>
                    <td>{m.value}</td>
                    <td>{m.unit}</td>
                    <td>{new Date(m.recorded_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>
      </main>

      <footer className="footer">
        HealthTrack API · Flask + Postgres + Redis · served via nginx
      </footer>
    </div>
  )
}
