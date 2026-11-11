// Where does the FastAPI server live?
// 1. Use VITE_API_URL from a .env file if you set one
// 2. Otherwise use the same host as this web page, on port 8000
export const API_URL =
    import.meta.env.VITE_API_URL || `http://${window.location.hostname}:8000`

// One helper that every request goes through.
// It turns network problems and server errors into readable messages.
async function request(path, options) {
    let response
    try {
        response = await fetch(`${API_URL}${path}`, options)
    } catch {
        throw new Error(`Can't reach the server at ${API_URL}. Is FastAPI running?`)
    }

    if (!response.ok) {
        let message = `Server error (${response.status})`
        try {
            // FastAPI sends errors as { "detail": "..." }
            const body = await response.json()
            if (typeof body.detail === 'string') message = body.detail
        } catch {
            // the body wasn't JSON: keep the generic message
        }
        throw new Error(message)
    }

    return response.json()
}

export function listRecordings() {
    return request('/recordings')
}

export function uploadRecording(blob) {
    // FormData is how browsers send files. It becomes a "multipart" request,
    // which FastAPI reads as an UploadFile.
    // Important: do NOT set a Content-Type header yourself. The browser adds
    // it, along with a boundary code that the server needs.
    const form = new FormData()
    form.append('file', blob, 'recording')
    return request('/recordings', { method: 'POST', body: form })
}

export function deleteRecording(id) {
    return request(`/recordings/${id}`, { method: 'DELETE' })
}

// These two don't call fetch. They build links for <audio> and <a> to use.
export function audioUrl(id) {
    return `${API_URL}/recordings/${id}/audio`
}

export function downloadUrl(id) {
    return `${API_URL}/recordings/${id}/audio?download=true`
}