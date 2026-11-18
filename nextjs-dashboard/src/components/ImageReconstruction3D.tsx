'use client'

import { useEffect, useRef } from 'react'

export function ImageReconstruction3D() {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!containerRef.current) return

    import('three').then((THREE) => {
      const container = containerRef.current!
      const width = container.clientWidth
      const height = 500

      const scene = new THREE.Scene()
      scene.background = new THREE.Color(0x0a0e13)

      const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000)
      camera.position.set(0, 5, 12)
      camera.lookAt(0, 0, 0)

      const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
      renderer.setSize(width, height)
      renderer.setPixelRatio(window.devicePixelRatio)
      container.appendChild(renderer.domElement)

      // Lighting
      const ambientLight = new THREE.AmbientLight(0xffffff, 0.5)
      scene.add(ambientLight)

      const pointLight1 = new THREE.PointLight(0x667eea, 1.2, 150)
      pointLight1.position.set(20, 20, 20)
      scene.add(pointLight1)

      const pointLight2 = new THREE.PointLight(0xf093fb, 1, 150)
      pointLight2.position.set(-20, -20, 20)
      scene.add(pointLight2)

      // Create amplitude encoding visualization (bars)
      const amplitudes = []
      const gridSize = 4
      for (let i = 0; i < gridSize; i++) {
        for (let j = 0; j < gridSize; j++) {
          const height = Math.random() * 3 + 0.5
          const geometry = new THREE.BoxGeometry(0.8, height, 0.8)
          const material = new THREE.MeshStandardMaterial({
            color: new THREE.Color().setHSL(0.6 + (i + j) * 0.02, 0.8, 0.5),
            emissive: new THREE.Color().setHSL(0.6 + (i + j) * 0.02, 0.8, 0.3),
            emissiveIntensity: 0.4,
            metalness: 0.3,
            roughness: 0.5,
          })
          const bar = new THREE.Mesh(geometry, material)
          const xPos = (i - gridSize / 2) * 1.2
          const zPos = (j - gridSize / 2) * 1.2
          bar.position.set(xPos, height / 2, zPos)
          bar.userData.originalHeight = height
          bar.userData.index = i * gridSize + j
          amplitudes.push(bar)
          scene.add(bar)
        }
      }

      // Create quantum state visualization (sphere with intensity mapping)
      const stateGeometry = new THREE.IcosahedronGeometry(2, 5)
      const stateVertices = stateGeometry.getAttribute('position')
      const vertexColors = new Float32Array(stateVertices.count * 3)

      for (let i = 0; i < stateVertices.count; i++) {
        const x = stateVertices.getX(i)
        const y = stateVertices.getY(i)
        const z = stateVertices.getZ(i)
        const intensity = (x + y + z + 3) / 6

        const color = new THREE.Color().setHSL(0.6, 0.8, intensity)
        vertexColors[i * 3] = color.r
        vertexColors[i * 3 + 1] = color.g
        vertexColors[i * 3 + 2] = color.b
      }

      stateGeometry.setAttribute('color', new THREE.BufferAttribute(vertexColors, 3))
      const stateMaterial = new THREE.MeshPhongMaterial({
        vertexColors: true,
        wireframe: false,
        emissive: 0x667eea,
        emissiveIntensity: 0.3,
      })
      const quantumState = new THREE.Mesh(stateGeometry, stateMaterial)
      quantumState.position.set(0, 0, 0)
      scene.add(quantumState)

      // Create measurement basis vectors
      const basisVectors = []
      const basisConfigs = [
        { dir: [1, 0, 0], color: 0xff4444, label: 'X' },
        { dir: [0, 1, 0], color: 0x44ff44, label: 'Y' },
        { dir: [0, 0, 1], color: 0x667eea, label: 'Z' },
      ]

      basisConfigs.forEach((config) => {
        const arrowGeometry = new THREE.CylinderGeometry(0.1, 0.1, 2.5, 16)
        const arrowMaterial = new THREE.MeshStandardMaterial({
          color: config.color,
          emissive: config.color,
          emissiveIntensity: 0.6,
        })
        const arrow = new THREE.Mesh(arrowGeometry, arrowMaterial)

        const headGeometry = new THREE.ConeGeometry(0.25, 0.5, 16)
        const headMesh = new THREE.Mesh(headGeometry, arrowMaterial)
        headMesh.position.set(config.dir[0] * 1.5, config.dir[1] * 1.5, config.dir[2] * 1.5)
        headMesh.rotation.set(config.dir[1] ? Math.PI / 2 : 0, config.dir[2] ? Math.PI / 2 : 0, 0)

        arrow.position.set(config.dir[0] * 0.75, config.dir[1] * 0.75, config.dir[2] * 0.75)
        if (config.dir[0] !== 0) arrow.rotation.z = Math.PI / 2
        if (config.dir[1] === 0 && config.dir[2] !== 0) arrow.rotation.x = Math.PI / 2

        const group = new THREE.Group()
        group.add(arrow)
        group.add(headMesh)
        basisVectors.push(group)
        scene.add(group)
      })

      // Create reconstructed image plane
      const canvas = document.createElement('canvas')
      canvas.width = 256
      canvas.height = 256
      const ctx = canvas.getContext('2d')!
      const imageData = ctx.createImageData(256, 256)
      const data = imageData.data

      for (let i = 0; i < data.length; i += 4) {
        const val = Math.random() * 255
        data[i] = val * 0.5 + 102 // R
        data[i + 1] = val * 0.3 + 50 // G
        data[i + 2] = val + 50 // B
        data[i + 3] = 255 // A
      }

      ctx.putImageData(imageData, 0, 0)
      const texture = new THREE.CanvasTexture(canvas)

      const planeGeometry = new THREE.PlaneGeometry(5, 5)
      const planeMaterial = new THREE.MeshStandardMaterial({
        map: texture,
        metalness: 0.1,
        roughness: 0.8,
      })
      const reconstructedPlane = new THREE.Mesh(planeGeometry, planeMaterial)
      reconstructedPlane.position.set(8, 0, 0)
      scene.add(reconstructedPlane)

      // Animation
      let animationFrameId: number
      const startTime = Date.now()

      const animate = () => {
        animationFrameId = requestAnimationFrame(animate)
        const elapsed = (Date.now() - startTime) * 0.001

        // Animate amplitude bars
        amplitudes.forEach((bar, i) => {
          const oscillation = Math.sin(elapsed * 0.8 + i * 0.1) * 0.5 + 0.5
          const newHeight = bar.userData.originalHeight * (0.7 + oscillation * 0.3)
          bar.scale.y = newHeight / bar.userData.originalHeight
          bar.position.y = newHeight / 2
        })

        // Rotate quantum state sphere
        quantumState.rotation.x += 0.003
        quantumState.rotation.y += 0.005

        // Rotate measurement bases
        basisVectors.forEach((basis, i) => {
          basis.rotation.x += 0.008
          basis.rotation.z += 0.012
        })

        // Rotate reconstructed plane
        reconstructedPlane.rotation.y += 0.003
        reconstructedPlane.position.z = Math.sin(elapsed * 0.3) * 0.5

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
