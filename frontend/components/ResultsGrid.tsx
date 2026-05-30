"use client"

import { FounderResult } from "@/lib/types"
import { FounderCard } from "./FounderCard"

interface ResultsGridProps {
  results: FounderResult[]
  skippedCompanies: number
}

export function ResultsGrid({ results, skippedCompanies }: ResultsGridProps) {
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
        {results.map((result, index) => (
          <div
            key={`${result.full_name}-${result.company_name}`}
            className="animate-in fade-in slide-in-from-bottom-2 duration-300"
            style={{ animationDelay: `${index * 30}ms` }}
          >
            <FounderCard result={result} rank={index + 1} />
          </div>
        ))}
      </div>
    </div>
  )
}
