"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { api } from "@/lib/api";
import type { Project, PaginatedResponse } from "@/lib/types";

export default function ProjectsPage() {
  const queryClient = useQueryClient();
  const { data, isLoading } = useQuery<PaginatedResponse<Project>>({
    queryKey: ["projects"],
    queryFn: () => api.get<PaginatedResponse<Project>>("/api/projects?limit=50"),
  });
  const [showNew, setShowNew] = useState(false);
  const [title, setTitle] = useState("");
  const [organization, setOrganization] = useState("");
  const [summary, setSummary] = useState("");
  const [role, setRole] = useState("");
  const [domain, setDomain] = useState("");
  const [skills, setSkills] = useState("");
  const [tools, setTools] = useState("");

  const createMutation = useMutation({
    mutationFn: () => api.post("/api/projects", { title, organization, summary, role, domain, skills, tools }),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["projects"] }); setShowNew(false); resetForm(); },
  });

  const resetForm = () => {
    setTitle(""); setOrganization(""); setSummary(""); setRole(""); setDomain(""); setSkills(""); setTools("");
  };

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Projects</h1>
          <p className="text-zinc-500 mt-1">Reusable resume building blocks</p>
        </div>
        <button onClick={() => setShowNew(true)} className="bg-blue-600 text-white px-4 py-2 rounded text-sm">New Project</button>
      </div>

      {showNew && (
        <div className="bg-white rounded-lg border border-zinc-200 p-6 space-y-3">
          <h2 className="font-semibold">New Project</h2>
          <div className="grid grid-cols-2 gap-3">
            <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Title" className="border px-3 py-2 text-sm rounded" />
            <input value={organization} onChange={(e) => setOrganization(e.target.value)} placeholder="Organization" className="border px-3 py-2 text-sm rounded" />
            <input value={role} onChange={(e) => setRole(e.target.value)} placeholder="Role" className="border px-3 py-2 text-sm rounded" />
            <input value={domain} onChange={(e) => setDomain(e.target.value)} placeholder="Domain" className="border px-3 py-2 text-sm rounded" />
            <input value={skills} onChange={(e) => setSkills(e.target.value)} placeholder="Skills (comma-separated)" className="border px-3 py-2 text-sm rounded col-span-2" />
            <input value={tools} onChange={(e) => setTools(e.target.value)} placeholder="Tools (comma-separated)" className="border px-3 py-2 text-sm rounded col-span-2" />
          </div>
          <textarea value={summary} onChange={(e) => setSummary(e.target.value)} rows={3} placeholder="Summary" className="w-full border px-3 py-2 text-sm rounded" />
          <div className="flex gap-2">
            <button onClick={() => createMutation.mutate()} disabled={createMutation.isPending || !title}
              className="bg-blue-600 text-white px-4 py-2 rounded text-sm disabled:opacity-50">Save</button>
            <button onClick={() => setShowNew(false)} className="text-sm text-zinc-500">Cancel</button>
          </div>
        </div>
      )}

      <div className="bg-white rounded-lg border border-zinc-200 p-6">
        {isLoading ? <p className="text-zinc-400 text-sm">Loading...</p> :
          data?.items?.length ? (
            <ul className="space-y-3">
              {data.items.map((p: Project) => (
                <li key={p.id} className="border-b border-zinc-100 pb-3">
                  <p className="font-medium text-sm">{p.title}</p>
                  <p className="text-xs text-zinc-500">{p.role} at {p.organization} &middot; {p.domain}</p>
                </li>
              ))}
            </ul>
          ) : <p className="text-sm text-zinc-400">No projects yet.</p>
        }
      </div>
    </div>
  );
}
