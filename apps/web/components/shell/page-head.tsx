import type { ReactNode } from "react";

interface PageHeadProps {
  title: string;
  description?: string;
  actions?: ReactNode;
}

export function PageHead({ title, description, actions }: PageHeadProps) {
  return (
    <div className="page-head">
      <div>
        <h1>{title}</h1>
        {description ? <p className="muted small">{description}</p> : null}
      </div>
      {actions ? <div className="actions">{actions}</div> : null}
    </div>
  );
}
