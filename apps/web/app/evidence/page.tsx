"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { api } from "@/lib/api";
import type { Evidence, PaginatedResponse } from "@/lib/types";

export default function EvidencePage() {
  const queryClient = useQueryClient();
  const { data, isLoading } = useQuery<PaginatedResponse<Evidence>>({
    queryKey: ["evidence"], queryFn: () => api.get<PaginatedResponse<Evidence>>("/api/evidence?limit=50"),
  });
  const [showNew, setShowNew] = useState(false);
  const [title, setTitle] = useState("");
  const [type, setType] = useState("user_statement");
  const [description, setDescription] = useState("");
  const [url, setUrl] = useState("");

  const createMutation = useMutation({
    mutationFn: () => api.post("/api/evidence", { title, type, description, url, confidence: 1.0 }),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["evidence"] }); setShowNew(false); setTitle(""); setDescription(""); setUrl(""); },
  });

  const evidenceTypes = ["user_statement", "document", "portfolio_link", "metric", "manager_feedback", "public_artifact"];

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Evidence</h1>
          <p className="text-zinc-500 mt-1">Supporting material for resume claims</p>
        </div>
        <button onClick={() => setShowNew(true)} className="bg-blue-600 text-white px-4 py-2 rounded text-sm">Add Evidence</button>
      </div>

      {showNew && (
        <div className="bg-white rounded-lg border border-zinc-200 p-6 space-y-3">
          <h2 className="font-semibold">New Evidence</h2>
          <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Title" className="w-full border px-3 py-2 text-sm rounded" />
          <select value={type} onChange={(e) => setType(e.target.value)} className="w-full border px-3 py-2 text-sm rounded">
            {evidenceTypes.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
          <textarea value={description} onChange={(e) => setDescription(e.target.value)} rows={3} placeholder="Description" className="w-full border px-3 py-2 text-sm rounded" />
          <input value={url} onChange={(e) => setUrl(e.target.value)} placeholder="URL (optional)" className="w-full border px-3 py-2 text-sm rounded" />
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
              {data.items.map((e: Evidence) => (
                <li key={e.id} className="border-b border-zinc-100 pb-3 flex justify-between items-center">
                  <div>
                    <p className="font-medium text-sm">{e.title}</p>
                    <p className="text-xs text-zinc-500 capitalize">{e.type.replace(/_/g, " ")}</p>
                  </div>
                  <span className={`text-xs px-2 py-0.5 rounded ${e.confidence >= 1 ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"}`}>
                    {Math.round(e.confidence * 100)}% confidence
                  </span>
                </li>
              ))}
            </ul>
          ) : <p className="text-sm text-zinc-400">No evidence records yet.</p>
        }
      </div>
    </div>
  );
}
