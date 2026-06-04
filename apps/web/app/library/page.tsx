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
        <p className="text-zinc-500 mt-1">Browse and manage your generated resumes</p>
      </div>

      <div className="bg-white rounded-lg border border-zinc-200 p-6">
        {error ? (
          <p className="text-sm text-red-600">Failed to load resumes</p>
        ) : isLoading ? <p className="text-zinc-400 text-sm">Loading...</p> :
          data?.items?.length ? (
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-zinc-500 border-b border-zinc-100">
                  <th className="pb-2 font-medium">Title</th>
                  <th className="pb-2 font-medium">Target Role</th>
                  <th className="pb-2 font-medium">Status</th>
                  <th className="pb-2 font-medium">Date</th>
                </tr>
              </thead>
              <tbody>
                {data.items.map((r: Resume) => (
                  <tr key={r.id} className="border-b border-zinc-50">
                    <td className="py-2 font-medium">{r.title}</td>
                    <td className="py-2 text-zinc-600">{r.target_role}</td>
                    <td className="py-2">
                      <span className={`text-xs px-2 py-0.5 rounded ${r.status === "approved" ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"}`}>
                        {r.status}
                      </span>
                    </td>
                    <td className="py-2 text-zinc-400">{new Date(r.created_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : <p className="text-sm text-zinc-400">No resumes in library yet.</p>
        }
      </div>
    </div>
  );
}
