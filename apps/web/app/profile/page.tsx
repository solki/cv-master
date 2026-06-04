"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import type { Profile } from "@/lib/types";

export default function CareerProfilePage() {
  const queryClient = useQueryClient();
  const { data: profile } = useQuery<Profile>({ queryKey: ["profile"], queryFn: () => api.get<Profile>("/api/profile") });
  const [form, setForm] = useState<Record<string, string>>({ full_name: "", headline: "", location: "", email: "", phone: "", links: "", default_summary: "" });
  const [editing, setEditing] = useState(false);

  useEffect(() => {
    if (profile) {
      setForm({
        full_name: profile.full_name || "",
        headline: profile.headline || "",
        location: profile.location || "",
        email: profile.email || "",
        phone: profile.phone || "",
        links: profile.links || "",
        default_summary: profile.default_summary || "",
      });
    }
  }, [profile]);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  const mutation = useMutation({
    mutationFn: (data: Record<string, string>) => api.put<Profile>("/api/profile", data),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["profile"] }); setEditing(false); },
    onError: (err: Error) => { setUploadMessage({ type: "error", text: "Save failed: " + err.message }); },
  });

  const handleSave = () => mutation.mutate(form);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setUploadMessage(null);
    try {
      const result = await api.uploadFile<{ ingestion_id: string; status: string }>("/api/ingestion/resume/upload", file);
      setUploadMessage({ type: "success", text: `Resume uploaded! Ingestion ID: ${result.ingestion_id}` });
      setTimeout(() => setUploadMessage(null), 8000);
      // Reset file input
      e.target.value = "";
    } catch (err: unknown) {
      setUploadMessage({ type: "error", text: "Upload failed: " + (err instanceof Error ? err.message : "unknown error") });
    } finally {
      setUploading(false);
    }
  };

  if (!profile) return <p className="text-slate-500">Loading...</p>;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold">Career Profile</h1>
        <p className="text-slate-500 mt-1">Manage your professional identity</p>
      </div>

      <div className="bg-slate-900 rounded-lg shadow-sm border border-slate-700 p-6 space-y-4">
        <div className="flex justify-between items-center">
          <h2 className="font-semibold">Personal Information</h2>
          <button onClick={() => setEditing(!editing)} className="text-sm text-blue-400 hover:underline">
            {editing ? "Cancel" : "Edit"}
          </button>
        </div>

        {editing ? (
          <div className="space-y-3">
            {["full_name", "headline", "location", "email", "phone", "links"].map((field) => (
              <input key={field}
                type={field === "email" ? "email" : field === "links" ? "url" : "text"}
                placeholder={field.replace(/_/g, " ")}
                value={form[field]}
                onChange={(e) => setForm({ ...form, [field]: e.target.value })}
                className="w-full border border-slate-700 rounded px-3 py-2 text-sm bg-slate-800 text-slate-100"
              />
            ))}
            <textarea placeholder="Default summary" rows={4}
              value={form.default_summary}
              onChange={(e) => setForm({ ...form, default_summary: e.target.value })}
              className="w-full border border-slate-700 rounded px-3 py-2 text-sm bg-slate-800 text-slate-100"
            />
            <button onClick={handleSave} disabled={mutation.isPending}
              className="bg-blue-600 text-white px-4 py-2 rounded text-sm disabled:opacity-50">
              {mutation.isPending ? "Saving..." : "Save Profile"}
            </button>
          </div>
        ) : (
          <div className="space-y-2 text-sm text-slate-600">
            <p><span className="font-medium text-slate-700">Name:</span> {profile.full_name || <span className="text-slate-500 italic">Not set</span>}</p>
            <p><span className="font-medium text-slate-700">Headline:</span> {profile.headline || <span className="text-slate-500 italic">Not set</span>}</p>
            <p><span className="font-medium text-slate-700">Location:</span> {profile.location || <span className="text-slate-500 italic">Not set</span>}</p>
            <p><span className="font-medium text-slate-700">Email:</span> {profile.email || <span className="text-slate-500 italic">Not set</span>}</p>
            <p><span className="font-medium text-slate-700">Phone:</span> {profile.phone || <span className="text-slate-500 italic">Not set</span>}</p>
          </div>
        )}
      </div>

      <div className="bg-slate-900 rounded-lg shadow-sm border border-slate-700 p-6 space-y-4">
        <h2 className="font-semibold">Import from Existing Resume</h2>
        <p className="text-sm text-slate-500">Upload a PDF resume to extract positions, skills, and education.</p>
        {uploadMessage && (
          <div className={`text-sm p-3 rounded flex items-center justify-between ${uploadMessage.type === "success" ? "bg-green-950 text-green-400 border border-green-800" : "bg-red-950 text-red-400 border border-red-800"}`}>
            <span>{uploadMessage.text}</span>
            <button onClick={() => setUploadMessage(null)} className="ml-3 text-slate-500 hover:text-slate-300 font-bold">&times;</button>
          </div>
        )}
        <input type="file" accept=".pdf" onChange={handleUpload} disabled={uploading} className="text-sm" />
        {uploading && <p className="text-sm text-blue-400">Uploading and analyzing...</p>}
      </div>
    </div>
  );
}
