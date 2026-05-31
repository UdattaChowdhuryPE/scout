"use client"

import { FounderResult } from "@/lib/types"
import { CopyButton } from "./CopyButton"
import { ExternalLink } from "lucide-react"

interface FounderCardProps {
  result: FounderResult
  rank: number
}

function getScoreBadgeStyle(score: number): string {
  if (score >= 7) return "bg-[--color-score-high] text-[--color-background]"
  if (score >= 5) return "bg-[--color-score-mid] text-[--color-background]"
  return "bg-[--color-score-low] text-[--color-background]"
}

export function FounderCard({ result, rank }: FounderCardProps) {
  return (
    <div className="bg-[--color-surface] border border-[--color-border] rounded-[var(--radius)] overflow-hidden transition-colors duration-150 hover:bg-opacity-80 flex flex-col">
      <div className="p-6 border-b border-[--color-border]">
        <div className="flex items-start justify-between gap-4 mb-3">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <h3 className="text-base sm:text-lg font-semibold text-[--color-ink]">
                {result.full_name}
              </h3>
              {result.linkedin_url && (
                <a
                  href={result.linkedin_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center text-[--color-muted] hover:text-[--color-accent] transition-colors flex-shrink-0"
                  aria-label={`${result.full_name} on LinkedIn`}
                >
                  <ExternalLink size={14} />
                </a>
              )}
            </div>
            <p className="text-xs sm:text-sm text-[--color-muted] truncate">
              {result.company_name}
            </p>
          </div>
          <div
            className={`px-3 py-1 rounded-[var(--radius-pill)] font-semibold text-xs sm:text-sm whitespace-nowrap flex-shrink-0 ${getScoreBadgeStyle(result.fit_score)}`}
          >
            {result.fit_score}/10
          </div>
        </div>

        <p className="text-xs sm:text-sm text-[--color-ink] leading-relaxed">
          {result.fit_explanation}
        </p>
      </div>

      <div className="p-6 bg-[--color-surface-2] border-t border-[--color-border] flex-1 flex flex-col">
        <div className="mb-4 flex-1">
          <p className="text-xs font-medium text-[--color-muted] mb-2">
            Outreach Message
          </p>
          <div className="bg-[--color-background] p-4 rounded-[var(--radius)] border border-[--color-border] text-xs text-[--color-ink] whitespace-pre-wrap font-mono leading-relaxed overflow-y-auto max-h-48">
            {result.outreach_message}
          </div>
        </div>

        <div className="flex justify-between items-center">
          <span className="text-xs text-[--color-muted]">#{rank}</span>
          <CopyButton text={result.outreach_message} />
        </div>
      </div>
    </div>
  )
}
