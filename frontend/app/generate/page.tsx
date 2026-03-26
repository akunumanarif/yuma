"use client";

import { GoalForm } from "@/components/GoalForm";
import { useGenerateJob } from "@/hooks/useGenerateJob";

export default function GeneratePage() {
  const { submit, isSubmitting, submitError } = useGenerateJob();

  return (
    <main className="min-h-screen flex flex-col items-center justify-center px-4 py-12">
      <div className="mb-10 text-center">
        <h1 className="text-4xl font-bold text-white mb-3">
          Yuma
        </h1>
        <p className="text-gray-400 max-w-lg">
          Generate AI-powered timelapse videos — room cleanups, construction, renovations, and more.
        </p>
      </div>

      <GoalForm
        onSubmit={submit}
        isSubmitting={isSubmitting}
        error={submitError}
      />
    </main>
  );
}
