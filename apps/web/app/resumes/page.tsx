"use client";

import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { Resume, JD, PaginatedResponse } from "@/lib/types";

export default function ResumeGeneratorPage() {
  const [title, setTitle] = useState("");
  const [targetRole, setTargetRole] = useState("");
  const [jdId, setJdId] = useState("");

  const { data: resumes } = useQuery<PaginatedResponse<Resume>>({
    queryKey: ["resumes"],
    queryFn: () => api.get<PaginatedResponse<Resume>>("/api/resumes?limit=10"),
  });
  const { data: jds } = useQuery<PaginatedResponse<JD>>({
    queryKey: ["jds"],
    queryFn: () => api.get<PaginatedResponse<JD>>("/api/job-descriptions?limit=20"),
  });

  const createMutation = useMutation({
    mutationFn: () => api.post<Resume>("/api/resumes", { title, target_role: targetRole, job_description_id: jdId || null }),
    onSuccess: () => { setTitle(""); setTargetRole(""); },
  });

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold">Resume Generator</h1>
        <p className="text-zinc-500 mt-1">Create a job-targeted resume</p>
      </div>

      <div className="bg-white rounded-lg border border-zinc-200 p-6 space-y-4">
        <h2 className="font-semibold">New Resume</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <input type="text" value={title} onChange={(e) => setTitle(e.target.value)}
            placeholder="Resume title" className="border border-zinc-200 rounded px-3 py-2 text-sm" />
          <input type="text" value={targetRole} onChange={(e) => setTargetRole(e.target.value)}
            placeholder="Target role" className="border border-zinc-200 rounded px-3 py-2 text-sm" />
          <select value={jdId} onChange={(e) => setJdId(e.target.value)} className="border border-zinc-200 rounded px-3 py-2 text-sm">
            <option value="">Select JD (optional)</option>
            {jds?.items?.map((jd: JD) => (
              <option key={jd.id} value={jd.id}>{jd.title}</option>
            ))}
          </select>
        </div>
        <button onClick={() => createMutation.mutate()} disabled={createMutation.isPending || !title}
          className="bg-blue-600 text-white px-4 py-2 rounded text-sm disabled:opacity-50">
          {createMutation.isPending ? "Creating..." : "Create Resume"}
        </button>
      </div>

      <div className="bg-white rounded-lg border border-zinc-200 p-6">
        <h2 className="font-semibold mb-4">Your Resumes</h2>
        {resumes?.items?.length ? (
          <ul className="space-y-3">
            {resumes.items.map((r: Resume) => (
              <li key={r.id} className="flex justify-between items-center border-b border-zinc-100 pb-2">
                <div>
                  <p className="font-medium text-sm">{r.title}</p>
                  <p className="text-xs text-zinc-500">{r.target_role} &middot; {new Date(r.created_at).toLocaleDateString()}</p>
                </div>
                <span className={`text-xs px-2 py-0.5 rounded ${r.status === "approved" ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"}`}>
                  {r.status}
                </span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-zinc-400">No resumes yet.</p>
        )}
      </div>
    </div>
  );
}
