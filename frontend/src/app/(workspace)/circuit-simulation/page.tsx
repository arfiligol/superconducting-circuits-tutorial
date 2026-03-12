import { Suspense } from "react";

import { SimulationWorkbenchShell } from "@/features/simulation/components/simulation-workbench-shell";

export default function CircuitSimulationPage() {
  return (
    <Suspense
      fallback={
        <div className="rounded-[1rem] border border-border bg-card px-5 py-5 text-sm text-muted-foreground">
          Loading simulation workspace...
        </div>
      }
    >
      <SimulationWorkbenchShell />
    </Suspense>
  );
}
