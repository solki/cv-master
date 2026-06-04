"use client";

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { api } from "@/lib/api";
import type { Resume, ResumeVersion, PaginatedResponse } from "@/lib/types";
import PageHeader from "@/components/ui/page-header";
import { ListSkeleton } from "@/components/ui/skeleton";
import EmptyState from "@/components/ui/empty-state";
import { LibraryIcon } from "@/components/icons";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function ResumeLibraryPage() {
  const { data, isLoading, error } = useQuery<PaginatedResponse<Resume>>({
    queryKey: ["library-resumes"],
    queryFn: () => api.get<PaginatedResponse<Resume>>("/api/resumes?limit=50"),
  });

  return (
    <div className="space-y-8">
      <PageHeader
        title="Resume Library"
        description="Browse and manage your generated resumes"
      />

      <div className="bg-slate-900 rounded-lg border border-slate-700 p-6">
        {error ? (
          <p className="text-sm text-red-400">Failed to load resumes</p>
        ) : isLoading ? (
          <ListSkeleton rows={5} />
        ) : data?.items?.length ? (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-slate-400 border-b border-slate-800">
                <th className="pb-2 font-medium">Title</th>
                <th className="pb-2 font-medium">Target Role</th>
                <th className="pb-2 font-medium">Status</th>
                <th className="pb-2 font-medium">Date</th>
                <th className="pb-2 font-medium w-28"></th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((r: Resume) => (
                <ResumeRow key={r.id} resume={r} />
              ))}
            </tbody>
          </table>
        ) : (
          <EmptyState
            icon={<LibraryIcon className="w-5 h-5" />}
            title="No resumes yet"
            description="Generate your first resume from the Resume Generator page to see it here."
            action={{ label: "Create Resume", onClick: () => window.location.href = "/resumes" }}
          />
        )}
      </div>
    </div>
  );
}

function ResumeRow({ resume }: { resume: Resume }) {
  const [exporting, setExporting] = useState(false);

  const { data: versions } = useQuery<ResumeVersion[]>({
    queryKey: ["resume-versions", resume.id],
    queryFn: () => api.get<ResumeVersion[]>(`/api/resumes/${resume.id}/versions`),
    enabled: exporting,
  });

  const handleExport = async () => {
    setExporting(true);
  };

  // Once versions are loaded, open the export URL
  if (exporting && versions !== undefined) {
    if (versions.length > 0) {
      const latestVersion = versions[0]; // versions are sorted by version_number desc
      const exportUrl = `${API_BASE}/api/exports/export_${latestVersion.id}:markdown/download`;
      window.open(exportUrl, "_blank");
    }
    setExporting(false);
  }

  const handleGenerateAndExport = async () => {
    setExporting(true);
    try {
      // First, trigger generation to create a version
      await api.post(`/api/resumes/${resume.id}/generate`, {
        job_description_id: resume.job_description_id || "",
      });
      // Small delay to let the backend create the version
      setTimeout(() => {
        // Fetch versions after generation
        api.get<ResumeVersion[]>(`/api/resumes/${resume.id}/versions`).then((vers) => {
          if (vers.length > 0) {
            const latestVersion = vers[0];
            const exportUrl = `${API_BASE}/api/exports/export_${latestVersion.id}:markdown/download`;
            window.open(exportUrl, "_blank");
          }
          setExporting(false);
        }).catch(() => setExporting(false));
      }, 500);
    } catch {
      setExporting(false);
    }
  };

  return (
    <tr className="border-b border-slate-800 group">
      <td className="py-2 font-medium text-slate-200">{resume.title}</td>
      <td className="py-2 text-slate-400">{resume.target_role || "—"}</td>
      <td className="py-2">
        <span className={`text-xs px-2 py-0.5 rounded-full ${resume.status === "approved" ? "bg-emerald-900 text-emerald-400" : "bg-slate-800 text-slate-400"}`}>
          {resume.status}
        </span>
      </td>
      <td className="py-2 text-slate-500">{new Date(resume.created_at).toLocaleDateString()}</td>
      <td className="py-2">
        <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            onClick={handleGenerateAndExport}
            disabled={exporting}
            className="text-xs text-blue-400 hover:text-blue-300 transition-colors disabled:opacity-50"
            title="Generate version and download Markdown"
          >
            {exporting ? "..." : "Generate & Export"}
          </button>
          <button
            onClick={handleExport}
            disabled={exporting}
            className="text-xs text-slate-400 hover:text-slate-300 transition-colors disabled:opacity-50"
            title="Export existing latest version"
          >
            Export
          </button>
        </div>
      </td>
    </tr>
  );
}
