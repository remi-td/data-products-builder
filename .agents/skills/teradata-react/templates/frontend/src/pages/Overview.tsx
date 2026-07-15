import { PageShell } from "@/components/PageShell";

export default function Overview() {
  return (
    <PageShell title="Overview">
      <p className="text-brand-muted">
        Replace this page with your app's landing view. Add new pages under
        <code className="mx-1 rounded bg-black/5 px-1">src/pages/</code>
        and wire them in <code className="mx-1 rounded bg-black/5 px-1">App.tsx</code>.
      </p>
    </PageShell>
  );
}
