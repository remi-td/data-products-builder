import type { ReactNode } from "react";
import type { UseQueryResult } from "@tanstack/react-query";

type Props<T> = {
  q: UseQueryResult<T>;
  empty?: ReactNode;
  isEmpty?: (data: T) => boolean;
  render: (data: T) => ReactNode;
};

export function StateGate<T>({ q, empty = "No data.", isEmpty, render }: Props<T>) {
  if (q.isLoading) return <div className="animate-pulse text-brand-muted">Loading…</div>;
  if (q.isError) {
    return (
      <div className="rounded border border-red-300 bg-red-50 p-4 text-red-900">
        <div className="font-medium">Failed to load</div>
        <div className="text-sm">{(q.error as Error).message}</div>
        <button
          className="mt-2 rounded bg-red-600 px-3 py-1 text-white text-sm"
          onClick={() => q.refetch()}
        >
          Retry
        </button>
      </div>
    );
  }
  if (q.data === undefined) return null;
  if (isEmpty && isEmpty(q.data)) return <div className="text-brand-muted">{empty}</div>;
  return <>{render(q.data)}</>;
}
