"""
Quantum measurement result processing.
Converts quantum measurements to image probability data.
"""

import numpy as np
from typing import Dict, Tuple, List
from collections import Counter


class MeasurementProcessor:
    """Processes quantum measurement results."""
    
    def __init__(self, num_qubits: int, image_size: Tuple[int, int]):
        """
        Initialize measurement processor.
        
        Args:
            num_qubits: Number of qubits measured
            image_size: Target image size (height, width)
        """
        self.num_qubits = num_qubits
        self.image_height, self.image_width = image_size
        self.num_pixels = image_size[0] * image_size[1]
    
    def process_counts(self, counts: Dict[str, int]) -> np.ndarray:
        """
        Convert measurement counts to pixel intensity estimates.
        
        Args:
            counts: Dictionary {bitstring: count}
                   e.g., {'00': 250, '01': 125, '10': 125, '11': 500}
        
        Returns:
            1D array of pixel intensities (probabilities)
        """
        total_shots = sum(counts.values())
        
        # Create probability array
        num_states = 2 ** self.num_qubits
        probabilities = np.zeros(num_states)
        
        # Convert each bitstring to probability
        for bitstring, count in counts.items():
            index = int(bitstring, 2)  # Convert binary string to decimal
            probabilities[index] = count / total_shots
        
        return probabilities
    
    def bitstring_to_index(self, bitstring: str) -> int:
        """
        Convert bitstring to pixel index.
        
        Args:
            bitstring: Binary string (e.g., "0110")
            
        Returns:
            Linear pixel index
        """
        if len(bitstring) != self.num_qubits:
            raise ValueError(f"Bitstring length {len(bitstring)} != {self.num_qubits}")
        
        return int(bitstring, 2)
    
    def index_to_coordinates(self, index: int) -> Tuple[int, int]:
        """
        Convert pixel index to image coordinates.
        
        Args:
            index: Linear pixel index
            
        Returns:
            (row, col) tuple
        """
        if index >= self.num_pixels:
            raise ValueError(f"Index {index} >= {self.num_pixels}")
        
        row = index // self.image_width
        col = index % self.image_width
        return row, col
    
    def bitstring_to_coordinates(self, bitstring: str) -> Tuple[int, int]:
        """
        Convert bitstring directly to image coordinates.
        
        Args:
            bitstring: Binary string
            
        Returns:
            (row, col) tuple
        """
        index = self.bitstring_to_index(bitstring)
        return self.index_to_coordinates(index)
    
    def get_fidelity(self, ideal_probs: np.ndarray, 
                    measured_probs: np.ndarray) -> float:
        """
        Calculate fidelity between ideal and measured probability distributions.
        
        Fidelity = (Σ √(p_i · q_i))²
        
        Args:
            ideal_probs: Ideal probability distribution
            measured_probs: Measured probability distribution
            
        Returns:
            Fidelity value (0 to 1; 1 = identical)
        """
        if len(ideal_probs) != len(measured_probs):
            raise ValueError("Probability distributions have different lengths")
        
        # Normalize
        ideal_probs = np.asarray(ideal_probs)
        measured_probs = np.asarray(measured_probs)
        
        ideal_probs = ideal_probs / (np.sum(ideal_probs) + 1e-10)
        measured_probs = measured_probs / (np.sum(measured_probs) + 1e-10)
        
        # Calculate fidelity
        fidelity = np.sum(np.sqrt(ideal_probs * measured_probs)) ** 2
        
        return float(np.clip(fidelity, 0, 1))
    
    def get_measurement_statistics(self, counts: Dict[str, int]) -> dict:
        """
        Calculate statistics from measurement results.
        
        Args:
            counts: Measurement counts
            
        Returns:
            Dictionary with statistics
        """
        total_shots = sum(counts.values())
        probs = self.process_counts(counts)
        
        return {
            "total_shots": total_shots,
            "num_distinct_outcomes": len(counts),
            "max_probability": np.max(probs),
            "min_probability": np.min(probs),
            "mean_probability": np.mean(probs),
            "std_probability": np.std(probs),
            "entropy": self._calculate_entropy(probs),
        }
    
    @staticmethod
    def _calculate_entropy(probabilities: np.ndarray) -> float:
        """
        Calculate Shannon entropy of probability distribution.
        
        Args:
            probabilities: Probability distribution
            
        Returns:
            Entropy value (bits)
        """
        # Remove zero probabilities
        nonzero = probabilities[probabilities > 0]
        
        # Calculate entropy
        entropy = -np.sum(nonzero * np.log2(nonzero + 1e-10))
        
        return float(entropy)


class CountsSimulator:
    """Simulate measurement counts from a probability distribution."""
    
    @staticmethod
    def simulate_counts(probabilities: np.ndarray, shots: int, 
                       seed: int = None) -> Dict[str, int]:
        """
        Simulate measurement counts from probability distribution.
        
        Args:
            probabilities: Probability distribution (sums to 1)
            shots: Number of shots
            seed: Random seed for reproducibility
            
        Returns:
            Dictionary {bitstring: count}
        """
        if seed is not None:
            np.random.seed(seed)
        
        # Ensure probabilities sum to 1
        probs_normalized = probabilities / np.sum(probabilities)
        
        # Sample outcomes
        num_outcomes = len(probabilities)
        outcomes = np.random.choice(num_outcomes, size=shots, p=probs_normalized)
        
        # Count outcomes
        unique, counts = np.unique(outcomes, return_counts=True)
        
        # Convert to bitstring dictionary
        num_qubits = int(np.log2(num_outcomes))
        counts_dict = {}
        for index, count in zip(unique, counts):
            bitstring = format(int(index), f'0{num_qubits}b')
            counts_dict[bitstring] = int(count)
        
        return counts_dict


if __name__ == "__main__":
    # Quick test
    num_qubits = 2
    image_size = (2, 2)
    processor = MeasurementProcessor(num_qubits, image_size)
    
    # Simulate measurement counts
    ideal_probs = np.array([0.25, 0.25, 0.25, 0.25])  # Uniform
    counts = CountsSimulator.simulate_counts(ideal_probs, shots=1000, seed=42)
    
    print(f"Measurement counts: {counts}")
    
    # Process counts
    measured_probs = processor.process_counts(counts)
    print(f"Measured probabilities: {measured_probs}")
    
    # Calculate fidelity
    fidelity = processor.get_fidelity(ideal_probs, measured_probs)
    print(f"Fidelity: {fidelity:.4f}")
    
    # Get statistics
    stats = processor.get_measurement_statistics(counts)
    print(f"\nMeasurement statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
