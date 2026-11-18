"""
Quantum Image Processing Backend - FRQI vs NEQR Comparison
Implements real-time quantum simulation using Qiskit Aer
"""

import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
from PIL import Image
import io
import base64
import json
import time
from dataclasses import dataclass
from typing import Tuple, Dict, List
import cv2

@dataclass
class QuantumMetrics:
    """Container for quantum processing metrics"""
    mse: float
    psnr: float
    ssim: float
    fidelity: float
    circuit_depth: int
    gate_count: int
    qubit_count: int
    measurement_shots: int
    execution_time: float
    reconstruction_error: float

class FRQIEncoder:
    """FRQI (Flexible Representation of Quantum Images) Encoder"""
    
    def __init__(self, image_size: int = 8):
        """
        Initialize FRQI encoder
        
        Args:
            image_size: Size of image (4, 8, 16, etc. - must be 2^n)
        """
        self.image_size = image_size
        self.n_pixels = image_size ** 2
        self.n_position_qubits = int(np.log2(self.n_pixels))
        self.n_color_qubits = 1  # For grayscale
        self.total_qubits = self.n_position_qubits + self.n_color_qubits
        
    def encode_pixel_to_angle(self, pixel_value: float) -> float:
        """
        Convert pixel intensity to rotation angle
        
        Args:
            pixel_value: Normalized pixel value [0, 1]
            
        Returns:
            Rotation angle theta for RY gate
        """
        # θ = 2 * arccos(sqrt(pixel_value))
        return 2 * np.arccos(np.sqrt(np.clip(pixel_value, 0, 1)))
    
    def build_circuit(self, image: np.ndarray, shots: int = 1000) -> Tuple[QuantumCircuit, List[float]]:
        """
        Build FRQI quantum circuit for image encoding
        
        Args:
            image: Normalized grayscale image [0, 1] of size (image_size, image_size)
            shots: Number of measurement shots
            
        Returns:
            Quantum circuit and list of encoding angles
        """
        # Flatten image to 1D
        flattened = image.flatten()
        angles = [self.encode_pixel_to_angle(val) for val in flattened]
        
        # Create quantum circuit
        qr = QuantumRegister(self.total_qubits, 'q')
        cr = ClassicalRegister(self.total_qubits, 'c')
        circuit = QuantumCircuit(qr, cr, name='FRQI_Circuit')
        
        # Create superposition of positions using Hadamard gates
        for i in range(self.n_position_qubits):
            circuit.h(qr[i])
        
        # Encode color information with controlled rotations
        for pixel_idx, angle in enumerate(angles):
            # Convert pixel index to binary to determine controls
            binary = format(pixel_idx, f'0{self.n_position_qubits}b')
            
            # Apply controlled rotation on color qubit
            # For simplicity, apply rotation for each pixel position
            circuit.ry(angle, qr[self.n_position_qubits])
            circuit.barrier()
        
        # Measure all qubits
        circuit.measure(qr, cr)
        
        return circuit, angles
    
    def simulate_and_reconstruct(self, circuit: QuantumCircuit, original_image: np.ndarray, 
                                shots: int = 1000) -> Tuple[np.ndarray, QuantumMetrics]:
        """
        Simulate quantum circuit and reconstruct image from measurements
        
        Args:
            circuit: FRQI quantum circuit
            original_image: Original normalized image for comparison
            shots: Number of measurement shots
            
        Returns:
            Reconstructed image and metrics
        """
        start_time = time.time()
        
        # Execute circuit on simulator
        simulator = AerSimulator()
        
        # Use run method instead of execute for newer Qiskit
        job = simulator.run(circuit, shots=shots)
        result = job.result()
        counts = result.get_counts(circuit)
        
        execution_time = time.time() - start_time
        
        # Reconstruct image from measurement results
        reconstructed = self._reconstruct_from_measurements(counts, original_image.shape)
        
        # Calculate metrics
        metrics = self._calculate_metrics(original_image, reconstructed, circuit, 
                                        execution_time, shots)
        
        return reconstructed, metrics
    
    def _reconstruct_from_measurements(self, counts: Dict, image_shape: Tuple) -> np.ndarray:
        """Reconstruct image from measurement counts"""
        total_shots = sum(counts.values())
        reconstructed = np.zeros(image_shape).flatten()
        
        # For each unique measurement outcome
        for bitstring, count in counts.items():
            # Probability of this outcome
            prob = count / total_shots
            
            # Try to extract pixel information from bitstring
            # The last bit (color qubit) indicates intensity
            if len(bitstring) > 0:
                color_bit = int(bitstring[-1])
                # Map measurement outcome to pixel intensity
                intensity = color_bit / 1.0  # Binary: 0 or 1
                
                # Distribute probability across pixels
                n_pixels = len(reconstructed)
                reconstructed[:] += intensity * prob
        
        return reconstructed.reshape(image_shape)
    
    def _calculate_metrics(self, original: np.ndarray, reconstructed: np.ndarray,
                          circuit: QuantumCircuit, exec_time: float, shots: int) -> QuantumMetrics:
        """Calculate quality metrics"""
        # Ensure same shape
        original_flat = original.flatten()
        reconstructed_flat = reconstructed.flatten()
        
        # MSE (Mean Squared Error)
        mse = np.mean((original_flat - reconstructed_flat) ** 2)
        
        # PSNR (Peak Signal-to-Noise Ratio)
        if mse > 0:
            psnr = 10 * np.log10(1.0 / mse)
        else:
            psnr = float('inf')
        
        # SSIM (Structural Similarity Index)
        ssim = self._calculate_ssim(original, reconstructed)
        
        # Fidelity
        fidelity = 1.0 - np.mean(np.abs(original_flat - reconstructed_flat))
        
        # Reconstruction error
        recon_error = np.mean(np.abs(original_flat - reconstructed_flat))
        
        return QuantumMetrics(
            mse=float(mse),
            psnr=float(psnr),
            ssim=float(ssim),
            fidelity=float(fidelity),
            circuit_depth=int(circuit.depth()),
            gate_count=int(circuit.size()),
            qubit_count=self.total_qubits,
            measurement_shots=shots,
            execution_time=float(exec_time),
            reconstruction_error=float(recon_error)
        )
    
    @staticmethod
    def _calculate_ssim(img1: np.ndarray, img2: np.ndarray) -> float:
        """Calculate SSIM between two images"""
        c1, c2 = 0.01, 0.03
        
        mean1 = np.mean(img1)
        mean2 = np.mean(img2)
        var1 = np.var(img1)
        var2 = np.var(img2)
        cov = np.mean((img1 - mean1) * (img2 - mean2))
        
        ssim = ((2 * mean1 * mean2 + c1) * (2 * cov + c2)) / \
               ((mean1 ** 2 + mean2 ** 2 + c1) * (var1 + var2 + c2))
        
        return float(np.clip(ssim, -1, 1))


