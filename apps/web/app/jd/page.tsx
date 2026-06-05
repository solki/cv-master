"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import PageHeader from "@/components/ui/page-header";
import { toast } from "@/components/ui/toast";

interface JDAnalysis {
  job_title?: string;
  seniority?: string;
  required_skills?: string[];
  preferred_skills?: string[];
  responsibilities?: string[];
  domain_keywords?: string[];
  ats_keywords?: string[];
  research_queries?: string[];
  red_flags?: string[];
}

interface JDResult {
  id: string;
  title: string;
  company: string;
  raw_text: string;
  source_type: string;
  created_at: string;
}

export default function JDAnalyzerPage() {
  const [rawText, setRawText] = useState("");
  const [url, setUrl] = useState("");
  const [result, setResult] = useState<JDResult | null>(null);
  const [analysis, setAnalysis] = useState<JDAnalysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState("");

  const runAnalysis = async (jdId: string) => {
    setAnalyzing(true);
    try {
      const data = await api.post(`/api/job-descriptions/${jdId}/analyze`);
      if (data && typeof data === "object" && "analysis" in data) {
        setAnalysis((data as { analysis: JDAnalysis }).analysis);
      }
    } catch {
      // Analysis failed silently — use basic keyword display
    } finally {
      setAnalyzing(false);
    }
  };

  const handlePaste = async () => {
    setLoading(true); setError(""); setAnalysis(null);
    try {
      const data = await api.post("/api/job-descriptions", {
        title: "JD Import", raw_text: rawText, source_type: "pasted"
      }) as unknown as JDResult;
      setResult(data);
      toast("success", "JD created — analyzing...");
      await runAnalysis(data.id);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed");
    } finally { setLoading(false); }
  };

  const handleURLFetch = async () => {
    setLoading(true); setError(""); setAnalysis(null);
    try {
      const data = await api.post("/api/job-descriptions/fetch-url", { url }) as unknown as JDResult;
      setResult(data);
      toast("success", "JD fetched — analyzing...");
      await runAnalysis(data.id);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed");
    } finally { setLoading(false); }
  };

  const handleMDUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setLoading(true); setError(""); setAnalysis(null);
    try {
      const data = await api.uploadFile("/api/job-descriptions/upload-md", file) as unknown as JDResult;
      setResult(data);
      toast("success", "JD uploaded — analyzing...");
      await runAnalysis(data.id);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed");
    } finally { setLoading(false); }
  };

  const wordCount = result?.raw_text ? result.raw_text.split(/\s+/).length : 0;

  return (
    <div className="space-y-8">
      <PageHeader
        title="JD Analyzer"
        description="Import a job description to analyze requirements with AI and match against your profile"
      />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-slate-900 rounded-lg border border-slate-700 p-6 space-y-4">
          <h2 className="font-semibold text-slate-200">Paste Job Description</h2>
          <textarea rows={8} value={rawText} onChange={(e) => setRawText(e.target.value)}
            placeholder="Paste the full job description here..."
            className="w-full border border-slate-700 rounded px-3 py-2 text-sm bg-slate-800 text-slate-100" />
          <button onClick={handlePaste} disabled={loading || !rawText}
            className="bg-blue-600 text-white px-4 py-2 rounded text-sm disabled:opacity-50 hover:bg-blue-500 transition-colors inline-flex items-center gap-2">
            {loading && <span className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />}
            {loading ? "Processing..." : "Analyze JD"}
          </button>
        </div>

        <div className="space-y-6">
          <div className="bg-slate-900 rounded-lg border border-slate-700 p-6 space-y-4">
            <h2 className="font-semibold text-slate-200">Fetch from URL</h2>
            <input type="url" value={url} onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com/job-posting"
              className="w-full border border-slate-700 rounded px-3 py-2 text-sm bg-slate-800 text-slate-100" />
            <button onClick={handleURLFetch} disabled={loading || !url}
              className="bg-blue-600 text-white px-4 py-2 rounded text-sm disabled:opacity-50 hover:bg-blue-500 transition-colors inline-flex items-center gap-2">
              {loading && <span className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />}
              {loading ? "Fetching..." : "Fetch & Analyze"}
            </button>
          </div>

          <div className="bg-slate-900 rounded-lg border border-slate-700 p-6 space-y-4">
            <h2 className="font-semibold text-slate-200">Upload Markdown File</h2>
            <p className="text-xs text-slate-400">Upload a .md file containing a job description.</p>
            <input type="file" accept=".md,.txt" onChange={handleMDUpload} disabled={loading} className="text-sm" />
          </div>
        </div>
      </div>

      {error && (
        <div className="bg-red-950 border border-red-800 text-red-400 p-4 rounded text-sm flex items-center justify-between">
          <span>{error}</span>
          <button onClick={() => setError("")} className="text-red-300 hover:text-red-100 font-bold">&times;</button>
        </div>
      )}

      {result && (
        <div className="bg-slate-900 rounded-lg border border-slate-700 p-6 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="font-semibold text-slate-200">Analysis Result</h2>
            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-500 bg-slate-800 px-2 py-0.5 rounded">{result.source_type}</span>
              {analyzing && <span className="text-xs text-blue-400 animate-pulse">Analyzing with AI...</span>}
            </div>
          </div>

          {/* LLM Analysis structured display */}
          {analysis && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
                <div>
                  <p className="text-slate-500 text-xs mb-0.5">Role Title</p>
                  <p className="text-slate-100 font-medium">{analysis.job_title || result.title}</p>
                </div>
                <div>
                  <p className="text-slate-500 text-xs mb-0.5">Seniority</p>
                  <p className="text-slate-100 capitalize">{analysis.seniority || "—"}</p>
                </div>
                <div>
                  <p className="text-slate-500 text-xs mb-0.5">Word Count</p>
                  <p className="text-slate-100">{wordCount.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-slate-500 text-xs mb-0.5">Date</p>
                  <p className="text-slate-100">{new Date(result.created_at).toLocaleDateString()}</p>
                </div>
              </div>

              {/* Required Skills */}
              {analysis.required_skills && analysis.required_skills.length > 0 && (
                <div>
                  <p className="text-slate-500 text-xs mb-2 font-medium uppercase tracking-wide">Required Skills</p>
                  <div className="flex flex-wrap gap-1.5">
                    {analysis.required_skills.map((s) => (
                      <span key={s} className="text-xs bg-red-950 text-red-300 px-2 py-0.5 rounded border border-red-900">{s}</span>
                    ))}
                  </div>
                </div>
              )}

              {/* Preferred Skills */}
              {analysis.preferred_skills && analysis.preferred_skills.length > 0 && (
                <div>
                  <p className="text-slate-500 text-xs mb-2 font-medium uppercase tracking-wide">Preferred Skills</p>
                  <div className="flex flex-wrap gap-1.5">
                    {analysis.preferred_skills.map((s) => (
                      <span key={s} className="text-xs bg-amber-950 text-amber-300 px-2 py-0.5 rounded border border-amber-900">{s}</span>
                    ))}
                  </div>
                </div>
              )}

              {/* All ATS keywords */}
              {analysis.ats_keywords && analysis.ats_keywords.length > 0 && (
                <div>
                  <p className="text-slate-500 text-xs mb-2 font-medium uppercase tracking-wide">ATS Keywords</p>
                  <div className="flex flex-wrap gap-1.5">
                    {analysis.ats_keywords.map((s) => (
                      <span key={s} className="text-xs bg-slate-800 text-slate-300 px-2 py-0.5 rounded border border-slate-700">{s}</span>
                    ))}
                  </div>
                </div>
              )}

              {/* Responsibilities */}
              {analysis.responsibilities && analysis.responsibilities.length > 0 && (
                <div>
                  <p className="text-slate-500 text-xs mb-2 font-medium uppercase tracking-wide">Key Responsibilities</p>
                  <ul className="space-y-1">
                    {analysis.responsibilities.slice(0, 8).map((r, i) => (
                      <li key={i} className="text-sm text-slate-400 flex gap-2">
                        <span className="text-slate-600">•</span>
                        {r}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Raw text (collapsible) */}
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
              href={`/resumes?jd_id=${result.id}`}
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
