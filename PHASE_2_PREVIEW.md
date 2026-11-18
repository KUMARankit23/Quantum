# Phase 2: Quantum Implementation - Preview & Planning

## Overview

Phase 2 will implement the core quantum components:
- Amplitude encoding
- Quantum circuit construction  
- State preparation circuits
- Measurement and reconstruction
- Noise models

---

## Quantum Image Representation

### Amplitude Encoding Formula

For an n×n image with pixels [I₀, I₁, ..., I_{N-1}] where N = n²:

```
|ψ_image⟩ = (1/√Z) Σ√(I_i) |i⟩

where:
  Z = Σ I_i (normalization factor)
  i = pixel index (0 to N-1)
  |i⟩ = computational basis state |i_k i_{k-1} ... i_1 i_0⟩
```

### Qubit Requirements

| Image Size | Pixels | Qubits | Basis States |
|-----------|--------|--------|-------------|
| 2×2 | 4 | 2 | 4 |
| 4×4 | 16 | 4 | 16 |
| 8×8 | 64 | 6 | 64 |
| 16×16 | 256 | 8 | 256 |

### Measurement & Reconstruction

1. **Measurement**: Measure all qubits in computational basis
2. **Count Results**: For each basis state |i⟩, count occurrences
3. **Estimate Intensities**: I_i ≈ count(|i⟩) / total_shots
4. **Normalize**: Scale reconstructed intensities back to [0,1]

---

## Module Architecture

### `src/quantum/encoding.py`

```python
class AmplitudeEncoder:
    """Encodes images as quantum state amplitudes."""
    
    def __init__(self, image: np.ndarray, num_qubits: int):
        self.image = image
        self.num_qubits = num_qubits
        
    def encode(self) -> np.ndarray:
        """Convert image to quantum state amplitudes."""
        # Flatten image
        # Normalize to sum to 1
        # Take square roots of normalized pixels
        # Return as amplitudes
        
    def get_normalization_factor(self) -> float:
        """Calculate normalization constant Z."""
        
    def get_required_qubits(self, size: int) -> int:
        """Calculate required qubits for n×n image."""
```

### `src/quantum/circuit_builder.py`

```python
class CircuitBuilder:
    """Builds quantum circuits for image processing."""
    
    def __init__(self, encoding_method: str = "amplitude"):
        self.encoding_method = encoding_method
        
    def build_state_preparation(self, image: np.ndarray) -> QuantumCircuit:
        """Create state preparation circuit."""
        # Initialize circuit
        # Add state preparation gates
        # Return circuit
        
    def build_processing_circuit(self, circuit: QuantumCircuit, 
                                circuit_type: str = "basic") -> QuantumCircuit:
        """Add optional processing gates."""
        # basic: minimal gates
        # medium: some entanglement
        # deep: multiple layers
        
    def add_measurement(self, circuit: QuantumCircuit) -> QuantumCircuit:
        """Add measurement operations."""
```

### `src/quantum/state_prep.py`

```python
def prepare_amplitude_encoding_circuit(amplitudes: np.ndarray) -> QuantumCircuit:
    """Create state preparation circuit from amplitudes."""
    # Use controlled rotations
    # Use SWAP gates if needed
    # Minimize circuit depth
    
def angle_from_amplitude(amplitude: float) -> float:
    """Convert amplitude to rotation angle."""
    
def controlled_amplitude_gate(circuit: QuantumCircuit, 
                            control: int, 
                            target: int, 
                            angle: float) -> None:
    """Apply controlled amplitude encoding gate."""
```

### `src/quantum/noise_models.py`

```python
class NoiseModelFactory:
    """Creates Qiskit noise models."""
    
    @staticmethod
    def create_bitflip_noise(probability: float) -> NoiseModel:
        """Create bit-flip noise model."""
        
    @staticmethod
    def create_phaseflip_noise(probability: float) -> NoiseModel:
        """Create phase-flip noise model."""
        
    @staticmethod
    def create_depolarizing_noise(probability: float) -> NoiseModel:
        """Create depolarizing noise model."""
        
    @staticmethod
    def create_readout_noise(probability: float) -> NoiseModel:
        """Create measurement/readout noise model."""
```

### `src/reconstruction/measurement_processor.py`

