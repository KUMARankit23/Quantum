'use client'

import { motion } from 'framer-motion'

interface StatCardProps {
  icon: string
  label: string
  value: string | number
  unit?: string
  trend?: 'up' | 'down' | 'neutral'
  description?: string
}

export function StatCard({ icon, label, value, unit, trend, description }: StatCardProps) {
  return (
    <motion.div
      whileHover={{ scale: 1.05, translateY: -5 }}
      className="bg-white border border-gray-200 rounded-lg p-6 hover:border-blue-600 transition"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="text-3xl">{icon}</div>
        {trend && (
          <div className={`text-xs font-semibold ${
            trend === 'up' ? 'text-green-400' : trend === 'down' ? 'text-red-400' : 'text-gray-400'
          }`}>
            {trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→'} {trend?.toUpperCase()}
          </div>
        )}
      </div>
      
      <p className="text-gray-400 text-sm mb-2">{label}</p>
      <p className="text-3xl font-bold text-blue-600 mb-2">{value}</p>
      
      {unit && (
        <p className="text-xs text-gray-500">{unit}</p>
      )}
      
      {description && (
        <p className="text-xs text-gray-500 mt-3 pt-3 border-t border-gray-700">{description}</p>
      )}
    </motion.div>
  )
}
