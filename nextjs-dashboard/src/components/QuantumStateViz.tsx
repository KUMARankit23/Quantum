'use client'

import { useEffect, useRef } from 'react'

export function QuantumStateViz() {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!containerRef.current) return

    import('three').then((THREE) => {
      const container = containerRef.current!
      const width = container.clientWidth
      const height = 400

      const scene = new THREE.Scene()
      scene.background = new THREE.Color(0x0a0e13)

      const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000)
      camera.position.set(0, 0, 8)

      const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
      renderer.setSize(width, height)
      renderer.setPixelRatio(window.devicePixelRatio)
      container.appendChild(renderer.domElement)

      const ambientLight = new THREE.AmbientLight(0xffffff, 0.6)
      scene.add(ambientLight)

      const pointLight = new THREE.PointLight(0x667eea, 1, 100)
      pointLight.position.set(10, 10, 10)
      scene.add(pointLight)

      // Create probability distribution bars (4x4 grid for 16 basis states)
      const bars = []
      const gridSize = 4
      const barSpacing = 1.2

      for (let i = 0; i < gridSize; i++) {
        for (let j = 0; j < gridSize; j++) {
          const probability = Math.random() * 0.8 + 0.2
          const barHeight = probability * 2

          const geometry = new THREE.BoxGeometry(0.7, barHeight, 0.7)
          const hue = (i * gridSize + j) / (gridSize * gridSize)
          const material = new THREE.MeshStandardMaterial({
            color: new THREE.Color().setHSL(hue * 0.6 + 0.4, 0.9, 0.5),
            emissive: new THREE.Color().setHSL(hue * 0.6 + 0.4, 0.9, 0.4),
            emissiveIntensity: 0.5,
            metalness: 0.4,
            roughness: 0.6,
          })

          const bar = new THREE.Mesh(geometry, material)
          const xPos = (i - gridSize / 2) * barSpacing + barSpacing / 2
          const zPos = (j - gridSize / 2) * barSpacing + barSpacing / 2

          bar.position.set(xPos, barHeight / 2, zPos)
          bar.userData.index = i * gridSize + j
          bar.userData.baseHeight = barHeight
          bar.userData.baseProbability = probability

          bars.push(bar)
          scene.add(bar)
        }
      }

      // Add center measurement indicator
      const centerGeometry = new THREE.SphereGeometry(0.3, 32, 32)
      const centerMaterial = new THREE.MeshStandardMaterial({
        color: 0xf093fb,
        emissive: 0xf093fb,
        emissiveIntensity: 0.8,
      })
      const measurementPoint = new THREE.Mesh(centerGeometry, centerMaterial)
      measurementPoint.position.set(0, -1, 0)
      scene.add(measurementPoint)

      // Animation
      let animationFrameId: number
      const startTime = Date.now()

      const animate = () => {
        animationFrameId = requestAnimationFrame(animate)
        const elapsed = (Date.now() - startTime) * 0.001

        // Animate probability bars with quantum oscillation
        bars.forEach((bar, i) => {
          const oscillation = Math.sin(elapsed * 1.2 + i * 0.2) * 0.3 + 0.7
          const newHeight = bar.userData.baseHeight * oscillation
          bar.scale.y = newHeight / bar.userData.baseHeight
          bar.position.y = newHeight / 2

          // Pulsing emission
          const emission = Math.sin(elapsed * 2 + i * 0.3) * 0.3 + 0.5
          ;(bar.material as THREE.MeshStandardMaterial).emissiveIntensity = emission
        })

        // Rotate measurement point
        measurementPoint.rotation.x += 0.01
        measurementPoint.rotation.y += 0.015

        renderer.render(scene, camera)
      }

      animate()

      const handleResize = () => {
        const newWidth = container.clientWidth
        const newHeight = height
        camera.aspect = newWidth / newHeight
        camera.updateProjectionMatrix()
        renderer.setSize(newWidth, newHeight)
      }

      window.addEventListener('resize', handleResize)

      return () => {
        window.removeEventListener('resize', handleResize)
        cancelAnimationFrame(animationFrameId)
        renderer.dispose()
        container.removeChild(renderer.domElement)
      }
    })
  }, [])

  return <div ref={containerRef} className="w-full bg-black/30 rounded-lg overflow-hidden border border-gray-700" style={{ height: '400px' }} />
}
