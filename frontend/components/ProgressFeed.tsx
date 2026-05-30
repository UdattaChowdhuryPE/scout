"use client"

import { SearchPhase } from "@/lib/types"

interface ProgressFeedProps {
  phase: SearchPhase
  message: string
  progressStep: "companies" | "founders" | "ai" | null
}

export function ProgressFeed({
  phase,
  message,
  progressStep,
}: ProgressFeedProps) {
  const steps = [
    { id: "companies", label: "Finding companies" },
    { id: "founders", label: "Fetching founders" },
    { id: "ai", label: "AI analysis" },
  ]

  return (
    <div className="w-full max-w-md mx-auto space-y-8">
      <div className="space-y-4">
        {steps.map((step) => {
          const isActive = progressStep === step.id
          const isDone = steps.indexOf(step) < steps.indexOf(steps.find((s) => s.id === progressStep) || steps[0])

          return (
            <div key={step.id} className="flex items-center gap-3">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center font-medium text-xs flex-shrink-0 transition-all duration-150 ${
                  isActive
                    ? "bg-[--color-accent] text-[--color-background] animate-pulse"
                    : isDone
                      ? "bg-[--color-score-high] text-[--color-background]"
                      : "bg-[--color-surface-2] text-[--color-muted] border border-[--color-border]"
                }`}
              >
                {isDone ? "✓" : isActive ? "⟳" : "○"}
              </div>
              <span
                className={`text-sm font-medium transition-colors duration-150 ${
                  isActive || isDone ? "text-[--color-ink]" : "text-[--color-muted]"
                }`}
              >
                {step.label}
              </span>
            </div>
          )
        })}
      </div>

      {message && (
        <p className="text-sm text-[--color-muted] text-center">{message}</p>
      )}
    </div>
  )
}
