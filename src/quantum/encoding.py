"""
Quantum image encoding module.
Converts classical images into quantum state amplitudes.
"""

import numpy as np
from typing import Tuple, Optional


class AmplitudeEncoder:
    """
    Encodes images as quantum state amplitudes.
    
    Mathematical Representation:
        |ψ⟩ = (1/√Z) Σ √(I_i) |i⟩
        
        where:
        - I_i: pixel intensity at position i
        - Z: normalization constant (sum of pixels)
        - |i⟩: computational basis state
    
    Example:
        encoder = AmplitudeEncoder(image, num_qubits=4)
        amplitudes = encoder.encode()
    """
    
    def __init__(self, image: np.ndarray, num_qubits: Optional[int] = None):
        """
        Initialize amplitude encoder.
        
        Args:
            image: 2D image array (normalized [0,1])
            num_qubits: Number of qubits (calculated if None)
        """
        self.image = np.asarray(image, dtype=float)
        
        if len(self.image.shape) != 2:
            raise ValueError(f"Image must be 2D, got shape {self.image.shape}")
        
        self.height, self.width = self.image.shape
        self.num_pixels = self.height * self.width
        
        # Calculate required qubits
        self.num_qubits = num_qubits or self._calculate_qubits()
        self.num_states = 2 ** self.num_qubits
        
        if self.num_states < self.num_pixels:
            raise ValueError(
                f"Insufficient qubits ({self.num_qubits}) for {self.num_pixels} pixels. "
                f"Need at least {np.ceil(np.log2(self.num_pixels)).astype(int)} qubits."
            )
    
    def _calculate_qubits(self) -> int:
        """Calculate minimum qubits needed for image."""
        if self.num_pixels == 0:
            return 1
        return int(np.ceil(np.log2(self.num_pixels)))
    
    def encode(self) -> np.ndarray:
        """
        Encode image as quantum state amplitudes.
        
        Returns:
            Complex amplitude vector of size 2^num_qubits
        """
        # Flatten and normalize
        pixels_flat = self.image.flatten()
        
        # Pad with zeros if needed
        if len(pixels_flat) < self.num_states:
            pixels_padded = np.zeros(self.num_states)
            pixels_padded[:len(pixels_flat)] = pixels_flat
        else:
            pixels_padded = pixels_flat
        
        # Calculate normalization constant
        norm_factor = self.get_normalization_factor()
        
        if norm_factor == 0:
            # All black image
            amplitudes = np.zeros(self.num_states, dtype=complex)
            amplitudes[0] = 1.0  # Ground state
            return amplitudes
        
        # Calculate amplitudes: sqrt(I_i / Z)
        amplitudes = np.sqrt(pixels_padded / norm_factor)
        
        # Verify normalization
        total_prob = np.sum(np.abs(amplitudes) ** 2)
        if not np.isclose(total_prob, 1.0, atol=1e-10):
            amplitudes = amplitudes / np.sqrt(total_prob)
        
        return amplitudes.astype(complex)
    
    def get_normalization_factor(self) -> float:
        """
        Calculate normalization constant Z = Σ I_i.
        
        Returns:
            Sum of all pixel intensities
        """
        return float(np.sum(self.image))
    
    def get_required_qubits(self, image_size: Tuple[int, int]) -> int:
        """
        Calculate qubits required for image size.
        
        Args:
            image_size: (height, width) tuple
            
        Returns:
            Number of qubits needed
        """
        num_pixels = image_size[0] * image_size[1]
        if num_pixels == 0:
            return 1
        return int(np.ceil(np.log2(num_pixels)))
    
    def get_state_vector(self) -> np.ndarray:
        """
        Get full quantum state vector.
        
        Returns:
            Complex vector representing |ψ⟩
        """
        return self.encode()
    
    def verify_encoding(self) -> bool:
        """
        Verify encoding is normalized and valid.
        
        Returns:
            True if encoding is valid, False otherwise
        """
        amplitudes = self.encode()
        
        # Check normalization
        norm = np.sum(np.abs(amplitudes) ** 2)
        if not np.isclose(norm, 1.0, atol=1e-10):
            return False
        
        # Check no NaN or Inf
        if np.any(np.isnan(amplitudes)) or np.any(np.isinf(amplitudes)):
            return False
        
        return True
    
    def get_measurement_probabilities(self) -> np.ndarray:
        """
        Get measurement probabilities for each basis state.
        
        Returns:
            Probability distribution (sum to 1)
        """
        amplitudes = self.encode()
        probabilities = np.abs(amplitudes) ** 2
        return probabilities / np.sum(probabilities)


def amplitude_from_intensity(intensity: float, norm_factor: float) -> float:
    """
    Convert pixel intensity to quantum amplitude.
    
    Args:
        intensity: Pixel value [0, 1]
        norm_factor: Normalization constant
        
    Returns:
        Amplitude value
    """
    if norm_factor == 0:
        return 0.0
    return np.sqrt(intensity / norm_factor)


def intensity_from_probability(probability: float) -> float:
    """
    Convert measurement probability to intensity.
    
    Args:
        probability: Measurement outcome probability
        
    Returns:
        Reconstructed intensity value [0, 1]
    """
    return float(probability)


def index_to_coordinates(index: int, height: int, width: int) -> Tuple[int, int]:
    """
    Convert linear index to 2D image coordinates.
    
    Args:
        index: Linear index (0 to height*width-1)
        height: Image height
        width: Image width
        
    Returns:
        (row, col) coordinates
    """
    row = index // width
    col = index % width
    return row, col


def coordinates_to_index(row: int, col: int, width: int) -> int:
    """
    Convert 2D image coordinates to linear index.
    
    Args:
        row: Row coordinate
        col: Column coordinate
        width: Image width
        
    Returns:
        Linear index
    """
    return row * width + col


if __name__ == "__main__":
    # Quick test
    from src.preprocessing.dataset import Dataset
    
    dataset = Dataset()
    image = dataset.generate_checkerboard(4, save=False)
    
    encoder = AmplitudeEncoder(image)
    amplitudes = encoder.encode()
    probs = encoder.get_measurement_probabilities()
    
    print(f"Image shape: {image.shape}")
    print(f"Number of qubits: {encoder.num_qubits}")
    print(f"Number of basis states: {encoder.num_states}")
    print(f"Normalization factor: {encoder.get_normalization_factor():.4f}")
    print(f"Encoding valid: {encoder.verify_encoding()}")
    print(f"Amplitude vector shape: {amplitudes.shape}")
    print(f"Probabilities sum: {np.sum(probs):.6f}")
    print(f"Max probability: {np.max(probs):.6f}")
