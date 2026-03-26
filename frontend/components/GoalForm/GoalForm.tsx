"use client";

import { useState } from "react";
import { CATEGORIES } from "@/lib/types";
import type { CreateJobRequest } from "@/lib/types";

interface Props {
  onSubmit: (req: CreateJobRequest) => void;
  isSubmitting: boolean;
  error: string | null;
}

export function GoalForm({ onSubmit, isSubmitting, error }: Props) {
  const [goal, setGoal] = useState("");
  const [category, setCategory] = useState(CATEGORIES[0].value);
  const [numStages, setNumStages] = useState(6);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (goal.trim().length < 10) return;
    onSubmit({ goal: goal.trim(), category, num_stages: numStages });
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-5 w-full max-w-2xl">
      <div className="flex flex-col gap-2">
        <label className="text-sm font-medium text-gray-300">Category</label>
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="bg-gray-800 border border-gray-600 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:ring-2 focus:ring-violet-500"
        >
          {CATEGORIES.map((c) => (
            <option key={c.value} value={c.value}>{c.label}</option>
          ))}
        </select>
      </div>

      <div className="flex flex-col gap-2">
        <label className="text-sm font-medium text-gray-300">
          Describe your transformation
        </label>
        <textarea
          value={goal}
          onChange={(e) => setGoal(e.target.value)}
          placeholder="e.g. A very messy college dorm room with clothes everywhere → clean, organized, minimalist dorm room with new decor"
          rows={4}
          className="bg-gray-800 border border-gray-600 rounded-lg px-4 py-3 text-white placeholder-gray-500 resize-none focus:outline-none focus:ring-2 focus:ring-violet-500"
          minLength={10}
          maxLength={500}
          required
        />
        <span className="text-xs text-gray-500 text-right">{goal.length}/500</span>
      </div>

      <div className="flex flex-col gap-2">
        <label className="text-sm font-medium text-gray-300">
          Number of keyframes: <span className="text-violet-400">{numStages}</span>
        </label>
        <input
          type="range"
          min={4}
          max={8}
          value={numStages}
          onChange={(e) => setNumStages(Number(e.target.value))}
          className="accent-violet-500"
        />
        <div className="flex justify-between text-xs text-gray-500">
          <span>4 (faster)</span>
          <span>8 (more detail)</span>
        </div>
      </div>

      {error && (
        <div className="bg-red-900/40 border border-red-500/50 rounded-lg px-4 py-3 text-red-300 text-sm">
          {error}
        </div>
      )}

      <button
        type="submit"
        disabled={isSubmitting || goal.trim().length < 10}
        className="bg-violet-600 hover:bg-violet-500 disabled:bg-gray-700 disabled:text-gray-500 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
      >
        {isSubmitting ? "Starting..." : "Generate Timelapse"}
      </button>
    </form>
  );
}