```python
class MeasurementProcessor:
    """Processes quantum measurement results."""
    
    def __init__(self, num_qubits: int, image_size: int):
        self.num_qubits = num_qubits
        self.image_size = image_size
        
    def process_counts(self, counts: Dict[str, int]) -> np.ndarray:
        """Convert measurement counts to pixel probabilities."""
        
    def bitstring_to_coordinates(self, bitstring: str) -> Tuple[int, int]:
        """Convert bitstring to (row, col) coordinates."""
        
    def get_fidelity(self, original_state: np.ndarray, 
                    measured_state: np.ndarray) -> float:
        """Calculate fidelity between states."""
```

### `src/reconstruction/image_reconstructor.py`

```python
class ImageReconstructor:
    """Reconstructs images from quantum measurements."""
    
    def reconstruct(self, measurement_data: np.ndarray, 
                   image_size: int) -> np.ndarray:
        """Convert measurement data to image."""
        
    def handle_missing_outcomes(self, image: np.ndarray) -> np.ndarray:
        """Interpolate missing measurement outcomes."""
        
    def normalize_reconstruction(self, image: np.ndarray) -> np.ndarray:
        """Normalize reconstructed image to [0,1]."""
```

---

## Phase 2 Implementation Plan

### Step 1: Encoding (Priority 1)
```
Target: Implement amplitude encoding
Time: ~2-3 hours
Tests: 
  - Verify orthonormality of encoded states
  - Check amplitude correctness
  - Test with checkerboard and gradient images
```

### Step 2: Circuit Builder (Priority 1)
```
Target: Build state preparation circuits
Time: ~2-3 hours
Tests:
  - Verify circuit depth ∝ log₂(n)
  - Check gate count scaling
  - Visual circuit inspection
```

### Step 3: Simulator Integration (Priority 2)
```
Target: Execute circuits with Qiskit Aer
Time: ~1-2 hours
Tests:
  - Run state preparation circuit
  - Collect measurement results
  - Verify measurement probabilities
```

### Step 4: Measurement Processing (Priority 2)
```
Target: Convert measurements to pixel values
Time: ~1-2 hours
Tests:
  - Verify probability sum to 1
  - Check reconstruction accuracy
  - Compare to original image
```

### Step 5: Noise Models (Priority 3)
```
Target: Add noise simulation
Time: ~1-2 hours
Tests:
  - Verify noise probability parameters
  - Check quality degradation
  - Compare noise types
```

---

## Key Implementation Details

### Amplitude Encoding Algorithm

```python
def amplitude_encode(image: np.ndarray) -> np.ndarray:
    """
    Step 1: Flatten to 1D
    Step 2: Normalize so sum = 1
    Step 3: Take element-wise sqrt
    Return: Amplitudes for quantum state
    """
    pixels = image.flatten()
    norm = np.sum(pixels)
    normalized = pixels / norm if norm > 0 else pixels
    amplitudes = np.sqrt(normalized)
    return amplitudes
```

### Circuit Depth

For amplitude encoding with controlled rotations:
- **Optimal depth**: O(log₂ n) for n states
- **2 qubits (4 states)**: depth 1
- **4 qubits (16 states)**: depth 4
- **6 qubits (64 states)**: depth 6
- **8 qubits (256 states)**: depth 8

### Measurement Reconstruction

```python
def reconstruct_image(counts: Dict[str, int], 
                     image_size: int) -> np.ndarray:
    """
    For each measured basis state:
      bitstring → decimal index → pixel coordinate
      frequency[bitstring] → estimated pixel intensity
    Reshape to 2D image
    Normalize to [0,1]
    """
```

---

## Expected Intermediate Results

### Ideal Case (No Noise)
```
Original checkerboard:      Reconstructed checkerboard:
[1 0 1 0]                   [1.0 0.0 0.9 0.1]
[0 1 0 1]                   [0.0 1.0 0.1 0.9]
[1 0 1 0]         ≈>        [0.9 0.1 1.0 0.0]
[0 1 0 1]                   [0.1 0.9 0.0 1.0]

Metrics:
  MSE ≈ 0.01 (small numerical error)
  PSNR ≈ 40 dB (good quality)
  SSIM ≈ 0.99 (very similar)
```

