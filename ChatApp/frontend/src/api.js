//Get our server IP
export const API_URL =
    import.meta.env.VITE_API_URL || `http://${window.location.hostname}:8000`

// check server availability and which model is running
export async function checkServer() {
    const response = await fetch(`${API_URL}`)
    if (!response.ok) throw new Error('Server responded with an error')
    return response.json()
}

// Send the conversation and read the reply as it streams in
// messages->[{role: 'user' | 'assistant', content:'...'}]
// onToken-> called with each new piece of text
// signal-> lets us cancel the request(the stop button)
export async function streamChat(messages, onToken, signal) {
    let response
    try {
        response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ messages }),
            signal,
        })
    } catch (error) {
        if (error.name === 'AbortError') throw error
        throw new Error(`Can't reach the server at ${API_URL}. Is FastAPI running?`)
    }

    if (!response.ok) {
        throw new Error(`Server error (${response.status})`)
    }

    //The body arrives in chunks. Read them one by one until the stream ends
    const reader = response.body.getReader()
    const decoder = new TextDecoder()

    while (true) {
        const { done, value } = await reader.read()
        if (done) break
            //stream: true keeps characters that are split across chunks intact
        onToken(decoder.decode(value, { stream: true }))
    }
}