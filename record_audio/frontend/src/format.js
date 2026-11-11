// 75 -> "1:15"
export function formatTime(totalSeconds) {
    const minutes = Math.floor(totalSeconds / 60)
    const seconds = totalSeconds % 60
    return `${minutes}:${String(seconds).padStart(2, '0')}`
}

// 2048 -> "2 KB"
export function formatSize(bytes) {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

// "2026-10-07T14:30:15Z" -> "Oct 7, 2026, 5:30 PM" (in the viewer's time zone)
export function formatDate(isoString) {
    return new Date(isoString).toLocaleString(undefined, {
        dateStyle: 'medium',
        timeStyle: 'short',
    })
}