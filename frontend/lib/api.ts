import type { CreateJobRequest, Job } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function createJob(request: CreateJobRequest): Promise<{ job_id: string }> {
  const res = await fetch(`${API_URL}/api/jobs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function fetchJob(jobId: string): Promise<Job> {
  const res = await fetch(`${API_URL}/api/jobs/${jobId}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const data = await res.json();
  return data.job;
}

export function getStreamUrl(jobId: string): string {
  return `${API_URL}/api/jobs/${jobId}/stream`;
}

export function getVideoUrl(jobId: string): string {
  return `${API_URL}/api/jobs/${jobId}/video`;
}

export function getFrameUrl(jobId: string, frameIndex: number): string {
  return `${API_URL}/api/jobs/${jobId}/frames/${frameIndex}`;
}

export async function cancelJob(jobId: string): Promise<void> {
  await fetch(`${API_URL}/api/jobs/${jobId}`, { method: "DELETE" });
}
