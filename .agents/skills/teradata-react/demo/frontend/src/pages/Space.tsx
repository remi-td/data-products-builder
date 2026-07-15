import { BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, Legend } from "recharts";
import { PageShell } from "@/components/PageShell";
import { StateGate } from "@/components/StateGate";
import { ChartCard } from "@/components/ChartCard";
import { DataTable } from "@/components/DataTable";
import { useSpaceByDatabase, type SpaceByDatabase } from "@/lib/queries";
import { formatBytes } from "@/lib/api";

export default function Space() {
  const q = useSpaceByDatabase(20);
  return (
    <PageShell title="Disk Space" subtitle="Top 20 databases by current and max perm">
      <StateGate
        q={q}
        isEmpty={(d) => d.length === 0}
        render={(rows) => (
          <>
            <ChartCard
              title="Current vs. max perm space"
              subtitle="Headroom indicator per database"
              height={400}
            >
              <BarChart data={rows} margin={{ top: 10, right: 16, left: 8, bottom: 80 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.08)" />
                <XAxis
                  dataKey="databasename"
                  angle={-35}
                  textAnchor="end"
                  interval={0}
                  height={90}
                  tick={{ fontSize: 11 }}
                />
                <YAxis tickFormatter={(v) => formatBytes(Number(v))} width={90} tick={{ fontSize: 11 }} />
                <Tooltip formatter={(v) => formatBytes(Number(v))} />
                <Legend />
                <Bar dataKey="currentperm" name="Current" fill="var(--chart-1)" />
                <Bar dataKey="maxperm" name="Max" fill="var(--chart-2)" />
              </BarChart>
            </ChartCard>
            <DataTable<SpaceByDatabase>
              rows={rows}
              columns={[
                { key: "databasename", header: "Database" },
                {
                  key: "currentperm",
                  header: "Current",
                  align: "right",
                  render: (r) => formatBytes(r.currentperm),
                },
                {
                  key: "maxperm",
                  header: "Max",
                  align: "right",
                  render: (r) => formatBytes(r.maxperm),
                },
              ]}
            />
          </>
        )}
      />
    </PageShell>
  );
}
