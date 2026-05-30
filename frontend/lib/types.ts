export interface SearchRequest {
  industry: string
  country: string
  stage: string
  role_interest: string
}

export interface Company {
  company_id: number
  company_name: string
  domain: string
  hq_country: string
  funding_stage: string
  total_funding_usd: number | null
  last_funding_date: string | null
  description: string | null
  linkedin_url: string | null
  company_tags: string[]
  linkedin_headcount: number | null
}

export interface Founder {
  full_name: string
  current_title: string
  linkedin_url: string | null
  email: string | null
  company_name: string
  company_id: number
}

export interface FounderResult {
  full_name: string
  company_name: string
  fit_score: number
  fit_explanation: string
  outreach_message: string
}

export type SearchPhase = "idle" | "companies" | "founders" | "ai" | "done" | "error"

export interface SSEEvent {
  type: "progress" | "results" | "error"
  step?: "companies" | "founders" | "ai"
  message?: string
  code?: string
  founders?: FounderResult[]
  skipped_companies?: number
}