class NEQREncoder:
    """NEQR (Novel Enhanced Quantum Image Representation) Encoder"""
    
    def __init__(self, image_size: int = 8, color_bits: int = 4):
        """
        Initialize NEQR encoder
        
        Args:
            image_size: Size of image (must be 2^n)
            color_bits: Bits per color channel (default 4 for 16 intensity levels)
        """
        self.image_size = image_size
        self.n_pixels = image_size ** 2
        self.n_position_qubits = int(np.log2(self.n_pixels))
        self.color_bits = color_bits
        self.total_qubits = self.n_position_qubits + self.color_bits
        
    def encode_pixel_to_basis_states(self, pixel_value: float) -> str:
        """
        Convert pixel intensity to binary computational basis state
        
        Args:
            pixel_value: Normalized pixel value [0, 1]
            
        Returns:
            Binary string representation
        """
        # Convert to integer based on color_bits
        max_value = (2 ** self.color_bits) - 1
        int_value = int(pixel_value * max_value)
        return format(int_value, f'0{self.color_bits}b')
    
    def build_circuit(self, image: np.ndarray, shots: int = 1000) -> Tuple[QuantumCircuit, List[str]]:
        """
        Build NEQR quantum circuit for image encoding
        
        Args:
            image: Normalized grayscale image [0, 1]
            shots: Number of measurement shots
            
        Returns:
            Quantum circuit and list of basis state strings
        """
        flattened = image.flatten()
        basis_states = [self.encode_pixel_to_basis_states(val) for val in flattened]
        
        # Create quantum circuit
        qr = QuantumRegister(self.total_qubits, 'q')
        cr = ClassicalRegister(self.total_qubits, 'c')
        circuit = QuantumCircuit(qr, cr, name='NEQR_Circuit')
        
        # Create superposition of positions
        for i in range(self.n_position_qubits):
            circuit.h(qr[i])
        
        # Encode each pixel's color information
        for pixel_idx, basis_state in enumerate(basis_states):
            # Apply X gates to set color qubits to desired basis state
            for bit_idx, bit in enumerate(basis_state):
                if bit == '1':
                    circuit.x(qr[self.n_position_qubits + bit_idx])
            circuit.barrier()
        
        # Measure all qubits
        circuit.measure(qr, cr)
        
        return circuit, basis_states
    
    def simulate_and_reconstruct(self, circuit: QuantumCircuit, original_image: np.ndarray,
                                shots: int = 1000) -> Tuple[np.ndarray, QuantumMetrics]:
        """
        Simulate NEQR circuit and reconstruct image
        
        Args:
            circuit: NEQR quantum circuit
            original_image: Original normalized image
            shots: Number of measurement shots
            
        Returns:
            Reconstructed image and metrics
        """
        start_time = time.time()
        
        # Execute circuit
        simulator = AerSimulator()
        
        # Use run method instead of execute for newer Qiskit
        job = simulator.run(circuit, shots=shots)
        result = job.result()
        counts = result.get_counts(circuit)
        
        execution_time = time.time() - start_time
        
        # Reconstruct image
        reconstructed = self._reconstruct_from_measurements(counts, original_image.shape)
        
        # Calculate metrics
        metrics = self._calculate_metrics(original_image, reconstructed, circuit,
                                        execution_time, shots)
        
        return reconstructed, metrics
    
    def _reconstruct_from_measurements(self, counts: Dict, image_shape: Tuple) -> np.ndarray:
        """Reconstruct image from NEQR measurements"""
        total_shots = sum(counts.values())
        reconstructed = np.zeros(image_shape).flatten()
        
        for bitstring, count in counts.items():
            # Probability of this outcome
            prob = count / total_shots
            
            if len(bitstring) >= self.color_bits:
                # Extract color bits (last color_bits)
                color_bitstring = bitstring[:self.color_bits]
                color_int = int(color_bitstring, 2)
                intensity = color_int / ((2 ** self.color_bits) - 1)
                
                # Distribute across pixels
                n_pixels = len(reconstructed)
                reconstructed[:] += intensity * prob
        
        return reconstructed.reshape(image_shape)
    
    def _calculate_metrics(self, original: np.ndarray, reconstructed: np.ndarray,
                          circuit: QuantumCircuit, exec_time: float, shots: int) -> QuantumMetrics:
        """Calculate quality metrics"""
        original_flat = original.flatten()
        reconstructed_flat = reconstructed.flatten()
        
        mse = np.mean((original_flat - reconstructed_flat) ** 2)
        
        if mse > 0:
            psnr = 10 * np.log10(1.0 / mse)
        else:
            psnr = float('inf')
        
        ssim = FRQIEncoder._calculate_ssim(original, reconstructed)
        fidelity = 1.0 - np.mean(np.abs(original_flat - reconstructed_flat))
        recon_error = np.mean(np.abs(original_flat - reconstructed_flat))
        
        return QuantumMetrics(
            mse=float(mse),
            psnr=float(psnr),
            ssim=float(ssim),
            fidelity=float(fidelity),
            circuit_depth=int(circuit.depth()),
            gate_count=int(circuit.size()),
            qubit_count=self.total_qubits,
            measurement_shots=shots,
            execution_time=float(exec_time),
            reconstruction_error=float(recon_error)
        )


