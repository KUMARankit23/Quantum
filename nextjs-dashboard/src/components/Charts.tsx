'use client'

import {
  LineChart, Line, BarChart, Bar, ScatterChart, Scatter,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from 'recharts'

const resolutionData = [
  { size: '2x2', qubits: 2, time: 0.1 },
  { size: '4x4', qubits: 4, time: 0.5 },
  { size: '8x8', qubits: 6, time: 2.1 },
  { size: '16x16', qubits: 8, time: 8.5 },
]

const shotImpactData = [
  { shots: 100, psnr: 18.5, time: 0.2 },
  { shots: 500, psnr: 22.1, time: 1.0 },
  { shots: 1000, psnr: 24.3, time: 2.0 },
  { shots: 5000, psnr: 25.8, time: 10.0 },
]

const noiseData = [
  { level: '0%', quality: 28.5 },
  { level: '1%', quality: 26.2 },
  { level: '5%', quality: 20.8 },
  { level: '10%', quality: 15.3 },
]

const comparisonData = [
  { name: 'Quantum', psnr: 24.3, time: 2.0 },
  { name: 'Classical', psnr: 30.2, time: 0.1 },
]

export function ResolutionScalingChart() {
  return (
    <div className='bg-white border border-gray-200 rounded-lg p-6'>
      <h3 className='text-lg font-bold mb-4 text-blue-600'>Resolution Scaling Analysis</h3>
      <ResponsiveContainer width='100%' height={300}>
        <LineChart data={resolutionData}>
          <CartesianGrid strokeDasharray='3 3' stroke='#e5e7eb' />
          <XAxis dataKey='size' stroke='#6b7280' />
          <YAxis stroke='#6b7280' />
          <Tooltip contentStyle={{ backgroundColor: '#ffffff', border: '1px solid #2563eb' }} />
          <Legend />
          <Line type='monotone' dataKey='qubits' stroke='#2563eb' strokeWidth={2} name='Qubits Required' />
          <Line type='monotone' dataKey='time' stroke='#7c3aed' strokeWidth={2} name='Execution Time (s)' />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

export function ShotImpactChart() {
  return (
    <div className='bg-white border border-gray-200 rounded-lg p-6'>
      <h3 className='text-lg font-bold mb-4 text-blue-600'>Shot Count Impact</h3>
      <ResponsiveContainer width='100%' height={300}>
        <ScatterChart data={shotImpactData} margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
          <CartesianGrid strokeDasharray='3 3' stroke='#e5e7eb' />
          <XAxis dataKey='shots' stroke='#6b7280' type='number' name='Shots' />
          <YAxis stroke='#6b7280' />
          <Tooltip contentStyle={{ backgroundColor: '#ffffff', border: '1px solid #2563eb' }} />
          <Scatter name='PSNR vs Shots' data={shotImpactData} fill='#2563eb' />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  )
}

export function NoiseImpactChart() {
  return (
    <div className='bg-white border border-gray-200 rounded-lg p-6'>
      <h3 className='text-lg font-bold mb-4 text-blue-600'>Noise Sensitivity</h3>
      <ResponsiveContainer width='100%' height={300}>
        <BarChart data={noiseData}>
          <CartesianGrid strokeDasharray='3 3' stroke='#e5e7eb' />
          <XAxis dataKey='level' stroke='#6b7280' />
          <YAxis stroke='#6b7280' />
          <Tooltip contentStyle={{ backgroundColor: '#ffffff', border: '1px solid #2563eb' }} />
          <Bar dataKey='quality' fill='#7c3aed' radius={[8, 8, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

export function QuantumVsClassicalChart() {
  return (
    <div className='bg-white border border-gray-200 rounded-lg p-6'>
      <h3 className='text-lg font-bold mb-4 text-blue-600'>Quantum vs Classical Comparison</h3>
      <ResponsiveContainer width='100%' height={300}>
        <BarChart data={comparisonData} layout='vertical'>
          <CartesianGrid strokeDasharray='3 3' stroke='#e5e7eb' />
          <XAxis type='number' stroke='#6b7280' />
          <YAxis dataKey='name' type='category' stroke='#6b7280' />
          <Tooltip contentStyle={{ backgroundColor: '#ffffff', border: '1px solid #2563eb' }} />
          <Legend />
          <Bar dataKey='psnr' fill='#2563eb' name='PSNR (dB)' />
          <Bar dataKey='time' fill='#7c3aed' name='Time (s)' />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
