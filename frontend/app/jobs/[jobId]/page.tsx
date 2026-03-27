"use client";

import { use, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useJobProgress } from "@/hooks/useJobProgress";
import { PipelineProgress } from "@/components/Pipeline";
import { KeyframeGallery } from "@/components/Keyframes";
import { VideoPlayer } from "@/components/VideoPlayer";
import { fetchJob } from "@/lib/api";
import type { Job } from "@/lib/types";

interface Props {
  params: Promise<{ jobId: string }>;
}

export default function JobPage({ params }: Props) {
  const { jobId } = use(params);
  const router = useRouter();
  const { progress, error: sseError } = useJobProgress(jobId);
  const [job, setJob] = useState<Job | null>(null);

  // Load initial job state
  useEffect(() => {
    fetchJob(jobId)
      .then(setJob)
      .catch(() => router.push("/generate"));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [jobId]);

  const isCompleted = progress?.status === "completed";
  const isFailed = progress?.status === "failed";
  const numStages = job?.num_stages ?? progress?.completed_keyframe_urls.length ?? 6;

  return (
    <main className="min-h-screen flex flex-col items-center px-4 py-12 gap-8">
      <div className="text-center">
        <h1 className="text-2xl font-bold text-white mb-1">
          {isCompleted ? "Timelapse Complete!" : "Generating Timelapse..."}
        </h1>
        {job && (
          <p className="text-gray-400 text-sm max-w-lg truncate">{job.goal}</p>
        )}
      </div>

      {progress && !isCompleted && (
        <PipelineProgress progress={progress} />
      )}

      {sseError && !progress && (
        <div className="text-red-400 text-sm">{sseError}</div>
      )}

      {isCompleted && (
        <VideoPlayer jobId={jobId} onReset={() => router.push("/generate")} />
      )}

      {(progress?.completed_keyframe_urls.length ?? 0) > 0 && !isCompleted && (
        <KeyframeGallery
          jobId={jobId}
          completedFrameUrls={progress?.completed_keyframe_urls ?? []}
          totalStages={numStages}
        />
      )}

      {isFailed && (
        <button
          onClick={() => router.push("/generate")}
          className="bg-gray-700 hover:bg-gray-600 text-white font-semibold py-2.5 px-6 rounded-lg transition-colors"
        >
          Try Again
        </button>
      )}
    </main>
  );
}
