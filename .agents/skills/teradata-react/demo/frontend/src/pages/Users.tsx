import { PageShell } from "@/components/PageShell";
import { StateGate } from "@/components/StateGate";
import { DataTable } from "@/components/DataTable";
import { useUsers, type UserRow } from "@/lib/queries";

export default function Users() {
  const q = useUsers(200);
  return (
    <PageShell title="Users" subtitle="Recently created users (dbc.UsersV)">
      <StateGate
        q={q}
        isEmpty={(d) => d.length === 0}
        render={(rows) => (
          <DataTable<UserRow>
            rows={rows}
            columns={[
              { key: "username", header: "User" },
              { key: "ownername", header: "Owner" },
              {
                key: "createtimestamp",
                header: "Created",
                render: (r) =>
                  r.createtimestamp ? new Date(r.createtimestamp).toLocaleString() : "—",
              },
              {
                key: "lastaltertimestamp",
                header: "Last altered",
                render: (r) =>
                  r.lastaltertimestamp ? new Date(r.lastaltertimestamp).toLocaleString() : "—",
              },
            ]}
          />
        )}
      />
    </PageShell>
  );
}
