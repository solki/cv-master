interface SkeletonProps {
  className?: string;
}

export function Skeleton({ className = "" }: SkeletonProps) {
  return (
    <div className={`animate-pulse bg-slate-800 rounded ${className}`} />
  );
}

export function CardSkeleton() {
  return (
    <div className="bg-slate-900 rounded-lg border border-slate-700 p-6 space-y-4">
      <Skeleton className="h-4 w-1/3" />
      <Skeleton className="h-3 w-full" />
      <Skeleton className="h-3 w-2/3" />
    </div>
  );
}

export function ListSkeleton({ rows = 5 }: { rows?: number }) {
  return (
    <div className="bg-slate-900 rounded-lg border border-slate-700 p-6 space-y-3">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex items-center gap-4 py-2 border-b border-slate-800 last:border-0">
          <Skeleton className="h-3 flex-1" />
          <Skeleton className="h-3 w-24" />
        </div>
      ))}
    </div>
  );
}

export function FormSkeleton({ fields = 5 }: { fields?: number }) {
  return (
    <div className="bg-slate-900 rounded-lg border border-slate-700 p-6 space-y-4">
      {Array.from({ length: fields }).map((_, i) => (
        <div key={i} className="space-y-2">
          <Skeleton className="h-3 w-20" />
          <Skeleton className="h-10 w-full" />
        </div>
      ))}
    </div>
  );
}
