"use client"

import { useState } from "react"

interface CopyButtonProps {
  text: string
  label?: string
}

export function CopyButton({ text, label = "Copy" }: CopyButtonProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error("Failed to copy:", err)
    }
  }

  return (
    <button
      onClick={handleCopy}
      className="px-3 py-1 text-xs sm:text-sm font-medium text-[--color-accent] hover:bg-[--color-surface-2] rounded-[var(--radius)] transition-colors duration-150"
    >
      {copied ? "✓ Copied!" : label}
    </button>
  )
}
