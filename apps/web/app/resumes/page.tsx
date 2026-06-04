"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { Resume, JD, PaginatedResponse } from "@/lib/types";
import { toast } from "@/components/ui/toast";

export default function ResumeGeneratorPage() {
  const queryClient = useQueryClient();
  const [title, setTitle] = useState("");
  const [targetRole, setTargetRole] = useState("");
  const [jdId, setJdId] = useState("");
  const [deleteTarget, setDeleteTarget] = useState<Resume | null>(null);
  const [generatingId, setGeneratingId] = useState<string | null>(null);

  const { data: resumes, isLoading: resumesLoading, error: resumesError } = useQuery<PaginatedResponse<Resume>>({
    queryKey: ["resumes", { limit: 10 }],
    queryFn: () => api.get<PaginatedResponse<Resume>>("/api/resumes?limit=10"),
  });
  const { data: jds, isLoading: jdsLoading, error: jdsError } = useQuery<PaginatedResponse<JD>>({
    queryKey: ["jds"],
    queryFn: () => api.get<PaginatedResponse<JD>>("/api/job-descriptions?limit=20"),
  });

  const createMutation = useMutation({
    mutationFn: () => api.post<Resume>("/api/resumes", { title, target_role: targetRole, job_description_id: jdId || null }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["resumes"] });
      toast("success", "Resume created");
      setTitle("");
      setTargetRole("");
      setJdId("");
    },
    onError: (err: Error) => toast("error", err.message),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => api.delete(`/api/resumes/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["resumes"] });
      toast("success", "Resume deleted");
      setDeleteTarget(null);
    },
    onError: (err: Error) => toast("error", err.message),
  });

  const handleGenerate = async (resumeId: string) => {
    setGeneratingId(resumeId);
    try {
      const resume = resumes?.items?.find((r) => r.id === resumeId);
      await api.post(`/api/resumes/${resumeId}/generate`, {
        job_description_id: resume?.job_description_id || "",
      });
      toast("success", "Version generated — ready for export");
    } catch (err: unknown) {
      toast("error", err instanceof Error ? err.message : "Generation failed");
    } finally {
      setGeneratingId(null);
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold">Resume Generator</h1>
        <p className="text-slate-400 mt-1">Create a job-targeted resume</p>
      </div>

      <div className="bg-slate-900 rounded-lg border border-slate-700 p-6 space-y-4">
        <h2 className="font-semibold text-slate-200">New Resume</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <input type="text" value={title} onChange={(e) => setTitle(e.target.value)}
            placeholder="Resume title" className="border border-slate-700 rounded px-3 py-2 text-sm bg-slate-800 text-slate-100" />
          <input type="text" value={targetRole} onChange={(e) => setTargetRole(e.target.value)}
            placeholder="Target role" className="border border-slate-700 rounded px-3 py-2 text-sm bg-slate-800 text-slate-100" />
          <select value={jdId} onChange={(e) => setJdId(e.target.value)}
            className="border border-slate-700 rounded px-3 py-2 text-sm bg-slate-800 text-slate-100 disabled:opacity-50">
            <option value="">{jdsLoading ? "Loading JDs..." : "Select JD (optional)"}</option>
            {jds?.items?.map((jd: JD) => (
              <option key={jd.id} value={jd.id}>{jd.title}</option>
            ))}
          </select>
        </div>
        <button onClick={() => createMutation.mutate()} disabled={createMutation.isPending || !title}
          className="bg-blue-600 text-white px-4 py-2 rounded text-sm disabled:opacity-50 inline-flex items-center gap-2 hover:bg-blue-500 transition-colors">
          {createMutation.isPending && <span className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />}
          {createMutation.isPending ? "Creating..." : "Create Resume"}
        </button>
      </div>

      {(resumesError || jdsError) && (
        <div className="bg-red-950 text-red-400 text-sm p-3 rounded border border-red-800">
          Failed to load data. Check that the API is running.
        </div>
      )}

      <div className="bg-slate-900 rounded-lg border border-slate-700 p-6">
        <h2 className="font-semibold text-slate-200 mb-4">Your Resumes</h2>
        {resumesLoading ? (
          <p className="text-sm text-slate-400">Loading...</p>
        ) : resumesError ? (
          <p className="text-sm text-red-400">Failed to load resumes</p>
        ) : resumes?.items?.length ? (
          <ul className="space-y-2">
            {resumes.items.map((r: Resume) => (
              <li key={r.id} className="flex items-center justify-between border-b border-slate-800 pb-2 group">
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-sm text-slate-200 truncate">{r.title}</p>
                  <p className="text-xs text-slate-400">{r.target_role || "—"} &middot; {new Date(r.created_at).toLocaleDateString()}</p>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`text-xs px-2 py-0.5 rounded-full ${r.status === "approved" ? "bg-emerald-900 text-emerald-400" : "bg-slate-800 text-slate-400"}`}>
                    {r.status}
                  </span>
                  <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      onClick={() => handleGenerate(r.id)}
                      disabled={generatingId === r.id}
                      className="text-xs text-blue-400 hover:bg-blue-950 px-2 py-1 rounded transition-colors disabled:opacity-50"
                    >
                      {generatingId === r.id ? "..." : "Generate"}
                    </button>
                    <button
                      onClick={() => setDeleteTarget(r)}
                      className="text-xs text-red-400 hover:bg-red-950 px-2 py-1 rounded transition-colors"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-slate-500">No resumes yet.</p>
        )}
      </div>

      {/* Confirm delete */}
      {deleteTarget && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="fixed inset-0 bg-black/60" onClick={() => setDeleteTarget(null)} />
          <div className="relative bg-slate-900 rounded-xl border border-slate-700 shadow-md p-6 max-w-sm mx-4 w-full">
            <h3 className="text-base font-semibold text-slate-100 mb-2">Delete Resume</h3>
            <p className="text-sm text-slate-400 mb-6">Permanently delete "{deleteTarget.title}"? This action cannot be undone.</p>
            <div className="flex gap-3 justify-end">
              <button onClick={() => setDeleteTarget(null)} className="px-4 py-2 text-sm text-slate-300 hover:bg-slate-800 rounded transition-colors">Cancel</button>
              <button
                onClick={() => deleteMutation.mutate(deleteTarget.id)}
                disabled={deleteMutation.isPending}
                className="px-4 py-2 text-sm text-white bg-red-600 hover:bg-red-500 rounded transition-colors disabled:opacity-50 inline-flex items-center gap-2"
              >
                {deleteMutation.isPending && <span className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />}
                {deleteMutation.isPending ? "Deleting..." : "Delete"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
