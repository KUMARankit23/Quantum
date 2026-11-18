'use client'

import { motion } from 'framer-motion'
import { useState } from 'react'

interface Column {
  key: string
  label: string
  width?: string
}

interface DataTableProps {
  columns: Column[]
  data: Record<string, any>[]
  title?: string
}

export function DataTable({ columns, data, title }: DataTableProps) {
  const [sortKey, setSortKey] = useState<string | null>(null)
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc')

  const handleSort = (key: string) => {
    if (sortKey === key) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      setSortKey(key)
      setSortOrder('asc')
    }
  }

  const sortedData = sortKey
    ? [...data].sort((a, b) => {
        const aVal = a[sortKey]
        const bVal = b[sortKey]
        
        if (typeof aVal === 'number' && typeof bVal === 'number') {
          return sortOrder === 'asc' ? aVal - bVal : bVal - aVal
        }
        
        const aStr = String(aVal).toLowerCase()
        const bStr = String(bVal).toLowerCase()
        return sortOrder === 'asc' ? aStr.localeCompare(bStr) : bStr.localeCompare(aStr)
      })
    : data

  return (
    <div className="bg-quantum-card border border-gray-700 rounded-lg overflow-hidden">
      {title && (
        <div className="border-b border-gray-700 px-6 py-4">
          <h3 className="font-semibold text-blue-600">{title}</h3>
        </div>
      )}
      
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200 bg-gray-50">
              {columns.map((col) => (
                <th
                  key={col.key}
                  onClick={() => handleSort(col.key)}
                  className="px-6 py-4 text-left text-xs font-semibold text-blue-600 uppercase cursor-pointer hover:bg-gray-100 transition"
                  style={{ width: col.width }}
                >
                  {col.label}
                  {sortKey === col.key && (
                    <span className="ml-2">{sortOrder === 'asc' ? '↑' : '↓'}</span>
                  )}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sortedData.map((row, idx) => (
              <motion.tr
                key={idx}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: idx * 0.05 }}
                className="border-b border-gray-200 hover:bg-gray-50 transition"
              >
                {columns.map((col) => (
                  <td
                    key={`${idx}-${col.key}`}
                    className="px-6 py-4 text-sm text-gray-400"
                    style={{ width: col.width }}
                  >
                    {typeof row[col.key] === 'number'
                      ? row[col.key].toFixed(2)
                      : row[col.key]}
                  </td>
                ))}
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
