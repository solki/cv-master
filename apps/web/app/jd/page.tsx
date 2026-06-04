"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import PageHeader from "@/components/ui/page-header";
import { JDIcon } from "@/components/icons";

interface JDResult {
  id: string;
  title: string;
  company: string;
  raw_text: string;
  source_url: string;
  source_type: string;
  source_filename: string;
  created_at: string;
}

export default function JDAnalyzerPage() {
  const [rawText, setRawText] = useState("");
  const [url, setUrl] = useState("");
  const [result, setResult] = useState<JDResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handlePaste = async () => {
    setLoading(true); setError("");
    try {
      const data = await api.post("/api/job-descriptions", { title: "JD Import", raw_text: rawText, source_type: "pasted" });
      setResult(data as unknown as JDResult);
    } catch (err: unknown) { setError(err instanceof Error ? err.message : "Failed"); }
    finally { setLoading(false); }
  };

  const handleURLFetch = async () => {
    setLoading(true); setError("");
    try {
      const data = await api.post("/api/job-descriptions/fetch-url", { url });
      setResult(data as unknown as JDResult);
    } catch (err: unknown) { setError(err instanceof Error ? err.message : "Failed"); }
    finally { setLoading(false); }
  };

  const handleMDUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setLoading(true); setError("");
    try {
      const data = await api.uploadFile("/api/job-descriptions/upload-md", file);
      setResult(data as unknown as JDResult);
    } catch (err: unknown) { setError(err instanceof Error ? err.message : "Failed"); }
    finally { setLoading(false); }
  };

  const wordCount = result?.raw_text ? result.raw_text.split(/\s+/).length : 0;
  const skills = result?.raw_text ? extractSkills(result.raw_text) : [];

  return (
    <div className="space-y-8">
      <PageHeader title="JD Analyzer" description="Import a job description to analyze requirements and match against your profile" />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Paste panel */}
        <div className="bg-slate-900 rounded-lg border border-slate-700 p-6 space-y-4">
          <h2 className="font-semibold text-slate-200">Paste Job Description</h2>
          <textarea rows={8} value={rawText} onChange={(e) => setRawText(e.target.value)}
            placeholder="Paste the full job description here..."
            className="w-full border border-slate-700 rounded px-3 py-2 text-sm" />
          <button onClick={handlePaste} disabled={loading || !rawText}
            className="bg-blue-600 text-white px-4 py-2 rounded text-sm disabled:opacity-50 hover:bg-blue-500 transition-colors inline-flex items-center gap-2">
            {loading && <span className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />}
            {loading ? "Processing..." : "Analyze JD"}
          </button>
        </div>

        {/* URL + Upload panel */}
        <div className="space-y-6">
          <div className="bg-slate-900 rounded-lg border border-slate-700 p-6 space-y-4">
            <h2 className="font-semibold text-slate-200">Fetch from URL</h2>
            <input type="url" value={url} onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com/job-posting"
              className="w-full border border-slate-700 rounded px-3 py-2 text-sm" />
            <button onClick={handleURLFetch} disabled={loading || !url}
              className="bg-blue-600 text-white px-4 py-2 rounded text-sm disabled:opacity-50 hover:bg-blue-500 transition-colors inline-flex items-center gap-2">
              {loading && <span className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />}
              {loading ? "Fetching..." : "Fetch & Analyze"}
            </button>
          </div>

          <div className="bg-slate-900 rounded-lg border border-slate-700 p-6 space-y-4">
            <h2 className="font-semibold text-slate-200">Upload Markdown File</h2>
            <p className="text-xs text-slate-500">Upload a .md file containing a job description.</p>
            <input type="file" accept=".md" onChange={handleMDUpload} disabled={loading} className="text-sm" />
          </div>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-950 border border-red-800 text-red-400 p-4 rounded text-sm flex items-center justify-between">
          <span>{error}</span>
          <button onClick={() => setError("")} className="text-red-300 hover:text-red-100 font-bold">&times;</button>
        </div>
      )}

      {/* Results - structured display */}
      {result && (
        <div className="bg-slate-900 rounded-lg border border-slate-700 p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="font-semibold text-slate-200">Analysis Result</h2>
            <span className="text-xs text-slate-500 bg-slate-800 px-2 py-0.5 rounded">{result.source_type}</span>
          </div>

          {/* Meta */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
            <div>
              <p className="text-slate-500 text-xs mb-0.5">Title</p>
              <p className="text-slate-200 font-medium">{result.title || "Untitled"}</p>
            </div>
            {result.company && (
              <div>
                <p className="text-slate-500 text-xs mb-0.5">Company</p>
                <p className="text-slate-200">{result.company}</p>
              </div>
            )}
            <div>
              <p className="text-slate-500 text-xs mb-0.5">Word Count</p>
              <p className="text-slate-200">{wordCount.toLocaleString()}</p>
            </div>
            <div>
              <p className="text-slate-500 text-xs mb-0.5">Created</p>
              <p className="text-slate-200">{new Date(result.created_at).toLocaleDateString()}</p>
            </div>
          </div>

          {/* Detected skills */}
          {skills.length > 0 && (
            <div>
              <p className="text-slate-500 text-xs mb-2">Detected Keywords</p>
              <div className="flex flex-wrap gap-1.5">
                {skills.map((skill) => (
                  <span key={skill} className="text-xs bg-slate-800 text-slate-300 px-2 py-0.5 rounded border border-slate-700">{skill}</span>
                ))}
              </div>
            </div>
          )}

          {/* Raw text preview */}
          <details className="group">
            <summary className="text-sm text-slate-400 cursor-pointer hover:text-slate-300 transition-colors">
              View full text ({wordCount} words)
            </summary>
            <pre className="mt-3 text-xs text-slate-400 whitespace-pre-wrap bg-slate-950 rounded p-4 max-h-64 overflow-y-auto border border-slate-800">
              {result.raw_text}
            </pre>
          </details>

          {/* CTA */}
          <div className="pt-2 border-t border-slate-800">
            <a
              href="/resumes"
              className="inline-flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded text-sm hover:bg-blue-500 transition-colors"
            >
              Generate Resume from this JD →
            </a>
          </div>
        </div>
      )}
    </div>
  );
}

/** Extract potential skill keywords from JD text */
function extractSkills(text: string): string[] {
  const common = ["Python", "JavaScript", "TypeScript", "React", "Node.js", "FastAPI", "PostgreSQL", "Docker", "Kubernetes", "AWS", "SQL", "REST", "GraphQL", "Machine Learning", "Data Science", "CI/CD", "Git", "Agile", "Scrum", "Java", "Go", "Rust", "C++", "C#", ".NET", "Angular", "Vue", "Swift", "Kotlin", "Redis", "MongoDB", "Linux", "DevOps", "Terraform", "Spark", "Kafka"];
  const found = common.filter((skill) => {
    const regex = new RegExp(`\\b${skill.replace(/[.+]/g, "\\$&")}\\b`, "i");
    return regex.test(text);
  });
  return found.slice(0, 15);
}
