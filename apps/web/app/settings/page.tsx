"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { HealthResponse, LLMHealthResponse } from "@/lib/types";

export default function SettingsPage() {
  const { data: health, error: healthError } = useQuery<HealthResponse>({ queryKey: ["health"], queryFn: () => api.get<HealthResponse>("/health") });
  const { data: llmHealth, error: llmError } = useQuery<LLMHealthResponse>({ queryKey: ["llm-health"], queryFn: () => api.get<LLMHealthResponse>("/health/llm") });

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold">Settings</h1>
        <p className="text-zinc-500 mt-1">System configuration and status</p>
      </div>

      {(healthError || llmError) && (
        <div className="bg-red-50 text-red-700 text-sm p-3 rounded border border-red-200">
          Failed to load system status. Check that the API is running.
        </div>
      )}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <StatusCard title="System Health" status={healthError ? "error" : health?.status === "ok" ? "healthy" : "error"}>
          <p className="text-sm text-zinc-600">Environment: {health?.environment || "N/A"}</p>
          <p className="text-sm text-zinc-600">Database: {health?.database?.status || "N/A"}</p>
        </StatusCard>
        <StatusCard title="LLM Provider" status={llmError ? "error" : llmHealth?.llm?.configured ? "configured" : "not configured"}>
          <p className="text-sm text-zinc-600">Provider: {llmHealth?.llm?.provider || "N/A"}</p>
          <p className="text-sm text-zinc-600">Search (Tavily): {llmHealth?.search?.configured ? "configured" : "not configured"}</p>
        </StatusCard>
      </div>

      <div className="bg-white rounded-lg border border-zinc-200 p-6 space-y-3">
        <h2 className="font-semibold">Configuration</h2>
        <p className="text-sm text-zinc-500">
          LLM provider, API keys, and search configuration are managed via environment variables.
          See <code className="text-xs bg-zinc-100 px-1 rounded">.env.example</code> for all available options.
        </p>
        <p className="text-sm text-zinc-500">
          Set <code className="text-xs bg-zinc-100 px-1 rounded">LLM_PROVIDER</code> to one of:
          openai_compatible, openai, anthropic, or ollama.
        </p>
      </div>
    </div>
  );
}

function StatusCard({ title, status, children }: { title: string; status: string; children: React.ReactNode }) {
  const color = status === "healthy" || status === "configured" ? "green" : status === "error" ? "red" : "yellow";
  const colorMap: Record<string, string> = {
    green: "bg-green-50 border-green-200", red: "bg-red-50 border-red-200", yellow: "bg-yellow-50 border-yellow-200",
  };
  const dotMap: Record<string, string> = {
    green: "bg-green-500", red: "bg-red-500", yellow: "bg-yellow-500",
  };
  return (
    <div className={`rounded-lg border p-6 space-y-3 ${colorMap[color] || colorMap.yellow}`}>
      <div className="flex items-center gap-2">
        <span className={`w-2 h-2 rounded-full ${dotMap[color] || dotMap.yellow}`} />
        <h2 className="font-semibold text-sm">{title}</h2>
        <span className="text-xs text-zinc-500 capitalize">({status})</span>
      </div>
      {children}
    </div>
  );
}
