/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'quantum-light': '#ffffff',
        'quantum-light-bg': '#f8f9fa',
        'quantum-light-card': '#ffffff',
        'quantum-primary': '#2563eb',
        'quantum-accent': '#7c3aed',
        'quantum-dark-text': '#1f2937',
        'quantum-light-text': '#4b5563',
      },
      fontFamily: {
        inter: ['Inter', 'sans-serif'],
        code: ['Fira Code', 'monospace'],
      },
    },
  },
  plugins: [],
}
