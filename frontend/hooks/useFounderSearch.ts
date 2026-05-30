"use client"

import { useState, useCallback, useRef } from "react"
import {
  SearchRequest,
  FounderResult,
  SearchPhase,
  SSEEvent,
} from "@/lib/types"

interface SearchState {
  phase: SearchPhase
  progressMessage: string
  progressStep: "companies" | "founders" | "ai" | null
  results: FounderResult[]
  errorCode: string | null
  errorMessage: string | null
  skippedCompanies: number
}

export function useFounderSearch() {
  const [state, setState] = useState<SearchState>({
    phase: "idle",
    progressMessage: "",
    progressStep: null,
    results: [],
    errorCode: null,
    errorMessage: null,
    skippedCompanies: 0,
  })

  const abortControllerRef = useRef<AbortController | null>(null)

  const startSearch = useCallback(async (request: SearchRequest) => {
    // Abort any previous request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }

    // Create new abort controller
    const controller = new AbortController()
    abortControllerRef.current = controller

    setState({
      phase: "companies",
      progressMessage: "",
      progressStep: null,
      results: [],
      errorCode: null,
      errorMessage: null,
      skippedCompanies: 0,
    })

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
      const response = await fetch(`${apiUrl}/api/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(request),
        signal: controller.signal,
        cache: "no-store",
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }

      if (!response.body) {
        throw new Error("No response body")
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ""

      while (true) {
        const { done, value } = await reader.read()

        if (done) break

        // Handle abort
        if (controller.signal.aborted) {
          reader.cancel()
          break
        }

        buffer += decoder.decode(value, { stream: true })
        const events = buffer.split("\n\n")
        buffer = events.pop() || ""

        for (const eventStr of events) {
          const line = eventStr.replace(/^data: /, "").trim()
          if (!line) continue

          try {
            const event: SSEEvent = JSON.parse(line)

            if (event.type === "progress") {
              setState((prev) => ({
                ...prev,
                phase: "companies",
                progressMessage: event.message || "",
                progressStep:
                  (event.step as "companies" | "founders" | "ai") || null,
              }))
            } else if (event.type === "results") {
              setState((prev) => ({
                ...prev,
                phase: "done",
                results: event.founders || [],
                skippedCompanies: event.skipped_companies || 0,
              }))
            } else if (event.type === "error") {
              setState((prev) => ({
                ...prev,
                phase: "error",
                errorCode: event.code || "unknown",
                errorMessage: event.message || "An error occurred",
              }))
            }
          } catch (e) {
            console.error("Failed to parse SSE event:", line, e)
          }
        }
      }
    } catch (error) {
      if (!(error instanceof Error && error.name === "AbortError")) {
        setState((prev) => ({
          ...prev,
          phase: "error",
          errorCode: "network_error",
          errorMessage:
            error instanceof Error
              ? error.message
              : "Network error occurred",
        }))
      }
    }
  }, [])

  const reset = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }
    setState({
      phase: "idle",
      progressMessage: "",
      progressStep: null,
      results: [],
      errorCode: null,
      errorMessage: null,
      skippedCompanies: 0,
    })
  }, [])

  return { state, startSearch, reset }
}
