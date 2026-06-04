"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { api } from "@/lib/api";
import type { Evidence, PaginatedResponse } from "@/lib/types";
import { evidenceSchema, type EvidenceFormData } from "@/lib/validations";

const EVIDENCE_TYPES = ["user_statement", "document", "portfolio_link", "metric", "manager_feedback", "public_artifact"];

export default function EvidencePage() {
  const queryClient = useQueryClient();
  const { data, isLoading, error } = useQuery<PaginatedResponse<Evidence>>({
    queryKey: ["evidence"], queryFn: () => api.get<PaginatedResponse<Evidence>>("/api/evidence?limit=50"),
  });
  const [showNew, setShowNew] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<EvidenceFormData>({
    resolver: zodResolver(evidenceSchema),
    defaultValues: { title: "", type: "user_statement", description: "", url: "", confidence: 1.0 },
  });

  const createMutation = useMutation({
    mutationFn: (data: EvidenceFormData) => api.post("/api/evidence", data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["evidence"] });
      setShowNew(false);
      reset();
    },
  });

  const onSubmit = (data: EvidenceFormData) => createMutation.mutate(data);

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Evidence</h1>
          <p className="text-zinc-500 mt-1">Supporting material for resume claims</p>
        </div>
        <button onClick={() => setShowNew(true)} className="bg-blue-600 text-white px-4 py-2 rounded text-sm hover:bg-blue-700 transition-colors">Add Evidence</button>
      </div>

      {error && (
        <div className="bg-red-50 text-red-700 text-sm p-3 rounded border border-red-200">
          Failed to load evidence: {error.message}
        </div>
      )}

      {showNew && (
        <form onSubmit={handleSubmit(onSubmit)} className="bg-white rounded-lg border border-zinc-200 p-6 space-y-3">
          <h2 className="font-semibold">New Evidence</h2>
          <div>
            <input {...register("title")} placeholder="Title *" className={`border px-3 py-2 text-sm rounded w-full ${errors.title ? "border-red-400" : ""}`} />
            {errors.title && <p className="text-red-500 text-xs mt-1">{errors.title.message}</p>}
          </div>
          <select {...register("type")} className="w-full border px-3 py-2 text-sm rounded">
            {EVIDENCE_TYPES.map((t) => <option key={t} value={t}>{t.replace(/_/g, " ")}</option>)}
          </select>
          <textarea {...register("description")} rows={3} placeholder="Description" className="w-full border px-3 py-2 text-sm rounded" />
          <div>
            <input {...register("url")} placeholder="URL (optional)" className={`border px-3 py-2 text-sm rounded w-full ${errors.url ? "border-red-400" : ""}`} />
            {errors.url && <p className="text-red-500 text-xs mt-1">{errors.url.message}</p>}
          </div>
          {createMutation.isError && (
            <p className="text-red-500 text-sm">Save failed: {createMutation.error.message}</p>
          )}
          <div className="flex gap-2">
            <button type="submit" disabled={createMutation.isPending}
              className="bg-blue-600 text-white px-4 py-2 rounded text-sm disabled:opacity-50 inline-flex items-center gap-2">
              {createMutation.isPending && <span className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />}
              {createMutation.isPending ? "Saving..." : "Save"}
            </button>
            <button type="button" onClick={() => setShowNew(false)} className="text-sm text-zinc-500 hover:text-zinc-700">Cancel</button>
          </div>
        </form>
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
