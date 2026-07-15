import { BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";
import { PageShell } from "@/components/PageShell";
import { StateGate } from "@/components/StateGate";
import { Kpi } from "@/components/Kpi";
import { ChartCard } from "@/components/ChartCard";
import { useOverview, useSpaceByDatabase } from "@/lib/queries";
import { formatBytes, formatInt } from "@/lib/api";

export default function Overview() {
  const o = useOverview();
  const s = useSpaceByDatabase(10);

  return (
    <PageShell
      title="Vantage Overview"
      subtitle="High-level system metrics sourced from dbc system views"
    >
      <StateGate
        q={o}
        render={(d) => (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <Kpi label="Databases" value={formatInt(d.database_count)} />
            <Kpi label="Tables / Views" value={formatInt(d.table_count)} />
            <Kpi label="Users" value={formatInt(d.user_count)} />
            <Kpi label="Total perm space" value={formatBytes(d.total_perm_bytes)} accent />
          </div>
        )}
      />

      <StateGate
        q={s}
        isEmpty={(d) => d.length === 0}
        render={(rows) => (
          <ChartCard
            title="Top 10 databases by current perm space"
            subtitle="dbc.DiskSpaceV, summed per database"
          >
            <BarChart data={rows} margin={{ top: 10, right: 16, left: 8, bottom: 60 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.08)" />
              <XAxis
                dataKey="databasename"
                angle={-30}
                textAnchor="end"
                interval={0}
                height={70}
                tick={{ fontSize: 11 }}
              />
              <YAxis tickFormatter={(v) => formatBytes(Number(v))} width={90} tick={{ fontSize: 11 }} />
              <Tooltip formatter={(v) => formatBytes(Number(v))} />
              <Bar dataKey="currentperm" fill="var(--chart-1)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ChartCard>
        )}
      />
    </PageShell>
  );
}
