"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import PageHeader from "@/components/ui/page-header";
import { ListSkeleton } from "@/components/ui/skeleton";
import EmptyState from "@/components/ui/empty-state";
import { toast } from "@/components/ui/toast";

interface IngestionStatus {
  id: string;
  source_filename: string;
  status: string;
  error_message: string;
  created_at: string;
}

interface Candidate {
  id: string;
  entity_type: string;
  extracted_data: Record<string, unknown>;
  confidence: string;
  status: string;
  user_edits: Record<string, unknown> | null;
}

const ENTITY_LABELS: Record<string, string> = {
  user_profile: "Profile",
  position: "Positions",
  skill: "Skills",
  education: "Education",
  project: "Projects",
  certification: "Certifications",
  achievement: "Achievements",
  evidence: "Evidence",
  raw_markdown: "Raw Markdown",
  other: "Other",
};

const STATUS_COLORS: Record<string, string> = {
  accepted: "bg-emerald-900 text-emerald-400",
  rejected: "bg-red-900 text-red-400",
  pending: "bg-slate-800 text-slate-400",
  needs_review: "bg-amber-900 text-amber-400",
};

export default function IngestionReviewPage() {
  const params = useParams();
  const ingestionId = params.id as string;
  const queryClient = useQueryClient();

  const { data: ingestion, isLoading: ingestionLoading } = useQuery<IngestionStatus>({
    queryKey: ["ingestion", ingestionId],
    queryFn: () => api.get<IngestionStatus>(`/api/ingestion/resume/${ingestionId}`),
    enabled: !!ingestionId,
  });

  const { data: candidates, isLoading: candidatesLoading, error: candidatesError } = useQuery<Candidate[]>({
    queryKey: ["ingestion-candidates", ingestionId],
    queryFn: () => api.get<Candidate[]>(`/api/ingestion/resume/${ingestionId}/candidates`),
    enabled: !!ingestionId,
  });

  const acceptMutation = useMutation({
    mutationFn: ({ candidateId }: { candidateId: string }) =>
      api.post(`/api/ingestion/resume/${ingestionId}/candidates/${candidateId}/accept`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["ingestion-candidates", ingestionId] });
      toast("success", "Candidate accepted");
    },
    onError: (err: Error) => toast("error", err.message),
  });

  const rejectMutation = useMutation({
    mutationFn: ({ candidateId }: { candidateId: string }) =>
      api.post(`/api/ingestion/resume/${ingestionId}/candidates/${candidateId}/reject`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["ingestion-candidates", ingestionId] });
      toast("success", "Candidate rejected");
    },
    onError: (err: Error) => toast("error", err.message),
  });

  const importMutation = useMutation({
    mutationFn: () => api.post<{ imported_count: number; created_entity_ids: string[] }>(
      `/api/ingestion/resume/${ingestionId}/import`
    ),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["ingestion-candidates", ingestionId] });
      queryClient.invalidateQueries({ queryKey: ["ingestion", ingestionId] });
      toast("success", `Imported ${data.imported_count} candidates`);
    },
    onError: (err: Error) => toast("error", err.message),
  });

  // Group candidates by entity_type
  const grouped = (candidates || []).reduce<Record<string, Candidate[]>>((acc, c) => {
    const type = c.entity_type;
    if (!acc[type]) acc[type] = [];
    acc[type].push(c);
    return acc;
  }, {});

  const acceptedCount = (candidates || []).filter((c) => c.status === "accepted").length;
  const isLoading = ingestionLoading || candidatesLoading;

  return (
    <div className="space-y-8">
      <PageHeader
        title="Review Candidates"
        description={
          ingestion
            ? `Parsed from ${ingestion.source_filename} · Status: ${ingestion.status}`
            : "Review parsed resume data before importing"
        }
        actions={
          <div className="flex items-center gap-2">
            <Link
              href="/profile"
              className="text-sm text-slate-400 hover:text-slate-200 transition-colors"
            >
              ← Back to Profile
            </Link>
            {candidates && candidates.length > 0 && acceptedCount > 0 && (
              <button
                onClick={() => importMutation.mutate()}
                disabled={importMutation.isPending}
                className="bg-blue-600 text-white px-4 py-2 rounded text-sm hover:bg-blue-500 disabled:opacity-50 inline-flex items-center gap-2 transition-colors"
              >
                {importMutation.isPending && (
                  <span className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                )}
                {importMutation.isPending ? "Importing..." : `Import ${acceptedCount} Accepted`}
              </button>
            )}
          </div>
        }
      />

      {isLoading ? (
        <ListSkeleton rows={6} />
      ) : candidatesError ? (
        <div className="bg-red-950 text-red-400 text-sm p-4 rounded-lg border border-red-800">
          Failed to load candidates. The ingestion may have no parsed data yet.
        </div>
      ) : !candidates || candidates.length === 0 ? (
        <EmptyState
          title="No candidates found"
          description={
            ingestion?.status === "processing"
              ? "The file is still being processed. Check back in a moment."
              : "No parsed sections were found in the uploaded file. Make sure your markdown resume uses ## section headers."
          }
          action={{ label: "Upload Another File", onClick: () => window.location.href = "/profile" }}
        />
      ) : (
        <>
          {/* Summary bar */}
          <div className="bg-slate-900 rounded-lg border border-slate-700 p-4 flex items-center gap-6 text-sm">
            <div className="text-slate-400">
              <span className="font-medium text-slate-200">{candidates.length}</span> total candidates
            </div>
            <div className="text-slate-400">
              <span className="font-medium text-emerald-400">{acceptedCount}</span> accepted
            </div>
            <div className="text-slate-400">
              <span className="font-medium text-red-400">{candidates.filter((c) => c.status === "rejected").length}</span> rejected
            </div>
            <div className="text-slate-400">
              <span className="font-medium text-amber-400">{candidates.filter((c) => c.status === "pending").length}</span> pending review
            </div>
          </div>

          {/* Grouped candidate sections */}
          <div className="space-y-6">
            {Object.entries(grouped).map(([entityType, items]) => (
              <div key={entityType} className="bg-slate-900 rounded-lg border border-slate-700 p-6">
                <h2 className="font-semibold text-slate-200 mb-4 flex items-center gap-2">
                  {ENTITY_LABELS[entityType] || entityType}
                  <span className="text-xs text-slate-500 font-normal">({items.length})</span>
                </h2>
                <div className="space-y-3">
                  {items.map((candidate) => (
                    <div
                      key={candidate.id}
                      className={`p-4 rounded-lg border ${
                        candidate.status === "accepted"
                          ? "border-emerald-800 bg-emerald-950/30"
                          : candidate.status === "rejected"
                          ? "border-red-800 bg-red-950/30"
                          : "border-slate-800 bg-slate-800/30"
                      }`}
                    >
                      {/* Entity-specific display */}
                      {entityType === "user_profile" && (
                        <div className="text-sm text-slate-300 whitespace-pre-wrap">
                          {candidate.extracted_data?.content as string || JSON.stringify(candidate.extracted_data, null, 2)}
                        </div>
                      )}
                      {entityType === "position" && (
                        <div className="space-y-1">
                          <p className="text-sm font-medium text-slate-200">
                            {candidate.extracted_data?.header as string || "Position"}
                          </p>
                          <pre className="text-xs text-slate-400 whitespace-pre-wrap font-sans">
                            {candidate.extracted_data?.content as string || ""}
                          </pre>
                        </div>
                      )}
                      {entityType === "skill" && (
                        <div>
                          <p className="text-sm text-slate-300 whitespace-pre-wrap">
                            {candidate.extracted_data?.content as string || ""}
                          </p>
                        </div>
                      )}
                      {entityType === "education" && (
                        <div className="space-y-1">
                          <p className="text-sm font-medium text-slate-200">
                            {candidate.extracted_data?.header as string || "Education"}
                          </p>
                          <pre className="text-xs text-slate-400 whitespace-pre-wrap font-sans">
                            {candidate.extracted_data?.content as string || ""}
                          </pre>
                        </div>
                      )}
                      {entityType === "project" && (
                        <div className="space-y-1">
                          <p className="text-sm font-medium text-slate-200">
                            {candidate.extracted_data?.header as string || "Project"}
                          </p>
                          <pre className="text-xs text-slate-400 whitespace-pre-wrap font-sans">
                            {candidate.extracted_data?.content as string || ""}
                          </pre>
                        </div>
                      )}
                      {entityType === "certification" && (
                        <div className="space-y-1">
                          <p className="text-sm font-medium text-slate-200">
                            {candidate.extracted_data?.header as string || "Certification"}
                          </p>
                          <pre className="text-xs text-slate-400 whitespace-pre-wrap font-sans">
                            {candidate.extracted_data?.content as string || ""}
                          </pre>
                        </div>
                      )}
                      {entityType === "achievement" && (
                        <div className="space-y-1">
                          <p className="text-sm font-medium text-slate-200">
                            {candidate.extracted_data?.header as string || "Achievement"}
                          </p>
                          <pre className="text-xs text-slate-400 whitespace-pre-wrap font-sans">
                            {candidate.extracted_data?.content as string || ""}
                          </pre>
                        </div>
                      )}
                      {entityType === "evidence" && (
                        <div className="text-sm text-slate-300 whitespace-pre-wrap">
                          {candidate.extracted_data?.content as string || ""}
                        </div>
                      )}
                      {entityType === "raw_markdown" && (
                        <details>
                          <summary className="text-xs text-slate-500 cursor-pointer hover:text-slate-400">
                            View raw markdown
                          </summary>
                          <pre className="mt-2 text-xs text-slate-400 whitespace-pre-wrap max-h-64 overflow-auto">
                            {(candidate.extracted_data?.content as string)?.substring(0, 2000) || ""}
                          </pre>
                        </details>
                      )}
                      {!Object.keys(ENTITY_LABELS).includes(entityType) && (
                        <pre className="text-xs text-slate-400 whitespace-pre-wrap font-sans">
                          {JSON.stringify(candidate.extracted_data, null, 2)}
                        </pre>
                      )}

                      {/* Confidence + status */}
                      <div className="flex items-center gap-2 mt-3">
                        <span className={`text-xs px-2 py-0.5 rounded-full ${STATUS_COLORS[candidate.status] || STATUS_COLORS.pending}`}>
                          {candidate.status.replace(/_/g, " ")}
                        </span>
                        <span className="text-xs text-slate-500">
                          confidence: {candidate.confidence}
                        </span>
                      </div>

                      {/* Actions */}
                      {candidate.status !== "accepted" && candidate.entity_type !== "raw_markdown" && (
                        <div className="flex items-center gap-2 mt-2">
                          <button
                            onClick={() => acceptMutation.mutate({ candidateId: candidate.id })}
                            disabled={acceptMutation.isPending}
                            className="text-xs text-emerald-400 hover:bg-emerald-950 px-2 py-1 rounded transition-colors disabled:opacity-50"
                          >
                            Accept
                          </button>
                          {candidate.status !== "rejected" && (
                            <button
                              onClick={() => rejectMutation.mutate({ candidateId: candidate.id })}
                              disabled={rejectMutation.isPending}
                              className="text-xs text-red-400 hover:bg-red-950 px-2 py-1 rounded transition-colors disabled:opacity-50"
                            >
                              Reject
                            </button>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
