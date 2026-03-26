"use client";

import { useEffect, useState } from "react";
import { getStreamUrl } from "@/lib/api";
import type { ProgressEvent } from "@/lib/types";

export function useJobProgress(jobId: string | null) {
  const [progress, setProgress] = useState<ProgressEvent | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!jobId) return;

    const url = getStreamUrl(jobId);
    const es = new EventSource(url);

    es.onmessage = (e) => {
      try {
        const event: ProgressEvent = JSON.parse(e.data);
        setProgress(event);
        if (event.status === "completed" || event.status === "failed") {
          es.close();
        }
      } catch {
        // ignore parse errors on ping comments
      }
    };

    es.onerror = () => {
      setError("Connection to server lost");
      es.close();
    };

    return () => es.close();
  }, [jobId]);

  return { progress, error };
}