### With Noise (10% depolarizing)
```
Original:                   Reconstructed (noisy):
[1 0 1 0]                   [0.8 0.2 0.7 0.3]
[0 1 0 1]         ≈>        [0.2 0.8 0.3 0.7]
[1 0 1 0]                   [0.6 0.4 0.8 0.2]
[0 1 0 1]                   [0.4 0.6 0.2 0.8]

Metrics:
  MSE ≈ 0.05 (moderate error)
  PSNR ≈ 23 dB (acceptable)
  SSIM ≈ 0.85 (perceptibly different)
```

---

## Testing Strategy for Phase 2

### Unit Tests

```python
# test_encoding.py
def test_amplitude_normalization():
    image = np.array([[1, 0], [0, 1]])
    amplitudes = amplitude_encode(image)
    assert np.isclose(np.sum(amplitudes**2), 1.0)

def test_circuit_depth():
    circuit = build_state_prep(4, 4)  # 4x4 image
    assert circuit.depth() <= 6  # Should be O(log n)

def test_reconstruction_accuracy():
    original = checkerboard(4)
    # ... run quantum pipeline ...
    reconstructed = reconstruct()
    mse = calculate_mse(original, reconstructed)
    assert mse < 0.1  # No noise, should be accurate

# test_noise_models.py
def test_noise_reduces_quality():
    ideal_mse = calculate_mse(original, ideal_reconstruction)
    noisy_mse = calculate_mse(original, noisy_reconstruction)
    assert noisy_mse > ideal_mse  # Noise should degrade
```

### Integration Tests

```python
def test_full_pipeline():
    """Test complete quantum pipeline."""
    # Load image
    image = Dataset().generate_checkerboard(4)
    
    # Encode
    encoder = AmplitudeEncoder(image, 4)
    state = encoder.encode()
    
    # Build circuit
    builder = CircuitBuilder()
    circuit = builder.build_state_preparation(image)
    
    # Execute
    result = execute_circuit(circuit, shots=1000)
    
    # Reconstruct
    reconstructor = ImageReconstructor()
    reconstructed = reconstructor.reconstruct(result, 4)
    
    # Evaluate
    metrics = calculate_all_metrics(image, reconstructed)
    assert metrics['psnr'] > 20  # Should be good quality
    assert metrics['ssim'] > 0.8
```

---

## Progress Checklist for Phase 2

### Encoding Module
- [ ] Implement `amplitude_encode()` function
- [ ] Implement `AmplitudeEncoder` class
- [ ] Test normalization
- [ ] Test with checkerboard
- [ ] Test with gradient
- [ ] Test with random images
- [ ] Unit tests passing

### Circuit Building
- [ ] Implement state preparation circuits
- [ ] Implement controlled rotation gates
- [ ] Test circuit depth scaling
- [ ] Test gate counts
- [ ] Visual circuit inspection (QASM)
- [ ] Unit tests passing

### Simulator Integration
- [ ] Connect to Qiskit Aer
- [ ] Execute state prep circuits
- [ ] Collect measurement counts
- [ ] Verify measurement statistics
- [ ] Integration tests passing

### Reconstruction
- [ ] Convert counts to probabilities
- [ ] Map to pixel coordinates
- [ ] Handle edge cases (missing outcomes)
- [ ] Normalize reconstruction
- [ ] Reconstruction tests passing

### Noise Models
- [ ] Implement bit-flip noise
- [ ] Implement phase-flip noise
- [ ] Implement depolarizing noise
- [ ] Implement readout noise
- [ ] Verify noise effects degradation
- [ ] Noise tests passing

---

## Expected Completion

**Phase 2 Estimated Duration**: 3-4 days
- Encoding: 1 day
- Circuit building: 1 day
- Simulator integration: 0.5 day
- Reconstruction: 0.5 day
- Noise models: 0.5 day
- Testing & debugging: 0.5-1 day

**Upon Completion**:
- Quantum pipeline fully functional
- Can run single experiments
- Ready for Phase 3 (controlled experiments)

---

## Ready for Phase 2?

- ✓ Phase 1 foundation complete
- ✓ Test images ready
- ✓ Metrics system ready
- ✓ Configuration system ready
- ✓ Classical baseline ready

**Start Phase 2 implementation now →**
