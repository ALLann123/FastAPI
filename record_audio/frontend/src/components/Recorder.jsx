import { useEffect, useRef, useState } from 'react'
import { uploadRecording } from '../api'
import { formatTime } from '../format'

// Browsers can record different audio formats. We try these in order
// and use the first one this browser supports.
const MIME_TYPES = [
  'audio/webm;codecs=opus', // Chrome, Edge, Firefox
  'audio/webm',
  'audio/ogg;codecs=opus',
  'audio/mp4', // Safari
]

function pickMimeType() {
  if (typeof MediaRecorder === 'undefined') return ''
  return MIME_TYPES.find((type) => MediaRecorder.isTypeSupported(type)) || ''
}

// Turn the browser's technical error into something a person can act on
function describeMicError(error) {
  if (error.name === 'NotAllowedError') {
    return 'Microphone access was blocked. Allow it in your browser\u2019s address bar, then try again.'
  }
  if (error.name === 'NotFoundError') {
    return 'No microphone found. Plug one in and try again.'
  }
  return `Could not start recording: ${error.message}`
}

export default function Recorder({ onSaved }) {
  // status moves through:  idle -> recording -> review -> saving -> idle
  const [status, setStatus] = useState('idle')
  const [seconds, setSeconds] = useState(0)
  const [preview, setPreview] = useState(null) // { blob, url } after you stop
  const [error, setError] = useState('')

  // Refs hold things that must survive re-renders but should NOT trigger one
  const recorderRef = useRef(null) // the MediaRecorder
  const streamRef = useRef(null) // the live microphone stream
  const chunksRef = useRef([]) // pieces of audio collected so far
  const timerRef = useRef(null) // the setInterval id for the timer

  // When the component leaves the screen: stop the timer and the microphone
  useEffect(() => {
    return () => {
      clearInterval(timerRef.current)
      streamRef.current?.getTracks().forEach((track) => track.stop())
    }
  }, [])

  // Whenever the preview changes (or we leave), free the memory it used
  useEffect(() => {
    if (!preview) return
    return () => URL.revokeObjectURL(preview.url)
  }, [preview])

  async function startRecording() {
    setError('')

    // Browsers only offer the microphone on https:// pages or on localhost
    if (!navigator.mediaDevices?.getUserMedia) {
      setError(
        'This page cannot use the microphone. Open it at http://localhost:5173 (or use https).',
      )
      return
    }

    try {
      // 1. Ask for the microphone. The browser shows a permission popup.
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      streamRef.current = stream

      // 2. Create a recorder that listens to the stream
      const mimeType = pickMimeType()
      const recorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined)
      chunksRef.current = []

      // 3. While recording, the browser hands us audio in small pieces
      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) chunksRef.current.push(event.data)
      }

      // 4. When we stop, glue the pieces into one Blob (a file-like object)
      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: recorder.mimeType })
        setPreview({ blob, url: URL.createObjectURL(blob) })
        // Release the microphone so the browser's "recording" light goes off
        stream.getTracks().forEach((track) => track.stop())
        setStatus('review')
      }

      recorder.start()
      recorderRef.current = recorder

      setSeconds(0)
      setStatus('recording')
      timerRef.current = setInterval(() => setSeconds((s) => s + 1), 1000)
    } catch (err) {
      setError(describeMicError(err))
    }
  }

  function stopRecording() {
    clearInterval(timerRef.current)
    recorderRef.current.stop() // this triggers recorder.onstop above
  }

  function discard() {
    setPreview(null)
    setSeconds(0)
    setStatus('idle')
  }

  async function save() {
    setStatus('saving')
    setError('')
    try {
      const saved = await uploadRecording(preview.blob)
      onSaved(saved) // tell App so it can add it to the list
      discard()
    } catch (err) {
      setError(err.message)
      setStatus('review') // keep the recording so the person can try again
    }
  }

  const isRecording = status === 'recording'
  const hasReview = status === 'review' || status === 'saving'

  return (
    <section className="recorder" aria-label="Recorder">
      <div className="timer" role="timer" aria-live="off">
        {formatTime(seconds)}
      </div>

      {!hasReview && (
        <>
          <button
            className={`record-button ${isRecording ? 'is-recording' : ''}`}
            onClick={isRecording ? stopRecording : startRecording}
            aria-label={isRecording ? 'Stop recording' : 'Start recording'}
          >
            {isRecording ? (
              <svg viewBox="0 0 24 24" width="30" height="30" aria-hidden="true">
                <rect x="6" y="6" width="12" height="12" rx="2.5" fill="currentColor" />
              </svg>
            ) : (
              <svg viewBox="0 0 24 24" width="34" height="34" aria-hidden="true">
                <rect x="9" y="3" width="6" height="11" rx="3" fill="currentColor" />
                <path
                  d="M5.5 11a6.5 6.5 0 0 0 13 0M12 17.5V21"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                />
              </svg>
            )}
          </button>
          <p className="hint">
            {isRecording ? 'Recording. Press to stop.' : 'Press to start recording.'}
          </p>
        </>
      )}

      {hasReview && preview && (
        <div className="review">
          {/* The preview plays from memory. Nothing is saved on the server yet. */}
          <audio controls src={preview.url} />
          <div className="review-actions">
            <button className="button primary" onClick={save} disabled={status === 'saving'}>
              {status === 'saving' ? 'Saving...' : 'Save recording'}
            </button>
            <button className="button" onClick={discard} disabled={status === 'saving'}>
              Discard
            </button>
          </div>
        </div>
      )}

      {error && (
        <p className="message error" role="alert">
          {error}
        </p>
      )}
    </section>
  )
}