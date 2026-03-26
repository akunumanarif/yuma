"use client";

import type { JobStatus, ProgressEvent } from "@/lib/types";

const STAGES: { key: JobStatus; label: string }[] = [
  { key: "planning", label: "Planning" },
  { key: "generating_frames", label: "Keyframes" },
  { key: "generating_clips", label: "Video Clips" },
  { key: "stitching", label: "Stitching" },
  { key: "completed", label: "Done" },
];

const STATUS_ORDER: JobStatus[] = [
  "pending",
  "planning",
  "generating_frames",
  "generating_clips",
  "stitching",
  "completed",
];

function stageIndex(status: JobStatus) {
  return STATUS_ORDER.indexOf(status);
}

interface Props {
  progress: ProgressEvent;
}

export function PipelineProgress({ progress }: Props) {
  const currentIdx = stageIndex(progress.status);

  return (
    <div className="w-full max-w-2xl flex flex-col gap-4">
      {/* Progress bar */}
      <div className="w-full bg-gray-700 rounded-full h-2">
        <div
          className="bg-violet-500 h-2 rounded-full transition-all duration-500"
          style={{ width: `${progress.progress_percent}%` }}
        />
      </div>

      {/* Stage steps */}
      <div className="flex items-center justify-between">
        {STAGES.map((stage, i) => {
          const idx = stageIndex(stage.key);
          const isDone = currentIdx > idx || progress.status === "completed";
          const isActive = currentIdx === idx && progress.status !== "failed";
          const isFailed = progress.status === "failed" && isActive;

          return (
            <div key={stage.key} className="flex flex-col items-center gap-1">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-all
                  ${isFailed ? "bg-red-500 text-white" : ""}
                  ${isDone ? "bg-violet-500 text-white" : ""}
                  ${isActive && !isFailed ? "bg-violet-500/30 border-2 border-violet-400 text-violet-300 animate-pulse" : ""}
                  ${!isDone && !isActive ? "bg-gray-700 text-gray-500" : ""}
                `}
              >
                {isDone ? "✓" : i + 1}
              </div>
              <span className="text-xs text-gray-400 hidden sm:block">{stage.label}</span>
            </div>
          );
        })}
      </div>

      {/* Message */}
      <p className="text-sm text-gray-300 text-center">
        {progress.status === "failed" ? (
          <span className="text-red-400">{progress.error ?? "Generation failed"}</span>
        ) : (
          progress.message
        )}
      </p>
    </div>
  );
}
