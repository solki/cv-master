"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { api } from "@/lib/api";
import type { Profile } from "@/lib/types";

export default function CareerProfilePage() {
  const queryClient = useQueryClient();
  const { data: profile } = useQuery<Profile>({ queryKey: ["profile"], queryFn: () => api.get<Profile>("/api/profile") });
  const [form, setForm] = useState<Record<string, string>>({ full_name: "", headline: "", location: "", email: "", phone: "", links: "", default_summary: "" });
  const [editing, setEditing] = useState(false);
  const [uploading, setUploading] = useState(false);

  const mutation = useMutation({
    mutationFn: (data: Record<string, string>) => api.put<Profile>("/api/profile", data),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["profile"] }); setEditing(false); },
  });

  const handleSave = () => mutation.mutate(form);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      const result = await api.uploadFile<{ ingestion_id: string; status: string }>("/api/ingestion/resume/upload", file);
      alert(`Resume uploaded! Ingestion ID: ${result.ingestion_id}`);
    } catch (err: unknown) {
      alert("Upload failed: " + (err instanceof Error ? err.message : "unknown error"));
    } finally {
      setUploading(false);
    }
  };

  if (!profile) return <p className="text-zinc-400">Loading...</p>;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold">Career Profile</h1>
        <p className="text-zinc-500 mt-1">Manage your professional identity</p>
      </div>

      <div className="bg-white rounded-lg border border-zinc-200 p-6 space-y-4">
        <div className="flex justify-between items-center">
          <h2 className="font-semibold">Personal Information</h2>
          <button onClick={() => setEditing(!editing)} className="text-sm text-blue-600 hover:underline">
            {editing ? "Cancel" : "Edit"}
          </button>
        </div>

        {editing ? (
          <div className="space-y-3">
            {["full_name", "headline", "location", "email", "phone", "links"].map((field) => (
              <input key={field} type="text" placeholder={field.replace(/_/g, " ")}
                value={form[field] || (profile as unknown as Record<string, string>)[field] || ""}
                onChange={(e) => setForm({ ...form, [field]: e.target.value })}
                className="w-full border border-zinc-200 rounded px-3 py-2 text-sm"
              />
            ))}
            <textarea placeholder="Default summary" rows={4}
              value={form.default_summary || profile.default_summary || ""}
              onChange={(e) => setForm({ ...form, default_summary: e.target.value })}
              className="w-full border border-zinc-200 rounded px-3 py-2 text-sm"
            />
            <button onClick={handleSave} disabled={mutation.isPending}
              className="bg-blue-600 text-white px-4 py-2 rounded text-sm disabled:opacity-50">
              {mutation.isPending ? "Saving..." : "Save Profile"}
            </button>
          </div>
        ) : (
          <div className="space-y-2 text-sm text-zinc-600">
            <p><span className="font-medium text-zinc-800">Name:</span> {profile.full_name || <span className="text-zinc-300">Not set</span>}</p>
            <p><span className="font-medium text-zinc-800">Headline:</span> {profile.headline || <span className="text-zinc-300">Not set</span>}</p>
            <p><span className="font-medium text-zinc-800">Location:</span> {profile.location || <span className="text-zinc-300">Not set</span>}</p>
            <p><span className="font-medium text-zinc-800">Email:</span> {profile.email || <span className="text-zinc-300">Not set</span>}</p>
            <p><span className="font-medium text-zinc-800">Phone:</span> {profile.phone || <span className="text-zinc-300">Not set</span>}</p>
          </div>
        )}
      </div>

      <div className="bg-white rounded-lg border border-zinc-200 p-6 space-y-4">
        <h2 className="font-semibold">Import from Existing Resume</h2>
        <p className="text-sm text-zinc-500">Upload a PDF resume to extract positions, skills, and education.</p>
        <input type="file" accept=".pdf" onChange={handleUpload} disabled={uploading} className="text-sm" />
        {uploading && <p className="text-sm text-blue-600">Uploading and analyzing...</p>}
      </div>
    </div>
  );
}
