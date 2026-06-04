export default function VaultPage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold">Knowledge Vault</h1>
        <p className="text-zinc-500 mt-1">Local Markdown career notes</p>
      </div>
      <div className="bg-white rounded-lg border border-zinc-200 p-6">
        <h2 className="font-semibold mb-4">Vault Structure</h2>
        <div className="space-y-2 text-sm text-zinc-600">
          <VaultItem path="profile.md" desc="User profile information" />
          <VaultItem path="work/" desc="Work experience records" />
          <VaultItem path="projects/" desc="Project records" />
          <VaultItem path="education/" desc="Education records" />
          <VaultItem path="certifications/" desc="Certification records" />
          <VaultItem path="skills/" desc="Skill records" />
          <VaultItem path="stories/" desc="STAR stories and narrative events" />
          <VaultItem path="evidence/" desc="Supporting evidence notes" />
        </div>
        <p className="text-xs text-zinc-400 mt-6">
          The vault syncs structured Postgres data to human-readable Markdown files.
          Each file includes stable frontmatter IDs linking back to database records.
        </p>
      </div>
    </div>
  );
}

function VaultItem({ path, desc }: { path: string; desc: string }) {
  return (
    <div className="flex gap-3 items-start">
      <code className="text-xs bg-zinc-100 px-2 py-0.5 rounded font-mono">{path}</code>
      <span className="text-zinc-500">{desc}</span>
    </div>
  );
}
