"use client"

import { FounderResult } from "@/lib/types"
import { FounderCard } from "./FounderCard"

interface ResultsGridProps {
  results: FounderResult[]
  skippedCompanies: number
}

export function ResultsGrid({ results, skippedCompanies }: ResultsGridProps) {
  const topResults = results.filter(r => r.fit_score >= 6)
  const lowResults = results.filter(r => r.fit_score < 6)

  return (
    <div className="w-full space-y-6">
      {skippedCompanies > 0 && (
        <div className="bg-[--color-surface-2] border border-[--color-border] rounded-[var(--radius)] p-4">
          <p className="text-xs sm:text-sm text-[--color-ink]">
            <strong>{skippedCompanies}</strong> companies had no indexed founders
          </p>
        </div>
      )}

      <div className="space-y-4">
        {topResults.map((result, index) => (
          <div
            key={`${result.full_name}-${result.company_name}`}
            className="animate-in fade-in slide-in-from-bottom-2 duration-300"
            style={{ animationDelay: `${index * 30}ms` }}
          >
            <FounderCard result={result} rank={index + 1} />
          </div>
        ))}
      </div>

      {lowResults.length > 0 && (
        <details className="group">
          <summary className="cursor-pointer bg-[--color-surface-2] border border-[--color-border] rounded-[var(--radius)] p-4 hover:bg-[--color-surface-3] transition-colors">
            <span className="text-sm font-medium text-[--color-ink]">
              Low Relevance — {lowResults.length} founder{lowResults.length === 1 ? '' : 's'}
            </span>
          </summary>
          <div className="mt-4 space-y-4">
            {lowResults.map((result, index) => (
              <div
                key={`${result.full_name}-${result.company_name}-low`}
                className="animate-in fade-in slide-in-from-bottom-2 duration-300"
                style={{ animationDelay: `${index * 30}ms` }}
              >
                <FounderCard result={result} rank={topResults.length + index + 1} />
              </div>
            ))}
          </div>
        </details>
      )}
    </div>
  )
}
