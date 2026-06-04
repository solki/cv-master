"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { Resume, PaginatedResponse } from "@/lib/types";
import PageHeader from "@/components/ui/page-header";
import { ListSkeleton } from "@/components/ui/skeleton";
import EmptyState from "@/components/ui/empty-state";
import { LibraryIcon } from "@/components/icons";

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
                <th className="pb-2 font-medium w-10"></th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((r: Resume) => (
                <tr key={r.id} className="border-b border-slate-800 group">
                  <td className="py-2 font-medium text-slate-200">{r.title}</td>
                  <td className="py-2 text-slate-400">{r.target_role || "—"}</td>
                  <td className="py-2">
                    <span className={`text-xs px-2 py-0.5 rounded-full ${r.status === "approved" ? "bg-emerald-900 text-emerald-400" : "bg-slate-800 text-slate-400"}`}>
                      {r.status}
                    </span>
                  </td>
                  <td className="py-2 text-slate-500">{new Date(r.created_at).toLocaleDateString()}</td>
                  <td className="py-2">
                    <button
                      onClick={() => {
                        const exportUrl = `http://localhost:8000/api/exports/export_${r.id}_v1_markdown/download`;
                        window.open(exportUrl, "_blank");
                      }}
                      className="opacity-0 group-hover:opacity-100 text-xs text-blue-400 hover:text-blue-300 transition-all"
                      title="Download Markdown"
                    >
                      Export
                    </button>
                  </td>
                </tr>
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
