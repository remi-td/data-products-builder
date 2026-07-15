import type { ReactNode } from "react";

export function PageShell({ title, children }: { title: string; children: ReactNode }) {
  return (
    <main className="flex-1 p-6 overflow-auto">
      <h1 className="text-2xl font-semibold text-brand-navy mb-4">{title}</h1>
      <div className="space-y-6">{children}</div>
    </main>
  );
}
