'use client'

import { useState } from 'react'

interface QuantumResult {
  success: boolean
  metrics: {
    qubits: number
    circuitDepth: number
    gateCount: number
    mse: string
    psnr: string
    ssim: string
    executionTime: string
    shots: number
    fidelity: string
  }
  timestamp: string
}

export function LiveQuantumOps() {
  const [imageSize, setImageSize] = useState(4)
  const [shots, setShots] = useState(1000)
  const [circuitType, setCircuitType] = useState('medium')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<QuantumResult | null>(null)
  const [error, setError] = useState('')

  const handleProcessImage = async () => {
    setLoading(true)
    setError('')

    try {
      // Generate random image data
      const imageData = Array(imageSize * imageSize)
        .fill(0)
        .map(() => Math.random())

      const response = await fetch('/api/quantum/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          imageData,
          imageSize,
          shots,
          circuitType,
        }),
      })

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError('Failed to process quantum operation')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Controls */}
      <div className="grid md:grid-cols-4 gap-4">
        <div>
          <label className="block text-sm font-semibold text-gray-900 mb-2">Image Size</label>
          <select
            value={imageSize}
            onChange={(e) => setImageSize(parseInt(e.target.value))}
            disabled={loading}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-white text-gray-900 focus:border-blue-600 focus:ring-2 focus:ring-blue-600/20"
          >
            <option value={2}>2×2</option>
            <option value={4}>4×4</option>
            <option value={8}>8×8</option>
            <option value={16}>16×16</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-900 mb-2">Shots</label>
          <select
            value={shots}
            onChange={(e) => setShots(parseInt(e.target.value))}
            disabled={loading}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-white text-gray-900 focus:border-blue-600 focus:ring-2 focus:ring-blue-600/20"
          >
            <option value={100}>100</option>
            <option value={500}>500</option>
            <option value={1000}>1000</option>
            <option value={5000}>5000</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-900 mb-2">Circuit Type</label>
          <select
            value={circuitType}
            onChange={(e) => setCircuitType(e.target.value)}
            disabled={loading}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-white text-gray-900 focus:border-blue-600 focus:ring-2 focus:ring-blue-600/20"
          >
            <option value="basic">Basic</option>
            <option value="medium">Medium</option>
            <option value="deep">Deep</option>
          </select>
        </div>

        <div className="flex items-end">
          <button
            onClick={handleProcessImage}
            disabled={loading}
            className="w-full px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-lg hover:shadow-lg transition disabled:opacity-50"
          >
            {loading ? 'Processing...' : 'Execute Quantum'}
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-6">
          <div className="bg-gradient-to-br from-blue-50 to-purple-50 border border-gray-200 rounded-lg p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Quantum Processing Results</h3>

            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-white rounded-lg p-4 border border-gray-200">
                <p className="text-sm text-gray-600">Qubits</p>
                <p className="text-2xl font-bold text-blue-600">{result.metrics.qubits}</p>
              </div>

              <div className="bg-white rounded-lg p-4 border border-gray-200">
                <p className="text-sm text-gray-600">Circuit Depth</p>
                <p className="text-2xl font-bold text-purple-600">{result.metrics.circuitDepth}</p>
              </div>

              <div className="bg-white rounded-lg p-4 border border-gray-200">
                <p className="text-sm text-gray-600">Gate Count</p>
                <p className="text-2xl font-bold text-blue-600">{result.metrics.gateCount}</p>
              </div>

              <div className="bg-white rounded-lg p-4 border border-gray-200">
                <p className="text-sm text-gray-600">Exec Time</p>
                <p className="text-2xl font-bold text-purple-600">{result.metrics.executionTime}</p>
              </div>
            </div>

            <div className="grid md:grid-cols-4 gap-4 mt-4">
              <div className="bg-white rounded-lg p-4 border border-gray-200">
                <p className="text-sm text-gray-600">MSE</p>
                <p className="text-xl font-bold text-gray-900">{result.metrics.mse}</p>
              </div>

              <div className="bg-white rounded-lg p-4 border border-gray-200">
                <p className="text-sm text-gray-600">PSNR (dB)</p>
                <p className="text-xl font-bold text-gray-900">{result.metrics.psnr}</p>
              </div>

              <div className="bg-white rounded-lg p-4 border border-gray-200">
                <p className="text-sm text-gray-600">SSIM</p>
                <p className="text-xl font-bold text-gray-900">{result.metrics.ssim}</p>
              </div>

              <div className="bg-white rounded-lg p-4 border border-gray-200">
                <p className="text-sm text-gray-600">Fidelity</p>
                <p className="text-xl font-bold text-gray-900">{result.metrics.fidelity}</p>
              </div>
            </div>

            <p className="text-xs text-gray-600 mt-4">Processed at: {new Date(result.timestamp).toLocaleTimeString()}</p>
          </div>
        </div>
      )}
    </div>
  )
}
