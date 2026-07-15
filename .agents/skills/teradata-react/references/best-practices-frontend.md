# Frontend Best Practices (React + Vite + TS)

Read this before writing or reviewing frontend code. Patterns are
expressed for the stack in `templates/frontend/`.

## Stack rationale

- **Vite** — fastest dev server, native ESM, agent-friendly output.
- **TypeScript** — catches schema/API drift at compile time.
- **Tailwind CSS** — utility-first, brandable via tokens, no
  component-library lock-in.
- **shadcn/ui** (optional, copy-in components) — accessible primitives
  without runtime dependency.
- **React Router** — file-agnostic, well understood by agents.
- **TanStack Query (React Query)** — cache, dedupe, retry, stale-time.
- **Recharts** — declarative charts, React-native, sane defaults.

Do not mix in Redux/Zustand for server state — React Query owns that.
Use local `useState`/`useReducer` for UI state only.

## API client

One typed wrapper. Throws on non-2xx so React Query can retry.

```ts
// src/lib/api.ts
const BASE = import.meta.env.VITE_API_URL ?? "/api";

export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "content-type": "application/json", ...(init?.headers ?? {}) },
    ...init,
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return (await res.json()) as T;
}
```

## Hooks per endpoint

```ts
// src/lib/queries.ts
import { useQuery } from "@tanstack/react-query";
import { api } from "./api";

export type TableRow = {
  databasename: string; tablename: string;
  tablekind: string;   createtimestamp: string;
};

export function useTablesByDatabase(database: string) {
  return useQuery({
    queryKey: ["tables", database],
    queryFn: () => api<TableRow[]>(`/tables?database=${encodeURIComponent(database)}`),
    enabled: database.length > 0,
    staleTime: 60_000,
  });
}
```

**Rules:**
- `queryKey` mirrors endpoint + params. Stable keys are the basis of
  caching.
- `staleTime` ≥ server cache TTL. Avoids re-fetch storms.
- `enabled` guards dependent queries.

## Pages compose, components render

```tsx
// src/pages/Tables.tsx
export default function TablesPage() {
  const [db, setDb] = useState("DBC");
  const q = useTablesByDatabase(db);
  return (
    <PageShell title="Tables">
      <DatabasePicker value={db} onChange={setDb} />
      {q.isLoading ? <Skeleton rows={10} />
        : q.isError ? <ErrorPanel error={q.error} retry={q.refetch} />
        : <DataTable rows={q.data ?? []} />}
    </PageShell>
  );
}
```

The page never calls `fetch`. The component never knows where data
came from.

## Loading, empty, error — always three states

Every data view handles three states. Make them components, not inline:

```tsx
function StateGate<T>({ q, empty, render }: {
  q: UseQueryResult<T[]>;
  empty: ReactNode;
  render: (rows: T[]) => ReactNode;
}) {
  if (q.isLoading) return <Skeleton />;
  if (q.isError) return <ErrorPanel error={q.error} retry={q.refetch} />;
  if (!q.data || q.data.length === 0) return <>{empty}</>;
  return <>{render(q.data)}</>;
}
```

## Charts

- Wrap Recharts in a `ChartCard` so titles, legends, tooltips,
  `ResponsiveContainer`, and empty states are consistent.
- Don't render Recharts directly in pages; it produces drifting styles
  across views.

```tsx
<ChartCard title="Top databases by space">
  <BarChart data={rows}>
    <XAxis dataKey="databasename" />
    <YAxis />
    <Tooltip />
    <Bar dataKey="currentperm" fill="var(--brand-orange)" />
  </BarChart>
</ChartCard>
```

## Performance

- Memoize chart inputs with `useMemo`. Recharts re-renders are
  expensive on large arrays.
- Virtualize tables >200 rows (`@tanstack/react-virtual`).
- `React.lazy` page components so route chunks ship separately.
- Use Vite's built-in code splitting; verify `npm run build` shows
  per-route bundles.

## Theming

Brand tokens are CSS variables, applied to Tailwind via the theme:

```js
// tailwind.config.js
theme: {
  extend: {
    colors: {
      brand: {
        orange: "var(--brand-orange)",
        navy:   "var(--brand-navy)",
      },
    },
    fontFamily: { sans: ["Inter", "system-ui", "sans-serif"] },
  },
}
```

```css
/* src/theme/brand.css */
:root {
  --brand-orange: #FF5F02;   /* Teradata Orange */
  --brand-navy:   #00233C;   /* Teradata Navy   */
  --brand-bg:     #FFFFFF;
  --brand-fg:     #00233C;
}
```

Users override by replacing `brand.css` or providing their own
stylesheet imported after it. See `styling.md`.

## Accessibility

- Every `<input>` has a `<label htmlFor>`.
- Charts include a screen-reader summary (`<figcaption>` or `aria-label`).
- Color is not the sole signal — pair with text/icon.
- Tab order matches visual order; trap focus in modals.

## Project conventions

- One component per file. File name matches component name.
- Co-locate component tests as `Foo.test.tsx`.
- Absolute imports via `@/` baseUrl alias; no `../../../` chains.
