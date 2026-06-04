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
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    formState: { errors },
  } = useForm<EvidenceFormData>({
    resolver: zodResolver(evidenceSchema),
    defaultValues: { title: "", type: "user_statement", description: "", url: "", confidence: 1.0 },
  });

  const saveMutation = useMutation({
    mutationFn: (formData: EvidenceFormData) =>
      editingId ? api.put(`/api/evidence/${editingId}`, formData) : api.post("/api/evidence", formData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["evidence"] });
      closeForm();
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => api.delete(`/api/evidence/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["evidence"] });
      setDeletingId(null);
    },
  });

  const closeForm = () => {
    setShowForm(false);
    setEditingId(null);
    reset();
  };

  const startEdit = (e: Evidence) => {
    setEditingId(e.id);
    setValue("title", e.title);
    setValue("type", e.type as EvidenceFormData["type"]);
    setValue("description", e.description || "");
    setValue("url", e.url || "");
    setValue("confidence", e.confidence);
    setShowForm(true);
  };

  const onSubmit = (formData: EvidenceFormData) => saveMutation.mutate(formData);

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Evidence</h1>
          <p className="text-zinc-500 mt-1">Supporting material for resume claims</p>
        </div>
        <button onClick={() => { setEditingId(null); reset(); setShowForm(true); }}
          className="bg-blue-600 text-white px-4 py-2 rounded text-sm hover:bg-blue-700 transition-colors">
          Add Evidence
        </button>
      </div>

      {error && (
        <div className="bg-red-50 text-red-700 text-sm p-3 rounded border border-red-200">
          Failed to load evidence: {error.message}
        </div>
      )}

      {showForm && (
        <form onSubmit={handleSubmit(onSubmit)} className="bg-white rounded-lg border border-zinc-200 p-6 space-y-3">
          <h2 className="font-semibold">{editingId ? "Edit Evidence" : "New Evidence"}</h2>
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
          {saveMutation.isError && (
            <p className="text-red-500 text-sm">Save failed: {saveMutation.error.message}</p>
          )}
          <div className="flex gap-2">
            <button type="submit" disabled={saveMutation.isPending}
              className="bg-blue-600 text-white px-4 py-2 rounded text-sm disabled:opacity-50 inline-flex items-center gap-2">
              {saveMutation.isPending && <span className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />}
              {saveMutation.isPending ? "Saving..." : editingId ? "Update" : "Save"}
            </button>
            <button type="button" onClick={closeForm} className="text-sm text-zinc-500 hover:text-zinc-700">Cancel</button>
          </div>
        </form>
      )}

      <div className="bg-white rounded-lg border border-zinc-200 p-6">
        {isLoading ? <p className="text-zinc-400 text-sm">Loading...</p> :
          data?.items?.length ? (
            <ul className="space-y-2">
              {data.items.map((e: Evidence) => (
                <li key={e.id} className="flex items-center justify-between border-b border-zinc-100 pb-2 group">
                  <button onClick={() => startEdit(e)} className="text-left flex-1 hover:bg-zinc-50 rounded px-2 py-1 -mx-2 transition-colors">
                    <div>
                      <p className="font-medium text-sm">{e.title}</p>
                      <p className="text-xs text-zinc-500 capitalize">{e.type.replace(/_/g, " ")}</p>
                    </div>
                  </button>
                  <div className="flex items-center gap-3">
                    <span className={`text-xs px-2 py-0.5 rounded ${e.confidence >= 1 ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"}`}>
                      {Math.round(e.confidence * 100)}%
                    </span>
                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button onClick={() => startEdit(e)}
                        className="text-xs text-blue-600 hover:bg-blue-50 px-2 py-1 rounded transition-colors">Edit</button>
                      {deletingId === e.id ? (
                        <span className="text-xs text-zinc-400 px-2">Delete?</span>
                      ) : (
                        <button onClick={() => setDeletingId(e.id)}
                          className="text-xs text-red-500 hover:bg-red-50 px-2 py-1 rounded transition-colors">Delete</button>
                      )}
                    </div>
                  </div>
                  {deletingId === e.id && (
                    <div className="flex items-center gap-1 ml-2">
                      <button onClick={() => deleteMutation.mutate(e.id)} disabled={deleteMutation.isPending}
                        className="text-xs bg-red-600 text-white px-2 py-1 rounded hover:bg-red-700 disabled:opacity-50">
                        {deleteMutation.isPending ? "..." : "Confirm"}
                      </button>
                      <button onClick={() => setDeletingId(null)}
                        className="text-xs text-zinc-500 hover:bg-zinc-100 px-2 py-1 rounded">No</button>
                    </div>
                  )}
                </li>
              ))}
            </ul>
          ) : <p className="text-sm text-zinc-400">No evidence records yet.</p>
        }
      </div>
    </div>
  );
}
