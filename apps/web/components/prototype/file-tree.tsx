import { FileText, Folder } from "lucide-react";

import type { FileNode } from "@/lib/api";

function Nodes({ nodes }: { nodes: FileNode[] }) {
  return (
    <ul className="tree-list">
      {nodes.map((n) => (
        <li key={n.path}>
          <span className={n.type === "dir" ? "d" : undefined}>
            {n.type === "dir" ? <Folder className="icon" aria-hidden="true" /> : <FileText className="icon" aria-hidden="true" />}
            {n.name}
            {n.type === "dir" ? "/" : ""}
          </span>
          {n.children && n.children.length > 0 ? <Nodes nodes={n.children} /> : null}
        </li>
      ))}
    </ul>
  );
}

/** Read-only tree of the generated app. */
export function FileTree({ nodes }: { nodes: FileNode[] }) {
  if (nodes.length === 0) return <p className="small muted panel-body">No files yet.</p>;
  return (
    <div className="panel-body tree" role="tree" aria-label="Generated files">
      <Nodes nodes={nodes} />
    </div>
  );
}
