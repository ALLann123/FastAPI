import RecordingItem from './RecordingItem'

export default function RecordingList({ recordings, loading, onDelete }) {
  if (loading) {
    return <p className="message">Loading recordings...</p>
  }

  if (recordings.length === 0) {
    return (
      <p className="message">
        No recordings yet. Press the red button to record your first one.
      </p>
    )
  }

  return (
    <ul className="list">
      {recordings.map((recording) => (
        <RecordingItem key={recording.id} recording={recording} onDelete={onDelete} />
      ))}
    </ul>
  )
}