export type JobStatus =
  | "pending"
  | "planning"
  | "generating_frames"
  | "generating_clips"
  | "stitching"
  | "completed"
  | "failed";

export type StageStatus = "pending" | "in_progress" | "completed" | "failed";

export interface SceneStage {
  index: number;
  title: string;
  description: string;
  prompt: string;
  keyframe_url: string | null;
  status: StageStatus;
}

export interface ProgressEvent {
  job_id: string;
  status: JobStatus;
  progress_percent: number;
  current_stage_index: number | null;
  message: string;
  completed_keyframe_urls: string[];
  completed_clips: number[];
  output_video_url: string | null;
  error: string | null;
}

export interface Job {
  id: string;
  goal: string;
  category: string;
  num_stages: number;
  status: JobStatus;
  stages: SceneStage[];
  output_video_url: string | null;
  progress_percent: number;
  created_at: string;
}

export interface CreateJobRequest {
  goal: string;
  category: string;
  num_stages: number;
}

export const CATEGORIES = [
  { value: "room_cleaning", label: "Room Cleaning" },
  { value: "construction", label: "Building / Construction" },
  { value: "car_cleaning", label: "Car / Vehicle Cleaning" },
  { value: "carpet_cleaning", label: "Carpet / Floor Cleaning" },
  { value: "garden", label: "Garden Transformation" },
  { value: "renovation", label: "Room Renovation" },
  { value: "other", label: "Other" },
] as const;

export type Category = (typeof CATEGORIES)[number]["value"];
