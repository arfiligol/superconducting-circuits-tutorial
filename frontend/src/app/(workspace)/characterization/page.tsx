import { Suspense } from "react";

import { CharacterizationWorkspace } from "@/features/characterization/components/characterization-workspace";

export default function CharacterizationPage() {
  return (
    <Suspense fallback={null}>
      <CharacterizationWorkspace />
    </Suspense>
  );
}
