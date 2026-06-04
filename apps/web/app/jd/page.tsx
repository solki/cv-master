"use client";

import { useState } from "react";
import { api } from "@/lib/api";

export default function JDAnalyzerPage() {
  const [rawText, setRawText] = useState("");
  const [url, setUrl] = useState("");
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handlePaste = async () => {
    setLoading(true); setError("");
    try {
      const data = await api.post("/api/job-descriptions", { title: "JD Import", raw_text: rawText, source_type: "pasted" });
      setResult(data as Record<string, unknown>);
    } catch (err: unknown) { setError(err instanceof Error ? err.message : "Failed"); }
    finally { setLoading(false); }
  };

  const handleURLFetch = async () => {
    setLoading(true); setError("");
    try {
      const data = await api.post("/api/job-descriptions/fetch-url", { url });
      setResult(data as Record<string, unknown>);
    } catch (err: unknown) { setError(err instanceof Error ? err.message : "Failed"); }
    finally { setLoading(false); }
  };

  const handleMDUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setLoading(true); setError("");
    try {
      const data = await api.uploadFile("/api/job-descriptions/upload-md", file);
      setResult(data as Record<string, unknown>);
    } catch (err: unknown) { setError(err instanceof Error ? err.message : "Failed"); }
    finally { setLoading(false); }
  };

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold">JD Analyzer</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg border border-zinc-200 p-6 space-y-4">
          <h2 className="font-semibold">Paste Job Description</h2>
          <textarea rows={8} value={rawText} onChange={(e) => setRawText(e.target.value)}
            placeholder="Paste the full job description here..."
            className="w-full border border-zinc-200 rounded px-3 py-2 text-sm" />
          <button onClick={handlePaste} disabled={loading || !rawText}
            className="bg-blue-600 text-white px-4 py-2 rounded text-sm disabled:opacity-50">
            {loading ? "Processing..." : "Analyze JD"}
          </button>
        </div>

        <div className="space-y-6">
          <div className="bg-white rounded-lg border border-zinc-200 p-6 space-y-4">
            <h2 className="font-semibold">Fetch from URL</h2>
            <input type="url" value={url} onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com/job-posting"
              className="w-full border border-zinc-200 rounded px-3 py-2 text-sm" />
            <button onClick={handleURLFetch} disabled={loading || !url}
              className="bg-blue-600 text-white px-4 py-2 rounded text-sm disabled:opacity-50">
              Fetch & Analyze
            </button>
          </div>

          <div className="bg-white rounded-lg border border-zinc-200 p-6 space-y-4">
            <h2 className="font-semibold">Upload Markdown File</h2>
            <input type="file" accept=".md" onChange={handleMDUpload} className="text-sm" />
          </div>
        </div>
      </div>

      {error && <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded text-sm">{error}</div>}
      {result && (
        <div className="bg-white rounded-lg border border-zinc-200 p-6">
          <h2 className="font-semibold mb-4">JD Analysis Result</h2>
          <pre className="text-xs text-zinc-600 whitespace-pre-wrap">{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
