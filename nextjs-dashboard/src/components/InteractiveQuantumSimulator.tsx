'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'

export function InteractiveQuantumSimulator() {
  const [qubits, setQubits] = useState(2)
  const [gateSelected, setGateSelected] = useState('H')
  const [measurements, setMeasurements] = useState<Record<string, number>>({})
  const [running, setRunning] = useState(false)

  const gates = [
    { name: 'H', label: 'Hadamard', description: 'Creates superposition' },
    { name: 'X', label: 'Pauli-X', description: 'Bit flip' },
    { name: 'Z', label: 'Pauli-Z', description: 'Phase flip' },
    { name: 'CNOT', label: 'CNOT', description: 'Entangles qubits' },
    { name: 'RZ', label: 'RZ(θ)', description: 'Phase rotation' },
  ]

  const simulateQuantum = async () => {
    setRunning(true)
    const states: Record<string, number> = {}

    // Simulate quantum execution
    for (let i = 0; i < 1000; i++) {
      let state = ''
      for (let q = 0; q < qubits; q++) {
        // Simulate gate effect
        const rand = Math.random()
        state += gateSelected === 'H' && rand > 0.5 ? '1' : '0'
        if (gateSelected === 'X') state = state === '1' ? '0' : '1'
      }
      states[state] = (states[state] || 0) + 1
    }

    // Animate results
    for (const [state, count] of Object.entries(states)) {
      await new Promise((resolve) => setTimeout(resolve, 100))
      setMeasurements((prev) => ({
        ...prev,
        [state]: Math.min((prev[state] || 0) + 10, count),
      }))
    }

    setRunning(false)
  }

  const maxCount = Math.max(...Object.values(measurements), 1)

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg border-2 border-blue-300 p-8">
        <h3 className="text-2xl font-bold mb-6 text-blue-800">Interactive Quantum Circuit Simulator</h3>

        <div className="grid md:grid-cols-3 gap-6 mb-6">
          {/* Qubit Control */}
          <div className="space-y-3">
            <label className="block font-semibold text-gray-800">Number of Qubits</label>
            <div className="flex items-center gap-4">
              <input
                type="range"
                min="1"
                max="5"
                value={qubits}
                onChange={(e) => setQubits(parseInt(e.target.value))}
                disabled={running}
                className="flex-1"
              />
              <span className="text-2xl font-bold text-blue-600 w-12 text-center">{qubits}</span>
            </div>
            <div className="flex gap-2 flex-wrap">
              {Array(qubits)
                .fill(0)
                .map((_, i) => (
                  <motion.div
                    key={i}
                    animate={{ scale: running ? [1, 1.2, 1] : 1 }}
                    transition={{ repeat: running ? Infinity : 0, duration: 0.5 }}
                    className="w-10 h-10 bg-blue-600 text-white rounded-lg flex items-center justify-center font-bold border-2 border-blue-400"
                  >
                    q{i}
                  </motion.div>
                ))}
            </div>
          </div>

          {/* Gate Selection */}
          <div className="space-y-3">
            <label className="block font-semibold text-gray-800">Quantum Gate</label>
            <select value={gateSelected} onChange={(e) => setGateSelected(e.target.value)} disabled={running} className="w-full p-2 border border-gray-300 rounded-lg">
              {gates.map((g) => (
                <option key={g.name} value={g.name}>
                  {g.label}
                </option>
              ))}
            </select>
            <p className="text-sm text-gray-600">
              {gates.find((g) => g.name === gateSelected)?.description}
            </p>
          </div>

          {/* Execute Button */}
          <div className="flex flex-col justify-end">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={simulateQuantum}
              disabled={running}
              className="px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-bold rounded-lg hover:shadow-lg disabled:opacity-50 transition"
            >
              {running ? 'Executing...' : 'Execute Circuit'}
            </motion.button>
          </div>
        </div>

        {/* Circuit Visualization */}
        <div className="bg-white rounded-lg border border-gray-300 p-6 mb-6">
          <h4 className="font-bold mb-4 text-gray-800">Quantum Circuit</h4>
          <div className="space-y-2 font-mono text-sm">
            {Array(qubits)
              .fill(0)
              .map((_, i) => (
                <div key={i} className="flex items-center gap-2">
                  <span className="w-12">q{i}:</span>
                  <div className="flex-1 h-8 bg-gray-200 rounded flex items-center px-2 relative overflow-hidden">
                    <span className="text-gray-700">──</span>
                    <motion.span animate={{ x: running ? [0, 100, 200, 0] : 0 }} transition={{ duration: 2, repeat: running ? Infinity : 0 }} className="absolute text-lg">
                      [{gateSelected}]
                    </motion.span>
                    <span className="ml-auto text-gray-700">──⊙</span>
                  </div>
                </div>
              ))}
          </div>
        </div>

        {/* Measurement Results */}
        {Object.keys(measurements).length > 0 && (
          <div className="bg-white rounded-lg border border-gray-300 p-6">
            <h4 className="font-bold mb-4 text-gray-800">Measurement Results (1000 shots)</h4>
            <div className="space-y-3">
              {Object.entries(measurements)
                .sort((a, b) => b[1] - a[1])
                .map(([state, count]) => (
                  <motion.div key={state} initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-1">
                    <div className="flex items-center justify-between text-sm">
                      <span className="font-mono font-bold text-blue-600">|{state}⟩</span>
                      <span className="text-gray-600">{((count / 1000) * 100).toFixed(1)}%</span>
                    </div>
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${(count / maxCount) * 100}%` }}
                      transition={{ duration: 0.5 }}
                      className="h-6 bg-gradient-to-r from-blue-400 to-indigo-600 rounded-lg flex items-center px-2 text-white text-xs font-bold"
                    >
                      {count}
                    </motion.div>
                  </motion.div>
                ))}
            </div>
          </div>
        )}
      </motion.div>

      {/* Metaphysical Insight */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="bg-gradient-to-r from-purple-100 to-pink-100 rounded-lg border-2 border-purple-300 p-6">
        <p className="text-sm text-gray-800">
          <strong>🧘 Metaphysical Insight:</strong> In quantum mechanics, like in the Upanishads, observation creates reality. When you execute the circuit, you&apos;re collapsing infinite possibilities (Brahman) into one measured state (Maya). Each measurement is a moment of cosmic choice.
        </p>
      </motion.div>
    </div>
  )
}
