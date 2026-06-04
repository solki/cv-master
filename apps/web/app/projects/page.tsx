"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { api } from "@/lib/api";
import type { Project, PaginatedResponse } from "@/lib/types";
import { projectSchema, type ProjectFormData } from "@/lib/validations";

export default function ProjectsPage() {
  const queryClient = useQueryClient();
  const { data, isLoading, error } = useQuery<PaginatedResponse<Project>>({
    queryKey: ["projects"],
    queryFn: () => api.get<PaginatedResponse<Project>>("/api/projects?limit=50"),
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
  } = useForm<ProjectFormData>({
    resolver: zodResolver(projectSchema),
    defaultValues: { title: "", organization: "", role: "", domain: "", summary: "", skills: "", tools: "" },
  });

  const createMutation = useMutation({
    mutationFn: (data: ProjectFormData) =>
      editingId ? api.put(`/api/projects/${editingId}`, data) : api.post("/api/projects", data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
      closeForm();
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => api.delete(`/api/projects/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
      setDeletingId(null);
    },
  });

  const closeForm = () => {
    setShowForm(false);
    setEditingId(null);
    reset();
  };

  const startEdit = (p: Project) => {
    setEditingId(p.id);
    setValue("title", p.title);
    setValue("organization", p.organization || "");
    setValue("role", p.role || "");
    setValue("domain", p.domain || "");
    setValue("summary", p.summary || "");
    setValue("skills", p.skills || "");
    setValue("tools", p.tools || "");
    setShowForm(true);
  };

  const onSubmit = (formData: ProjectFormData) => createMutation.mutate(formData);

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Projects</h1>
          <p className="text-zinc-500 mt-1">Reusable resume building blocks</p>
        </div>
        <button onClick={() => { setEditingId(null); reset(); setShowForm(true); }}
          className="bg-blue-600 text-white px-4 py-2 rounded text-sm hover:bg-blue-700 transition-colors">
          New Project
        </button>
      </div>

      {error && (
        <div className="bg-red-50 text-red-700 text-sm p-3 rounded border border-red-200">
          Failed to load projects: {error.message}
        </div>
      )}

      {showForm && (
        <form onSubmit={handleSubmit(onSubmit)} className="bg-white rounded-lg border border-zinc-200 p-6 space-y-3">
          <h2 className="font-semibold">{editingId ? "Edit Project" : "New Project"}</h2>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <input {...register("title")} placeholder="Title *" className={`border px-3 py-2 text-sm rounded w-full ${errors.title ? "border-red-400" : ""}`} />
              {errors.title && <p className="text-red-500 text-xs mt-1">{errors.title.message}</p>}
            </div>
            <input {...register("organization")} placeholder="Organization" className="border px-3 py-2 text-sm rounded" />
            <input {...register("role")} placeholder="Role" className="border px-3 py-2 text-sm rounded" />
            <input {...register("domain")} placeholder="Domain" className="border px-3 py-2 text-sm rounded" />
            <input {...register("skills")} placeholder="Skills (comma-separated)" className="border px-3 py-2 text-sm rounded col-span-2" />
            <input {...register("tools")} placeholder="Tools (comma-separated)" className="border px-3 py-2 text-sm rounded col-span-2" />
          </div>
          <textarea {...register("summary")} rows={3} placeholder="Summary" className="w-full border px-3 py-2 text-sm rounded" />
          {createMutation.isError && (
            <p className="text-red-500 text-sm">Save failed: {createMutation.error.message}</p>
          )}
          <div className="flex gap-2">
            <button type="submit" disabled={createMutation.isPending}
              className="bg-blue-600 text-white px-4 py-2 rounded text-sm disabled:opacity-50 inline-flex items-center gap-2">
              {createMutation.isPending && <span className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />}
              {createMutation.isPending ? "Saving..." : editingId ? "Update" : "Save"}
            </button>
            <button type="button" onClick={closeForm} className="text-sm text-zinc-500 hover:text-zinc-700">Cancel</button>
          </div>
        </form>
      )}

      <div className="bg-white rounded-lg border border-zinc-200 p-6">
        {isLoading ? <p className="text-zinc-400 text-sm">Loading...</p> :
          data?.items?.length ? (
            <ul className="space-y-2">
              {data.items.map((p: Project) => (
                <li key={p.id} className="flex items-center justify-between border-b border-zinc-100 pb-2 group">
                  <button onClick={() => startEdit(p)} className="text-left flex-1 hover:bg-zinc-50 rounded px-2 py-1 -mx-2 transition-colors">
                    <p className="font-medium text-sm">{p.title}</p>
                    <p className="text-xs text-zinc-500">{p.role} at {p.organization} &middot; {p.domain}</p>
                  </button>
                  <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button onClick={() => startEdit(p)}
                      className="text-xs text-blue-600 hover:bg-blue-50 px-2 py-1 rounded transition-colors">Edit</button>
                    {deletingId === p.id ? (
                      <span className="text-xs text-zinc-400 px-2">Delete?</span>
                    ) : (
                      <button onClick={() => setDeletingId(p.id)}
                        className="text-xs text-red-500 hover:bg-red-50 px-2 py-1 rounded transition-colors">Delete</button>
                    )}
                  </div>
                  {deletingId === p.id && (
                    <div className="flex items-center gap-1 ml-2">
                      <button onClick={() => deleteMutation.mutate(p.id)} disabled={deleteMutation.isPending}
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
          ) : <p className="text-sm text-zinc-400">No projects yet.</p>
        }
      </div>
    </div>
  );
}
