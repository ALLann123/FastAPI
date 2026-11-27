// src/components/Badge.jsx
export default function Badge({ text, type = 'info' }) {
  return <span className={`badge badge-${type}`}>{text}</span>;
}