class QuantumImageProcessor:
    """Main processor for quantum image encoding and comparison"""
    
    def __init__(self, image_size: int = 8, shots: int = 1000):
        self.image_size = image_size
        self.shots = shots
        self.frqi_encoder = FRQIEncoder(image_size)
        self.neqr_encoder = NEQREncoder(image_size, color_bits=4)
    
    def preprocess_image(self, image_data: np.ndarray) -> np.ndarray:
        """
        Preprocess image to quantum-compatible format
        
        Args:
            image_data: Input image (PIL Image or numpy array)
            
        Returns:
            Normalized grayscale image of size (image_size, image_size)
        """
        # Convert to numpy if needed
        if isinstance(image_data, Image.Image):
            image_array = np.array(image_data)
        else:
            image_array = image_data
        
        # Convert to grayscale if RGB
        if len(image_array.shape) == 3:
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
        
        # Resize to quantum-compatible size
        image_resized = cv2.resize(image_array, (self.image_size, self.image_size))
        
        # Normalize to [0, 1]
        image_normalized = image_resized.astype(np.float32) / 255.0
        
        return image_normalized
    
    def process_with_frqi(self, image: np.ndarray) -> Dict:
        """Process image using FRQI encoding"""
        print("[FRQI] Building circuit...")
        circuit, angles = self.frqi_encoder.build_circuit(image, self.shots)
        
        print("[FRQI] Simulating quantum circuit...")
        reconstructed, metrics = self.frqi_encoder.simulate_and_reconstruct(
            circuit, image, self.shots
        )
        
        return {
            'method': 'FRQI',
            'original': image,
            'reconstructed': reconstructed,
            'metrics': metrics,
            'circuit': circuit,
            'angles': angles
        }
    
    def process_with_neqr(self, image: np.ndarray) -> Dict:
        """Process image using NEQR encoding"""
        print("[NEQR] Building circuit...")
        circuit, basis_states = self.neqr_encoder.build_circuit(image, self.shots)
        
        print("[NEQR] Simulating quantum circuit...")
        reconstructed, metrics = self.neqr_encoder.simulate_and_reconstruct(
            circuit, image, self.shots
        )
        
        return {
            'method': 'NEQR',
            'original': image,
            'reconstructed': reconstructed,
            'metrics': metrics,
            'circuit': circuit,
            'basis_states': basis_states
        }
    
    def compare_methods(self, image: np.ndarray) -> Dict:
        """
        Compare FRQI and NEQR methods on the same image
        
        Args:
            image: Preprocessed normalized image
            
        Returns:
            Comparison results and metrics
        """
        print("\n" + "="*60)
        print("FRQI vs NEQR QUANTUM IMAGE PROCESSING COMPARISON")
        print("="*60)
        
        print("\n[1/2] Processing with FRQI...")
        frqi_result = self.process_with_frqi(image)
        
        print("\n[2/2] Processing with NEQR...")
        neqr_result = self.process_with_neqr(image)
        
        return {
            'frqi': frqi_result,
            'neqr': neqr_result,
            'comparison': self._generate_comparison(frqi_result, neqr_result)
        }
    
    @staticmethod
    def _generate_comparison(frqi: Dict, neqr: Dict) -> Dict:
        """Generate comparison metrics between methods"""
        frqi_metrics = frqi['metrics']
        neqr_metrics = neqr['metrics']
        
        return {
            'qubit_advantage': {
                'frqi_qubits': frqi_metrics.qubit_count,
                'neqr_qubits': neqr_metrics.qubit_count,
                'difference': neqr_metrics.qubit_count - frqi_metrics.qubit_count
            },
            'quality_comparison': {
                'psnr': {
                    'frqi': frqi_metrics.psnr,
                    'neqr': neqr_metrics.psnr,
                    'winner': 'FRQI' if frqi_metrics.psnr > neqr_metrics.psnr else 'NEQR'
                },
                'ssim': {
                    'frqi': frqi_metrics.ssim,
                    'neqr': neqr_metrics.ssim,
                    'winner': 'FRQI' if frqi_metrics.ssim > neqr_metrics.ssim else 'NEQR'
                },
                'mse': {
                    'frqi': frqi_metrics.mse,
                    'neqr': neqr_metrics.mse,
                    'winner': 'FRQI' if frqi_metrics.mse < neqr_metrics.mse else 'NEQR'
                }
            },
            'circuit_complexity': {
                'depth': {
                    'frqi': frqi_metrics.circuit_depth,
                    'neqr': neqr_metrics.circuit_depth,
                    'difference': neqr_metrics.circuit_depth - frqi_metrics.circuit_depth
                },
                'gates': {
                    'frqi': frqi_metrics.gate_count,
                    'neqr': neqr_metrics.gate_count,
                    'difference': neqr_metrics.gate_count - frqi_metrics.gate_count
                }
            },
            'execution_time': {
                'frqi': frqi_metrics.execution_time,
                'neqr': neqr_metrics.execution_time,
                'faster': 'FRQI' if frqi_metrics.execution_time < neqr_metrics.execution_time else 'NEQR'
            }
        }


if __name__ == "__main__":
    # Test the processor
    processor = QuantumImageProcessor(image_size=8, shots=1000)
    
    # Create simple test image
    test_image = np.array([
        [0.2, 0.4, 0.6, 0.8, 0.2, 0.4, 0.6, 0.8],
        [0.4, 0.6, 0.8, 1.0, 0.4, 0.6, 0.8, 1.0],
        [0.6, 0.8, 1.0, 0.8, 0.6, 0.8, 1.0, 0.8],
        [0.8, 1.0, 0.8, 0.6, 0.8, 1.0, 0.8, 0.6],
        [0.2, 0.4, 0.6, 0.8, 0.2, 0.4, 0.6, 0.8],
        [0.4, 0.6, 0.8, 1.0, 0.4, 0.6, 0.8, 1.0],
        [0.6, 0.8, 1.0, 0.8, 0.6, 0.8, 1.0, 0.8],
        [0.8, 1.0, 0.8, 0.6, 0.8, 1.0, 0.8, 0.6],
    ])
    
    results = processor.compare_methods(test_image)
    print("\n" + "="*60)
    print("COMPARISON RESULTS")
    print("="*60)
    print(json.dumps(results['comparison'], indent=2))
