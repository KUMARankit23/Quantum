'use client'

import { useEffect, useRef } from 'react'

export function QuantumCircuit3D() {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!containerRef.current) return

    import('three').then((THREE) => {
      const container = containerRef.current!
      const width = container.clientWidth
      const height = 500

      const scene = new THREE.Scene()
      scene.background = new THREE.Color(0x0a0e13)
      scene.fog = new THREE.Fog(0x0a0e13, 50, 100)

      const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000)
      camera.position.set(0, 0, 10)

      const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
      renderer.setSize(width, height)
      renderer.setPixelRatio(window.devicePixelRatio)
      container.appendChild(renderer.domElement)

      // Enhanced lighting
      const ambientLight = new THREE.AmbientLight(0xffffff, 0.4)
      scene.add(ambientLight)

      const pointLight1 = new THREE.PointLight(0x667eea, 1.5, 200)
      pointLight1.position.set(15, 15, 15)
      scene.add(pointLight1)

      const pointLight2 = new THREE.PointLight(0xf093fb, 1.2, 200)
      pointLight2.position.set(-15, -15, 15)
      scene.add(pointLight2)

      // Create Bloch sphere representation (background)
      const sphereGeometry = new THREE.SphereGeometry(6, 32, 32)
      const sphereMaterial = new THREE.MeshPhongMaterial({
        color: 0x667eea,
        wireframe: true,
        transparent: true,
        opacity: 0.1,
      })
      const blochSphere = new THREE.Mesh(sphereGeometry, sphereMaterial)
      scene.add(blochSphere)

      // Create coordinate axes
      const axesGroup = new THREE.Group()
      const axisLength = 7
      const axisThickness = 0.1

      // X axis (red)
      const xGeometry = new THREE.CylinderGeometry(axisThickness, axisThickness, axisLength, 16)
      const xMaterial = new THREE.MeshStandardMaterial({ color: 0xff4444 })
      const xAxis = new THREE.Mesh(xGeometry, xMaterial)
      xAxis.rotation.z = Math.PI / 2
      xAxis.position.x = axisLength / 2
      axesGroup.add(xAxis)

      // Y axis (green)
      const yGeometry = new THREE.CylinderGeometry(axisThickness, axisThickness, axisLength, 16)
      const yMaterial = new THREE.MeshStandardMaterial({ color: 0x44ff44 })
      const yAxis = new THREE.Mesh(yGeometry, yMaterial)
      yAxis.position.y = axisLength / 2
      axesGroup.add(yAxis)

      // Z axis (blue)
      const zGeometry = new THREE.CylinderGeometry(axisThickness, axisThickness, axisLength, 16)
      const zMaterial = new THREE.MeshStandardMaterial({ color: 0x667eea })
      const zAxis = new THREE.Mesh(zGeometry, zMaterial)
      zAxis.rotation.x = Math.PI / 2
      zAxis.position.z = axisLength / 2
      axesGroup.add(zAxis)

      scene.add(axesGroup)

      // Create quantum state vectors (animated)
      const vectors = []
      for (let i = 0; i < 3; i++) {
        const vectorGeometry = new THREE.CylinderGeometry(0.08, 0.08, 4, 16)
        const vectorMaterial = new THREE.MeshStandardMaterial({
          color: 0xf093fb,
          emissive: 0xf093fb,
          emissiveIntensity: 0.6,
          metalness: 0.4,
        })
        const vector = new THREE.Mesh(vectorGeometry, vectorMaterial)
        vector.userData.index = i
        vector.userData.angle = (i * Math.PI * 2) / 3
        vectors.push(vector)
        scene.add(vector)
      }

      // Create qubit nodes on the circuit
      const qubits = []
      const qubitPositions = [-5, 0, 5]
      qubitPositions.forEach((y, idx) => {
        const geometry = new THREE.SphereGeometry(0.5, 32, 32)
        const material = new THREE.MeshStandardMaterial({
          color: 0x667eea,
          emissive: 0x667eea,
          emissiveIntensity: 0.6,
          metalness: 0.4,
          roughness: 0.3,
        })
        const qubit = new THREE.Mesh(geometry, material)
        qubit.position.set(-8, y, 0)
        qubit.userData.index = idx
        qubits.push(qubit)
        scene.add(qubit)
      })

      // Create quantum gates
      const gates = []
      const gateConfigs = [
        { x: -3, y: -5, type: 'H', rotation: 0 },
        { x: -3, y: 0, type: 'CNOT', rotation: 0.5 },
        { x: 2, y: 5, type: 'RZ(θ)', rotation: 1 },
        { x: 5, y: -5, type: 'X', rotation: 1.5 },
        { x: 5, y: 0, type: 'U', rotation: 2 },
      ]

      gateConfigs.forEach((config) => {
        const geometry = new THREE.BoxGeometry(0.8, 0.8, 0.8)
        const material = new THREE.MeshStandardMaterial({
          color: 0xf093fb,
          emissive: 0xf093fb,
          emissiveIntensity: 0.4,
          metalness: 0.3,
          roughness: 0.5,
        })
        const gate = new THREE.Mesh(geometry, material)
        gate.position.set(config.x, config.y, 0)
        gate.userData.initialRotation = config.rotation
        gate.userData.type = config.type
        gates.push(gate)
        scene.add(gate)
      })

      // Create connecting wires
      const wirePositions = [
        [[-8, -5, 0], [8, -5, 0]],
        [[-8, 0, 0], [8, 0, 0]],
        [[-8, 5, 0], [8, 5, 0]],
      ]

      wirePositions.forEach((positions) => {
        const geometry = new THREE.BufferGeometry()
        geometry.setFromPoints(positions.map((p) => new THREE.Vector3(...p)))
        const lineMaterial = new THREE.LineBasicMaterial({ color: 0x667eea, linewidth: 3 })
        const line = new THREE.Line(geometry, lineMaterial)
        scene.add(line)
      })

      // Animation loop
      let animationFrameId: number
      const time = Date.now()
      const animate = () => {
        animationFrameId = requestAnimationFrame(animate)
        const elapsed = (Date.now() - time) * 0.001

        // Rotate Bloch sphere
        blochSphere.rotation.x += 0.0003
        blochSphere.rotation.z += 0.0005

        // Animate state vectors
        vectors.forEach((vector, i) => {
          const angle = vector.userData.angle + elapsed * 0.5
          const radius = 3
          vector.position.x = Math.cos(angle) * radius
          vector.position.y = Math.sin(angle) * radius
          vector.position.z = Math.cos(elapsed + i) * 0.5
          vector.lookAt(0, 0, 0)
          vector.rotation.x = Math.atan2(vector.position.y, vector.position.z)
        })

        // Rotate qubits
        qubits.forEach((qubit) => {
          qubit.rotation.x += 0.008
          qubit.rotation.y += 0.012
        })

        // Animate gates
        gates.forEach((gate, i) => {
          gate.rotation.x += 0.012
          gate.rotation.z += 0.015
          gate.position.z = Math.sin(elapsed * 0.7 + i) * 0.4
          const scale = 1 + Math.sin(elapsed * 0.8 + i * 0.5) * 0.1
          gate.scale.set(scale, scale, scale)
        })

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

  return <div ref={containerRef} className="w-full bg-black/30 rounded-lg overflow-hidden border border-gray-700" style={{ height: '500px' }} />
}
