import { useEffect, useState } from 'react'
import { deleteRecording, listRecordings } from './api'
import Recorder from './components/Recorder'
import RecordingList from './components/RecordingList'

export default function App() {
  const [recordings, setRecordings] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // Run once when the page loads: fetch the saved recordings
  useEffect(() => {
    listRecordings()
      .then(setRecordings)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  // Called by <Recorder> after a successful upload.
  // Put the new one at the top instead of re-fetching the whole list.
  function handleSaved(recording) {
    setRecordings((previous) => [recording, ...previous])
  }

  async function handleDelete(id) {
    try {
      await deleteRecording(id)
      setRecordings((previous) => previous.filter((r) => r.id !== id))
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="page">
      <header className="header">
        <h1>Voice Notes</h1>
        <p>Record in your browser. Recordings are saved on your own server.</p>
      </header>

      <Recorder onSaved={handleSaved} />

      <section className="library" aria-label="Saved recordings">
        <h2>
          Saved recordings
          {recordings.length > 0 && <span className="count">{recordings.length}</span>}
        </h2>

        {error && (
          <p className="message error" role="alert">
            {error}
          </p>
        )}

        <RecordingList recordings={recordings} loading={loading} onDelete={handleDelete} />
      </section>
    </div>
  )
}