"use client"

import { useState } from "react"
import { SearchRequest } from "@/lib/types"
import { INDUSTRIES, COUNTRIES, STAGES } from "@/lib/constants"

interface SearchFormProps {
  onSubmit: (req: SearchRequest) => void
  isLoading: boolean
}

export function SearchForm({ onSubmit, isLoading }: SearchFormProps) {
  const [formData, setFormData] = useState<SearchRequest>({
    industry: "AI",
    country: "India",
    stage: "Series A",
    role_interest: "AI Engineer",
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(formData)
  }

  return (
    <form onSubmit={handleSubmit} className="w-full space-y-6">
      <div>
        <label className="block text-sm font-medium text-[--color-ink] mb-2">
          Industry
        </label>
        <select
          value={formData.industry}
          onChange={(e) =>
            setFormData({ ...formData, industry: e.target.value })
          }
          className="w-full px-4 py-2 bg-[--color-surface-2] border border-[--color-border] text-[--color-ink] rounded-[var(--radius)] text-sm transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-[--color-accent] focus:ring-offset-2 focus:ring-offset-[--color-surface]"
          disabled={isLoading}
        >
          {INDUSTRIES.map((ind) => (
            <option key={ind} value={ind}>
              {ind}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-[--color-ink] mb-2">
          Country
        </label>
        <select
          value={formData.country}
          onChange={(e) =>
            setFormData({ ...formData, country: e.target.value })
          }
          className="w-full px-4 py-2 bg-[--color-surface-2] border border-[--color-border] text-[--color-ink] rounded-[var(--radius)] text-sm transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-[--color-accent] focus:ring-offset-2 focus:ring-offset-[--color-surface]"
          disabled={isLoading}
        >
          {COUNTRIES.map((country) => (
            <option key={country} value={country}>
              {country}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-[--color-ink] mb-2">
          Company Stage
        </label>
        <select
          value={formData.stage}
          onChange={(e) => setFormData({ ...formData, stage: e.target.value })}
          className="w-full px-4 py-2 bg-[--color-surface-2] border border-[--color-border] text-[--color-ink] rounded-[var(--radius)] text-sm transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-[--color-accent] focus:ring-offset-2 focus:ring-offset-[--color-surface]"
          disabled={isLoading}
        >
          {STAGES.map((stage) => (
            <option key={stage} value={stage}>
              {stage}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-[--color-ink] mb-2">
          Role Interest
        </label>
        <input
          type="text"
          value={formData.role_interest}
          onChange={(e) =>
            setFormData({ ...formData, role_interest: e.target.value })
          }
          placeholder="e.g. AI Engineer, Full-stack Engineer"
          className="w-full px-4 py-2 bg-[--color-surface-2] border border-[--color-border] text-[--color-ink] placeholder-[--color-muted] rounded-[var(--radius)] text-sm transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-[--color-accent] focus:ring-offset-2 focus:ring-offset-[--color-surface]"
          disabled={isLoading}
        />
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full px-6 py-3 bg-[--color-accent] text-[--color-background] font-medium rounded-[var(--radius)] text-sm transition-opacity duration-150 hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isLoading ? "Searching..." : "Find Founders"}
      </button>
    </form>
  )
}
