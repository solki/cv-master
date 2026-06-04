export default function HomePage() {
  return (
    <main style={{ padding: "2rem", fontFamily: "system-ui, sans-serif" }}>
      <h1>CV Master</h1>
      <p>API: <a href="http://localhost:8000/health">/health</a></p>
      <p>API Docs: <a href="http://localhost:8000/docs">/docs</a></p>
      <p>Adminer: <a href="http://localhost:8080">localhost:8080</a></p>
    </main>
  );
}
