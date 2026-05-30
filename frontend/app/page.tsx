"use client"

import { useFounderSearch } from "@/hooks/useFounderSearch"
import { SearchForm } from "@/components/SearchForm"
import { ProgressFeed } from "@/components/ProgressFeed"
import { ResultsGrid } from "@/components/ResultsGrid"
import { ErrorBanner } from "@/components/ErrorBanner"

export default function Home() {
  const { state, startSearch, reset } = useFounderSearch()

  return (
    <div className="min-h-screen bg-[--color-background] flex flex-col">
      <div className="flex-1 py-8 px-4 sm:py-12 sm:px-6 lg:py-16">
        <div className="max-w-3xl mx-auto">
          {state.phase === "idle" ? (
            <>
              <div className="mb-12 sm:mb-16">
                <h1 className="text-3xl sm:text-4xl font-bold text-[--color-ink] mb-3">
                  Founder Discovery
                </h1>
                <p className="text-base sm:text-lg text-[--color-muted]">
                  Search startups and find founders aligned with your role.
                </p>
              </div>

              <div className="bg-[--color-surface] border border-[--color-border] rounded-[var(--radius)] p-6 sm:p-8">
                <SearchForm onSubmit={startSearch} isLoading={false} />
              </div>
            </>
          ) : state.phase === "error" ? (
            <>
              <div className="mb-8">
                <h1 className="text-3xl sm:text-4xl font-bold text-[--color-ink] mb-2">
                  Founder Discovery
                </h1>
              </div>
              <ErrorBanner
                code={state.errorCode || "unknown"}
                message={state.errorMessage || "An error occurred"}
                onRetry={reset}
              />
            </>
          ) : state.phase === "done" ? (
            <>
              <div className="mb-8 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                  <h1 className="text-3xl sm:text-4xl font-bold text-[--color-ink] mb-1">
                    Results
                  </h1>
                  <p className="text-sm text-[--color-muted]">
                    {state.results.length} founder{state.results.length !== 1 ? "s" : ""} found
                  </p>
                </div>
                <button
                  onClick={reset}
                  className="px-4 sm:px-6 py-2 text-[--color-ink] border border-[--color-border] rounded-[var(--radius)] font-medium hover:bg-[--color-surface-2] transition-colors duration-150 text-sm sm:text-base"
                >
                  New Search
                </button>
              </div>

              <ResultsGrid
                results={state.results}
                skippedCompanies={state.skippedCompanies}
              />
            </>
          ) : (
            <>
              <div className="mb-8">
                <h1 className="text-3xl sm:text-4xl font-bold text-[--color-ink] mb-2">
                  Founder Discovery
                </h1>
              </div>
              <ProgressFeed
                phase={state.phase}
                message={state.progressMessage}
                progressStep={state.progressStep}
              />
            </>
          )}
        </div>
      </div>

      <div className="py-4 px-4 border-t border-[--color-border] text-center text-xs text-[--color-muted]">
        <p>Backend must be running on http://localhost:8000</p>
      </div>
    </div>
  )
}
