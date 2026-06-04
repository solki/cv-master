import type { ReactNode } from "react";

interface EmptyStateProps {
  icon?: ReactNode;
  title: string;
  description: string;
  action?: { label: string; onClick: () => void };
}

export default function EmptyState({ icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12 px-4 text-center">
      {icon && (
        <div className="w-12 h-12 rounded-full bg-slate-800 flex items-center justify-center text-slate-500 mb-4">
          {icon}
        </div>
      )}
      <h3 className="text-sm font-medium text-slate-300 mb-1">{title}</h3>
      <p className="text-sm text-slate-500 max-w-sm">{description}</p>
      {action && (
        <button
          onClick={action.onClick}
          className="mt-4 bg-blue-600 text-white px-4 py-2 rounded text-sm hover:bg-blue-500 transition-colors"
        >
          {action.label}
        </button>
      )}
    </div>
  );
}
