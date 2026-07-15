import type { ReactNode } from "react";

export function PageShell({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle?: string;
  children: ReactNode;
}) {
  return (
    <main className="flex-1 p-8 overflow-auto">
      <header className="mb-6">
        <h1 className="text-3xl font-semibold text-brand-navy tracking-tight">{title}</h1>
        {subtitle && <p className="mt-1 text-brand-muted">{subtitle}</p>}
      </header>
      <div className="space-y-6">{children}</div>
    </main>
  );
}
