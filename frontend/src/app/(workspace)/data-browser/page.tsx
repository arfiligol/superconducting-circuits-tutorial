import { Suspense } from "react";

import { DataBrowserWorkspace } from "@/features/data-browser/components/data-browser-workspace";

export default function DataBrowserPage() {
  return (
    <Suspense
      fallback={
        <div className="rounded-[1rem] border border-border bg-card px-5 py-5 text-sm text-muted-foreground">
          Loading datasets...
        </div>
      }
    >
      <DataBrowserWorkspace />
    </Suspense>
  );
}
