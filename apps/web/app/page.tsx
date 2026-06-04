"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { Profile, PaginatedResponse, Resume } from "@/lib/types";

export default function DashboardPage() {
  const { data: profile, error: profileError } = useQuery<Profile>({
    queryKey: ["profile"],
    queryFn: () => api.get<Profile>("/api/profile"),
  });

  const { data: resumes, error: resumesError } = useQuery<PaginatedResponse<Resume>>({
    queryKey: ["resumes"],
    queryFn: () => api.get<PaginatedResponse<Resume>>("/api/resumes?limit=5"),
  });

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="text-zinc-500 mt-1">Your career command center</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <QuickActionCard title="Paste a JD" href="/jd" desc="Start resume generation" />
        <QuickActionCard title="Upload Resume PDF" href="/profile" desc="Extract career data from existing resume" />
        <QuickActionCard title="New Resume" href="/resumes" desc="Create a targeted resume" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg border border-zinc-200 p-6">
          <h2 className="font-semibold mb-4">Profile Overview</h2>
          {profileError ? (
            <p className="text-sm text-red-600">Failed to load profile</p>
          ) : profile ? (
            <div className="space-y-2 text-sm text-zinc-600">
              <p><span className="font-medium">Name:</span> {profile.full_name || "Not set"}</p>
              <p><span className="font-medium">Headline:</span> {profile.headline || "Not set"}</p>
              <p><span className="font-medium">Location:</span> {profile.location || "Not set"}</p>
            </div>
          ) : (
            <p className="text-sm text-zinc-400">Loading profile...</p>
          )}
        </div>
        <div className="bg-white rounded-lg border border-zinc-200 p-6">
          <h2 className="font-semibold mb-4">Recent Resumes</h2>
          {resumesError ? (
            <p className="text-sm text-red-600">Failed to load resumes</p>
          ) : resumes?.items?.length ? (
            <ul className="space-y-2">
              {resumes.items.map((r: Resume) => (
                <li key={r.id} className="text-sm flex justify-between">
                  <span>{r.title}</span>
                  <span className="text-zinc-400 capitalize">{r.status}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-zinc-400">No resumes yet. Create one to get started.</p>
          )}
        </div>
      </div>
    </div>
  );
}

function QuickActionCard({ title, href, desc }: { title: string; href: string; desc: string }) {
  return (
    <a href={href} className="block bg-white rounded-lg border border-zinc-200 p-5 hover:border-zinc-300 hover:shadow-sm transition-all">
      <h3 className="font-semibold text-sm">{title}</h3>
      <p className="text-xs text-zinc-500 mt-1">{desc}</p>
    </a>
  );
}
