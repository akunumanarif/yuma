"use client";

import Image from "next/image";
import { getFrameUrl } from "@/lib/api";

interface Props {
  jobId: string;
  completedFrameUrls: string[];
  totalStages: number;
}

export function KeyframeGallery({ jobId, completedFrameUrls, totalStages }: Props) {
  const skeletonCount = Math.max(0, totalStages - completedFrameUrls.length);

  return (
    <div className="w-full max-w-4xl">
      <h3 className="text-sm font-medium text-gray-400 mb-3">
        Keyframes ({completedFrameUrls.length}/{totalStages})
      </h3>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
        {completedFrameUrls.map((url, i) => (
          <div
            key={i}
            className="relative aspect-video rounded-lg overflow-hidden bg-gray-800 animate-fade-in"
          >
            <Image
              src={`${process.env.NEXT_PUBLIC_API_URL}${url}`}
              alt={`Keyframe ${i + 1}`}
              fill
              className="object-cover"
              unoptimized
            />
            <div className="absolute bottom-1 left-1 bg-black/60 text-white text-xs px-1.5 py-0.5 rounded">
              {i + 1}
            </div>
          </div>
        ))}
        {Array.from({ length: skeletonCount }).map((_, i) => (
          <div
            key={`skeleton-${i}`}
            className="aspect-video rounded-lg bg-gray-800 animate-pulse"
          />
        ))}
      </div>
    </div>
  );
}
