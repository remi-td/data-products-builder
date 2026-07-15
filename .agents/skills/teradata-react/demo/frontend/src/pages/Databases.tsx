import { PageShell } from "@/components/PageShell";
import { StateGate } from "@/components/StateGate";
import { DataTable } from "@/components/DataTable";
import { useDatabases, type DatabaseRow } from "@/lib/queries";
import { formatBytes } from "@/lib/api";

export default function Databases() {
  const q = useDatabases(200);
  return (
    <PageShell title="Databases" subtitle="Top 200 databases by allocated perm space">
      <StateGate
        q={q}
        isEmpty={(d) => d.length === 0}
        render={(rows) => (
          <DataTable<DatabaseRow>
            rows={rows}
            columns={[
              { key: "databasename", header: "Database" },
              { key: "ownername", header: "Owner" },
              {
                key: "permspace",
                header: "Perm",
                align: "right",
                render: (r) => formatBytes(r.permspace),
              },
              {
                key: "spoolspace",
                header: "Spool",
                align: "right",
                render: (r) => formatBytes(r.spoolspace),
              },
              {
                key: "tempspace",
                header: "Temp",
                align: "right",
                render: (r) => formatBytes(r.tempspace),
              },
            ]}
          />
        )}
      />
    </PageShell>
  );
}
