'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'

interface CodeBlockProps {
  code: string
  language?: string
  title?: string
}

export function CodeBlock({ code, language = 'python', title }: CodeBlockProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      whileInView={{ opacity: 1, y: 0 }}
      className="bg-black/50 border border-gray-700 rounded-lg overflow-hidden"
    >
      {/* Header */}
      <div className="flex items-center justify-between bg-gray-100 px-4 py-3 border-b border-gray-200">
        <div className="flex items-center gap-3">
          <div className="w-3 h-3 rounded-full bg-red-500" />
          <div className="w-3 h-3 rounded-full bg-yellow-500" />
          <div className="w-3 h-3 rounded-full bg-green-500" />
          {title && <span className="ml-3 text-xs text-gray-400 font-code">{title}</span>}
        </div>
        <button
          onClick={handleCopy}
          className="text-xs text-gray-600 hover:text-blue-600 transition px-2 py-1"
        >
          {copied ? '✓ Copied' : 'Copy'}
        </button>
      </div>

      {/* Code */}
      <pre className="overflow-x-auto p-4 text-sm font-code text-gray-300 leading-relaxed">
        <code>{code}</code>
      </pre>
    </motion.div>
  )
}
