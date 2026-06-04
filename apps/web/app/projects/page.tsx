"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { api } from "@/lib/api";
import type { Project, PaginatedResponse } from "@/lib/types";
import { projectSchema, type ProjectFormData } from "@/lib/validations";
import PageHeader from "@/components/ui/page-header";
import { ListSkeleton } from "@/components/ui/skeleton";
import EmptyState from "@/components/ui/empty-state";
import ConfirmDialog from "@/components/ui/confirm-dialog";
import { toast } from "@/components/ui/toast";
import { ProjectsIcon } from "@/components/icons";

export default function ProjectsPage() {
  const queryClient = useQueryClient();
  const { data, isLoading, error } = useQuery<PaginatedResponse<Project>>({
    queryKey: ["projects"],
    queryFn: () => api.get<PaginatedResponse<Project>>("/api/projects?limit=50"),
  });
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Project | null>(null);

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

  const saveMutation = useMutation({
    mutationFn: (formData: ProjectFormData) =>
      editingId ? api.put(`/api/projects/${editingId}`, formData) : api.post("/api/projects", formData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
      toast("success", editingId ? "Project updated" : "Project created");
      closeForm();
    },
    onError: (err: Error) => toast("error", err.message),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => api.delete(`/api/projects/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
      toast("success", "Project deleted");
      setDeleteTarget(null);
    },
    onError: (err: Error) => toast("error", err.message),
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

  const onSubmit = (formData: ProjectFormData) => saveMutation.mutate(formData);

  return (
    <div className="space-y-8">
      <PageHeader
        title="Projects"
        description="Reusable resume building blocks"
        actions={
          <button
            onClick={() => { setEditingId(null); reset(); setShowForm(true); }}
            className="bg-blue-600 text-white px-4 py-2 rounded text-sm hover:bg-blue-500 transition-colors"
          >
            New Project
          </button>
        }
      />

      {error && (
        <div className="bg-red-950 text-red-400 text-sm p-3 rounded border border-red-800">
          Failed to load projects: {error.message}
        </div>
      )}

      {showForm && (
        <form onSubmit={handleSubmit(onSubmit)} className="bg-slate-900 rounded-lg border border-slate-700 p-6 space-y-3">
          <h2 className="font-semibold text-slate-200">{editingId ? "Edit Project" : "New Project"}</h2>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <input {...register("title")} placeholder="Title *" className={`border px-3 py-2 text-sm rounded w-full ${errors.title ? "border-red-500" : ""}`} />
              {errors.title && <p className="text-red-400 text-xs mt-1">{errors.title.message}</p>}
            </div>
            <input {...register("organization")} placeholder="Organization" className="border px-3 py-2 text-sm rounded" />
            <input {...register("role")} placeholder="Role" className="border px-3 py-2 text-sm rounded" />
            <input {...register("domain")} placeholder="Domain" className="border px-3 py-2 text-sm rounded" />
            <input {...register("skills")} placeholder="Skills (comma-separated)" className="border px-3 py-2 text-sm rounded col-span-2" />
            <input {...register("tools")} placeholder="Tools (comma-separated)" className="border px-3 py-2 text-sm rounded col-span-2" />
          </div>
          <textarea {...register("summary")} rows={3} placeholder="Summary" className="w-full border px-3 py-2 text-sm rounded" />
          <div className="flex gap-2">
            <button type="submit" disabled={saveMutation.isPending}
              className="bg-blue-600 text-white px-4 py-2 rounded text-sm disabled:opacity-50 inline-flex items-center gap-2">
              {saveMutation.isPending && <span className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />}
              {saveMutation.isPending ? "Saving..." : editingId ? "Update" : "Save"}
            </button>
            <button type="button" onClick={closeForm} className="text-sm text-slate-400 hover:text-slate-200">Cancel</button>
          </div>
        </form>
      )}

      <div className="bg-slate-900 rounded-lg border border-slate-700 p-6">
        {isLoading ? (
          <ListSkeleton rows={4} />
        ) : data?.items?.length ? (
          <ul className="space-y-2">
            {data.items.map((p: Project) => (
              <li key={p.id} className="flex items-center justify-between border-b border-slate-800 pb-2 group">
                <button onClick={() => startEdit(p)} className="text-left flex-1 hover:bg-slate-800 rounded px-2 py-1 -mx-2 transition-colors">
                  <p className="font-medium text-sm text-slate-200">{p.title}</p>
                  <p className="text-xs text-slate-400">{p.role} at {p.organization} &middot; {p.domain}</p>
                </button>
                <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button onClick={() => startEdit(p)}
                    className="text-xs text-blue-400 hover:bg-blue-950 px-2 py-1 rounded transition-colors">Edit</button>
                  <button onClick={() => setDeleteTarget(p)}
                    className="text-xs text-red-400 hover:bg-red-950 px-2 py-1 rounded transition-colors">Delete</button>
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <EmptyState
            icon={<ProjectsIcon className="w-5 h-5" />}
            title="No projects yet"
            description="Add your first project to start building your resume blocks."
            action={{ label: "New Project", onClick: () => { setEditingId(null); reset(); setShowForm(true); } }}
          />
        )}
      </div>

      <ConfirmDialog
        open={deleteTarget !== null}
        title="Delete Project"
        description={`Permanently delete "${deleteTarget?.title}"? This action cannot be undone.`}
        confirmLabel="Delete"
        variant="danger"
        loading={deleteMutation.isPending}
        onConfirm={() => deleteTarget && deleteMutation.mutate(deleteTarget.id)}
        onCancel={() => setDeleteTarget(null)}
      />
    </div>
  );
}
