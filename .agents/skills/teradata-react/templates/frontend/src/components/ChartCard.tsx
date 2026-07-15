import type { ReactNode } from "react";
import { ResponsiveContainer } from "recharts";

export function ChartCard({
  title,
  subtitle,
  height = 320,
  children,
}: {
  title: string;
  subtitle?: string;
  height?: number;
  children: ReactNode;
}) {
  return (
    <section className="rounded-lg border border-black/5 bg-white shadow-sm p-4">
      <header className="mb-2">
        <h2 className="text-sm font-semibold text-brand-navy">{title}</h2>
        {subtitle && <p className="text-xs text-brand-muted">{subtitle}</p>}
      </header>
      <div style={{ width: "100%", height }}>
        <ResponsiveContainer>{children as React.ReactElement}</ResponsiveContainer>
      </div>
    </section>
  );
}
