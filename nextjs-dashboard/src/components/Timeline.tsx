'use client'

import { motion } from 'framer-motion'

interface TimelineEvent {
  title: string
  description: string
  icon: string
}

interface TimelineProps {
  events: TimelineEvent[]
}

export function Timeline({ events }: TimelineProps) {
  return (
    <div className="relative">
      {/* Vertical line */}
      <div className="absolute left-8 top-0 bottom-0 w-1 bg-gradient-to-b from-blue-600 to-purple-600" />

      {/* Events */}
      <div className="space-y-8">
        {events.map((event, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className="relative pl-24"
          >
            {/* Circle */}
            <motion.div
              whileHover={{ scale: 1.2 }}
              className="absolute -left-3 top-0 w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center"
            >
              <span className="text-white text-lg">{event.icon}</span>
            </motion.div>

            {/* Content */}
            <div className="bg-gray-100 border border-blue-300 rounded-lg p-6 hover:border-blue-600 transition">
              <h3 className="font-semibold text-blue-600 mb-2">{event.title}</h3>
              <p className="text-gray-400 text-sm">{event.description}</p>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )
}
