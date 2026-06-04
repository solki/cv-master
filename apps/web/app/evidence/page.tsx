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
          <p className="text-slate-500 mt-1">Supporting material for resume claims</p>
        </div>
        <button onClick={() => { setEditingId(null); reset(); setShowForm(true); }}
          className="bg-blue-600 text-white px-4 py-2 rounded text-sm hover:bg-blue-500 transition-colors">
          Add Evidence
        </button>
      </div>

      {error && (
        <div className="bg-red-950 text-red-400 text-sm p-3 rounded border border-red-800">
          Failed to load evidence: {error.message}
        </div>
      )}

      {showForm && (
        <form onSubmit={handleSubmit(onSubmit)} className="bg-slate-900 rounded-lg shadow-sm border border-slate-700 p-6 space-y-3">
          <h2 className="font-semibold">{editingId ? "Edit Evidence" : "New Evidence"}</h2>
          <div>
            <input {...register("title")} placeholder="Title *" className={`border px-3 py-2 text-sm rounded w-full ${errors.title ? "border-red-500" : ""}`} />
            {errors.title && <p className="text-red-400 text-xs mt-1">{errors.title.message}</p>}
          </div>
          <select {...register("type")} className="w-full border px-3 py-2 text-sm rounded">
            {EVIDENCE_TYPES.map((t) => <option key={t} value={t}>{t.replace(/_/g, " ")}</option>)}
          </select>
          <textarea {...register("description")} rows={3} placeholder="Description" className="w-full border px-3 py-2 text-sm rounded" />
          <div>
            <input {...register("url")} placeholder="URL (optional)" className={`border px-3 py-2 text-sm rounded w-full ${errors.url ? "border-red-500" : ""}`} />
            {errors.url && <p className="text-red-400 text-xs mt-1">{errors.url.message}</p>}
          </div>
          {saveMutation.isError && (
            <p className="text-red-400 text-sm">Save failed: {saveMutation.error.message}</p>
          )}
          <div className="flex gap-2">
            <button type="submit" disabled={saveMutation.isPending}
              className="bg-blue-600 text-white px-4 py-2 rounded text-sm disabled:opacity-50 inline-flex items-center gap-2">
              {saveMutation.isPending && <span className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />}
              {saveMutation.isPending ? "Saving..." : editingId ? "Update" : "Save"}
            </button>
            <button type="button" onClick={closeForm} className="text-sm text-slate-500 hover:text-slate-300">Cancel</button>
          </div>
        </form>
      )}

      <div className="bg-slate-900 rounded-lg shadow-sm border border-slate-700 p-6">
        {isLoading ? <p className="text-slate-500 text-sm">Loading...</p> :
          data?.items?.length ? (
            <ul className="space-y-2">
              {data.items.map((e: Evidence) => (
                <li key={e.id} className="flex items-center justify-between border-b border-slate-800 pb-2 group">
                  <button onClick={() => startEdit(e)} className="text-left flex-1 hover:bg-slate-950 rounded px-2 py-1 -mx-2 transition-colors">
                    <div>
                      <p className="font-medium text-sm">{e.title}</p>
                      <p className="text-xs text-slate-500 capitalize">{e.type.replace(/_/g, " ")}</p>
                    </div>
                  </button>
                  <div className="flex items-center gap-3">
                    <span className={`text-xs px-2 py-0.5 rounded ${e.confidence >= 1 ? "bg-green-900 text-green-400" : "bg-yellow-900 text-yellow-400"}`}>
                      {Math.round(e.confidence * 100)}%
                    </span>
                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button onClick={() => startEdit(e)}
                        className="text-xs text-blue-400 hover:bg-blue-950 px-2 py-1 rounded transition-colors">Edit</button>
                      {deletingId === e.id ? (
                        <span className="text-xs text-slate-500 px-2">Delete?</span>
                      ) : (
                        <button onClick={() => setDeletingId(e.id)}
                          className="text-xs text-red-400 hover:bg-red-950 px-2 py-1 rounded transition-colors">Delete</button>
                      )}
                    </div>
                  </div>
                  {deletingId === e.id && (
                    <div className="flex items-center gap-1 ml-2">
                      <button onClick={() => deleteMutation.mutate(e.id)} disabled={deleteMutation.isPending}
                        className="text-xs bg-red-600 text-white px-2 py-1 rounded hover:bg-red-500 disabled:opacity-50">
                        {deleteMutation.isPending ? "..." : "Confirm"}
                      </button>
                      <button onClick={() => setDeletingId(null)}
                        className="text-xs text-slate-500 hover:bg-slate-800 px-2 py-1 rounded">No</button>
                    </div>
                  )}
                </li>
              ))}
            </ul>
          ) : <p className="text-sm text-slate-500">No evidence records yet.</p>
        }
      </div>
    </div>
  );
}
