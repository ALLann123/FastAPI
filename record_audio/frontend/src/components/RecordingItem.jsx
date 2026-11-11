import { audioUrl, downloadUrl } from '../api'
import { formatDate, formatSize } from '../format'

export default function RecordingItem({ recording, onDelete }) {
  // "20261007-143015-a1b2c3.webm" -> "WEBM"
  const type = recording.filename.split('.').pop().toUpperCase()

  function handleDelete() {
    if (window.confirm('Delete this recording? This cannot be undone.')) {
      onDelete(recording.id)
    }
  }

  return (
    <li className="item">
      <div className="item-top">
        <div>
          <div className="item-date">{formatDate(recording.created_at)}</div>
          <div className="item-meta">
            {type}, {formatSize(recording.size_bytes)}
          </div>
        </div>

        <div className="item-actions">
          <a className="button small" href={downloadUrl(recording.id)}>
            Download
          </a>
          <button className="button small danger" onClick={handleDelete}>
            Delete
          </button>
        </div>
      </div>

      {/* preload="none": don't download the audio until Play is pressed */}
      <audio controls preload="none" src={audioUrl(recording.id)} />
    </li>
  )
}