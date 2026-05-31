"use client"

import { SearchPhase } from "@/lib/types"

interface ProgressFeedProps {
  phase: SearchPhase
  message: string
  progressStep: "companies" | "founders" | "ai" | null
}

function SpinnerIcon() {
  return (
    <svg
      className="animate-spin h-4 w-4"
      viewBox="0 0 16 16"
      fill="none"
    >
      <circle cx="8" cy="8" r="6" stroke="currentColor" strokeOpacity="0.3" strokeWidth="2" />
      <path d="M8 2a6 6 0 0 1 6 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  )
}

function CheckmarkIcon() {
  return (
    <svg
      className="h-4 w-4"
      viewBox="0 0 16 16"
      fill="none"
    >
      <path
        d="M3 8l3.5 3.5L13 5"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}

function PendingDot() {
  return <div className="w-2 h-2 rounded-full bg-current" />
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
                    ? "bg-[--color-accent] text-[--color-background]"
                    : isDone
                      ? "bg-[--color-score-high] text-[--color-background] animate-in zoom-in-50 duration-200"
                      : "bg-[--color-surface-2] text-[--color-muted] border border-[--color-border] animate-pulse opacity-60"
                }`}
              >
                {isDone ? <CheckmarkIcon /> : isActive ? <SpinnerIcon /> : <PendingDot />}
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
        <p className="text-sm text-[--color-muted] text-center">
          {message}
          <span className="inline-block w-px h-3 bg-[--color-muted] ml-1 align-middle animate-[blink_1s_step-end_infinite]" />
        </p>
      )}
    </div>
  )
}
