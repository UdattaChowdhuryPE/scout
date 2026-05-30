"use client"

interface ErrorBannerProps {
  code: string
  message: string
  onRetry: () => void
}

function getErrorHint(code: string): string {
  const hints: Record<string, string> = {
    no_companies:
      "Try a different industry or country combination.",
    no_founders:
      "Try different search criteria — many companies don't have indexed founders.",
    crustdata_error:
      "The data service is having issues. Please try again in a moment.",
    ai_error:
      "Claude analysis failed. Please check your API key and try again.",
    missing_keys:
      "Please configure your API keys in the backend .env file.",
    network_error:
      "Connection failed. Make sure the backend is running on http://localhost:8000",
  }
  return hints[code] || "An error occurred. Please try again."
}

export function ErrorBanner({ code, message, onRetry }: ErrorBannerProps) {
  return (
    <div className="w-full max-w-2xl bg-[--color-surface] border border-[--color-score-low] rounded-[var(--radius)] p-6 space-y-4">
      <div>
        <h3 className="font-semibold text-[--color-score-low] mb-2 text-base sm:text-lg">Search Failed</h3>
        <p className="text-sm text-[--color-ink] mb-2">{message}</p>
        <p className="text-xs text-[--color-muted]">{getErrorHint(code)}</p>
      </div>

      <button
        onClick={onRetry}
        className="w-full sm:w-auto px-6 py-2 bg-[--color-score-low] text-[--color-background] font-medium rounded-[var(--radius)] text-sm transition-opacity duration-150 hover:opacity-90"
      >
        Try Again
      </button>
    </div>
  )
}
