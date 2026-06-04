import PageHeader from "@/components/ui/page-header";
import { VaultIcon } from "@/components/icons";

export default function VaultPage() {
  return (
    <div className="space-y-8">
      <PageHeader
        title="Knowledge Vault"
        description="Local Markdown career notes synced from your profile data"
      />
      <div className="bg-slate-900 rounded-lg border border-slate-700 p-6">
        <h2 className="font-semibold text-slate-200 mb-4">Vault Structure</h2>
        <div className="space-y-2 text-sm">
          <VaultItem path="profile.md" desc="User profile information" />
          <VaultItem path="work/" desc="Work experience records" />
          <VaultItem path="projects/" desc="Project records" />
          <VaultItem path="education/" desc="Education records" />
          <VaultItem path="certifications/" desc="Certification records" />
          <VaultItem path="skills/" desc="Skill records" />
          <VaultItem path="stories/" desc="STAR stories and narrative events" />
          <VaultItem path="evidence/" desc="Supporting evidence notes" />
        </div>
        <p className="text-xs text-slate-500 mt-6 border-t border-slate-800 pt-4">
          Each file includes stable frontmatter IDs linking back to database records.
          The vault mirrors your structured Postgres data as editable Markdown.
        </p>
      </div>
    </div>
  );
}

function VaultItem({ path, desc }: { path: string; desc: string }) {
  return (
    <div className="flex gap-3 items-start py-1.5">
      <code className="text-xs bg-slate-800 px-2 py-0.5 rounded font-mono text-slate-300 flex-shrink-0">{path}</code>
      <span className="text-slate-400">{desc}</span>
    </div>
  );
}
