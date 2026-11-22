import { Suspense } from "react";

import { ShareRoute } from "@/components/share/share-view";

export default function SharePage() {
  return (
    <Suspense fallback={null}>
      <ShareRoute />
    </Suspense>
  );
}
