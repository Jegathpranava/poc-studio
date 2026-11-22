import { PageHead } from "./page-head";

export function PlaceholderPage({ title, description }: { title: string; description: string }) {
  return (
    <section className="screen">
      <PageHead title={title} description={description} />
      <div className="panel">
        <div className="panel-body muted small">This page arrives in a later increment.</div>
      </div>
    </section>
  );
}
