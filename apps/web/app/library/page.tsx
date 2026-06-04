"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { Resume, PaginatedResponse } from "@/lib/types";

export default function ResumeLibraryPage() {
  const { data, isLoading, error } = useQuery<PaginatedResponse<Resume>>({
    queryKey: ["library-resumes"],
    queryFn: () => api.get<PaginatedResponse<Resume>>("/api/resumes?limit=50"),
  });

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold">Resume Library</h1>
        <p className="text-slate-500 mt-1">Browse and manage your generated resumes</p>
      </div>

      <div className="bg-slate-900 rounded-lg shadow-sm border border-slate-700 p-6">
        {error ? (
          <p className="text-sm text-red-400">Failed to load resumes</p>
        ) : isLoading ? <p className="text-slate-500 text-sm">Loading...</p> :
          data?.items?.length ? (
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-slate-500 border-b border-slate-800">
                  <th className="pb-2 font-medium">Title</th>
                  <th className="pb-2 font-medium">Target Role</th>
                  <th className="pb-2 font-medium">Status</th>
                  <th className="pb-2 font-medium">Date</th>
                </tr>
              </thead>
              <tbody>
                {data.items.map((r: Resume) => (
                  <tr key={r.id} className="border-b border-slate-800">
                    <td className="py-2 font-medium text-slate-200">{r.title}</td>
                    <td className="py-2 text-slate-400">{r.target_role}</td>
                    <td className="py-2">
                      <span className={`text-xs px-2 py-0.5 rounded ${r.status === "approved" ? "bg-green-900 text-green-400" : "bg-yellow-900 text-yellow-400"}`}>
                        {r.status}
                      </span>
                    </td>
                    <td className="py-2 text-slate-500">{new Date(r.created_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : <p className="text-sm text-slate-500">No resumes in library yet.</p>
        }
      </div>
    </div>
  );
}
