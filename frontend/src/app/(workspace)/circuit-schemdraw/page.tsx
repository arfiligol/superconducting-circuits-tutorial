import { Suspense } from "react";

import { CircuitSchemdrawWorkspace } from "@/features/circuit-schemdraw/components/circuit-schemdraw-workspace";

export default function CircuitSchemdrawPage() {
  return (
    <Suspense
      fallback={
        <div className="rounded-[1rem] border border-border bg-card px-5 py-5 text-sm text-muted-foreground">
          Loading schemdraw workspace...
        </div>
      }
    >
      <CircuitSchemdrawWorkspace />
    </Suspense>
  );
}
