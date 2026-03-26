"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { createJob } from "@/lib/api";
import type { CreateJobRequest } from "@/lib/types";

export function useGenerateJob() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  async function submit(request: CreateJobRequest) {
    setIsSubmitting(true);
    setSubmitError(null);
    try {
      const { job_id } = await createJob(request);
      router.push(`/jobs/${job_id}`);
    } catch (e) {
      setSubmitError(e instanceof Error ? e.message : "Failed to start job");
      setIsSubmitting(false);
    }
  }

  return { submit, isSubmitting, submitError };
}
