// src/components/Footer.jsx
export default function Footer() {
  const year = new Date().getFullYear();
  return <footer className="footer">© {year} Course Catalogue</footer>;
}