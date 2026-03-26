"use client";

import { getVideoUrl } from "@/lib/api";

interface Props {
  jobId: string;
  onReset: () => void;
}

export function VideoPlayer({ jobId, onReset }: Props) {
  const videoUrl = getVideoUrl(jobId);

  return (
    <div className="w-full max-w-3xl flex flex-col gap-4">
      <h2 className="text-xl font-semibold text-white text-center">Your Timelapse is Ready!</h2>
      <video
        src={videoUrl}
        controls
        autoPlay
        loop
        className="w-full rounded-xl border border-gray-700 bg-black"
      />
      <div className="flex gap-3 justify-center">
        <a
          href={videoUrl}
          download={`timelapse_${jobId}.mp4`}
          className="bg-violet-600 hover:bg-violet-500 text-white font-semibold py-2.5 px-6 rounded-lg transition-colors"
        >
          Download MP4
        </a>
        <button
          onClick={onReset}
          className="bg-gray-700 hover:bg-gray-600 text-white font-semibold py-2.5 px-6 rounded-lg transition-colors"
        >
          Generate Another
        </button>
      </div>
    </div>
  );
}
