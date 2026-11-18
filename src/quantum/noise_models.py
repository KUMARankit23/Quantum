"""
Quantum noise model definitions for simulation.
Supports various realistic noise scenarios (with mock fallback).
"""

import numpy as np
from typing import Optional

# Try importing from Qiskit Aer, fallback to mock
try:
    from qiskit_aer.noise import NoiseModel, pauli_error, depolarizing_error, ReadoutError
    NOISE_AVAILABLE = True
except ImportError:
    NOISE_AVAILABLE = False
    print("[INFO] Qiskit Aer noise not available, using mock noise models")
    
    class NoiseModel:
        """Mock NoiseModel."""
        pass
    
    class ReadoutError:
        """Mock ReadoutError."""
        def __init__(self, confusion_matrix):
            pass
    
    def pauli_error(pauli_list):
        """Mock pauli_error."""
        return None
    
    def depolarizing_error(prob, num_qubits):
        """Mock depolarizing_error."""
        return None


class NoiseModelFactory:
    """Factory for creating Qiskit noise models."""
    
    @staticmethod
    def create_bitflip_noise(error_prob: float) -> NoiseModel:
        """
        Create bit-flip noise model.
        
        Applies X (bit-flip) error with given probability to each gate.
        
        Args:
            error_prob: Error probability (0.0 to 1.0)
            
        Returns:
            NoiseModel with bit-flip errors
        """
        if not (0 <= error_prob <= 1):
            raise ValueError(f"Error probability must be [0,1], got {error_prob}")
        
        noise_model = NoiseModel()
        
        # Single-qubit bit-flip error
        single_error = pauli_error([('I', 1 - error_prob), ('X', error_prob)])
        
        # Two-qubit bit-flip error
        two_error = single_error.tensor(single_error)
        
        # Add to all single-qubit gates
        noise_model.add_all_qubit_quantum_error(single_error, ['u1', 'u2', 'u3', 'h', 'x'])
        
        # Add to all two-qubit gates
        noise_model.add_all_qubit_quantum_error(two_error, ['cx', 'cz', 'swap'])
        
        return noise_model
    
    @staticmethod
    def create_phaseflip_noise(error_prob: float) -> NoiseModel:
        """
        Create phase-flip noise model.
        
        Applies Z (phase-flip) error with given probability.
        
        Args:
            error_prob: Error probability (0.0 to 1.0)
            
        Returns:
            NoiseModel with phase-flip errors
        """
        if not (0 <= error_prob <= 1):
            raise ValueError(f"Error probability must be [0,1], got {error_prob}")
        
        noise_model = NoiseModel()
        
        # Single-qubit phase-flip error
        single_error = pauli_error([('I', 1 - error_prob), ('Z', error_prob)])
        
        # Two-qubit phase-flip error
        two_error = single_error.tensor(single_error)
        
        # Add to all gates
        noise_model.add_all_qubit_quantum_error(single_error, ['u1', 'u2', 'u3', 'h', 'x'])
        noise_model.add_all_qubit_quantum_error(two_error, ['cx', 'cz', 'swap'])
        
        return noise_model
    
    @staticmethod
    def create_depolarizing_noise(error_prob: float) -> NoiseModel:
        """
        Create depolarizing noise model.
        
        Most general single-qubit noise: maps to |0⟩, |1⟩, or leaves unchanged.
        
        Args:
            error_prob: Error probability (0.0 to 1.0)
            
        Returns:
            NoiseModel with depolarizing errors
        """
        if not (0 <= error_prob <= 1):
            raise ValueError(f"Error probability must be [0,1], got {error_prob}")
        
        noise_model = NoiseModel()
        
        # Single-qubit depolarizing
        single_error = depolarizing_error(error_prob, 1)
        
        # Two-qubit depolarizing
        two_error = depolarizing_error(error_prob, 2)
        
        # Add to all gates
        noise_model.add_all_qubit_quantum_error(single_error, ['u1', 'u2', 'u3', 'h', 'x', 'rx', 'ry', 'rz'])
        noise_model.add_all_qubit_quantum_error(two_error, ['cx', 'cz', 'swap'])
        
        return noise_model
    
    @staticmethod
    def create_readout_noise(error_prob: float) -> NoiseModel:
        """
        Create measurement/readout noise model.
        
        Measurement outcomes are flipped with given probability.
        
        Args:
            error_prob: Error probability (0.0 to 1.0)
            
        Returns:
            NoiseModel with readout errors
        """
        if not (0 <= error_prob <= 1):
            raise ValueError(f"Error probability must be [0,1], got {error_prob}")
        
        noise_model = NoiseModel()
        
        # Create readout error
        # Confusion matrix: [[1-p, p], [p, 1-p]]
        error = ReadoutError([[1 - error_prob, error_prob], [error_prob, 1 - error_prob]])
        
        # Add to all measurements
        noise_model.add_all_qubit_readout_error(error)
        
        return noise_model
    
    @staticmethod
    def create_combined_noise(bitflip_prob: float = 0.0, 
                            phaseflip_prob: float = 0.0,
                            depolarizing_prob: float = 0.0,
                            readout_prob: float = 0.0) -> NoiseModel:
        """
        Create combined noise model with multiple error types.
        
        Args:
            bitflip_prob: Bit-flip error probability
            phaseflip_prob: Phase-flip error probability
            depolarizing_prob: Depolarizing error probability
            readout_prob: Readout error probability
            
        Returns:
            Combined NoiseModel
        """
        noise_model = NoiseModel()
        
        # Bitflip
        if bitflip_prob > 0:
            single_bitflip = pauli_error([('I', 1 - bitflip_prob), ('X', bitflip_prob)])
            noise_model.add_all_qubit_quantum_error(single_bitflip, ['u1', 'u2', 'u3', 'h', 'x'])
        
        # Phaseflip
        if phaseflip_prob > 0:
            single_phaseflip = pauli_error([('I', 1 - phaseflip_prob), ('Z', phaseflip_prob)])
            noise_model.add_all_qubit_quantum_error(single_phaseflip, ['u1', 'u2', 'u3', 'h', 'x'])
        
        # Depolarizing
        if depolarizing_prob > 0:
            single_depol = depolarizing_error(depolarizing_prob, 1)
            noise_model.add_all_qubit_quantum_error(single_depol, ['u1', 'u2', 'u3', 'h', 'x', 'rx', 'ry', 'rz'])
        
        # Readout
        if readout_prob > 0:
            readout_error = ReadoutError([[1 - readout_prob, readout_prob], [readout_prob, 1 - readout_prob]])
            noise_model.add_all_qubit_readout_error(readout_error)
        
        return noise_model


class NoiseConfig:
    """Configuration for noise parameters."""
    
    def __init__(self, noise_type: str = "none", noise_prob: float = 0.0):
        """
        Initialize noise configuration.
        
        Args:
            noise_type: Type of noise ("none", "bitflip", "phaseflip", "depolarizing", "readout")
            noise_prob: Noise probability (0.0 to 1.0)
        """
        self.noise_type = noise_type
        self.noise_prob = max(0.0, min(1.0, noise_prob))
    
    def get_noise_model(self) -> Optional[NoiseModel]:
        """
        Get the corresponding noise model.
        
        Returns:
            NoiseModel or None if no noise
        """
        if self.noise_type == "none":
            return None
        elif self.noise_type == "bitflip":
            return NoiseModelFactory.create_bitflip_noise(self.noise_prob)
        elif self.noise_type == "phaseflip":
            return NoiseModelFactory.create_phaseflip_noise(self.noise_prob)
        elif self.noise_type == "depolarizing":
            return NoiseModelFactory.create_depolarizing_noise(self.noise_prob)
        elif self.noise_type == "readout":
            return NoiseModelFactory.create_readout_noise(self.noise_prob)
        else:
            raise ValueError(f"Unknown noise type: {self.noise_type}")
    
    def is_noisy(self) -> bool:
        """Check if this configuration includes noise."""
        return self.noise_type != "none" and self.noise_prob > 0


if __name__ == "__main__":
    print("Noise Models Available:")
    print("  - bitflip: X error with probability")
    print("  - phaseflip: Z error with probability")
    print("  - depolarizing: General depolarizing channel")
    print("  - readout: Measurement outcome flips")
    print("  - none: No noise (ideal simulator)")
    
    # Test each noise model
    for noise_type in ["bitflip", "phaseflip", "depolarizing", "readout"]:
        config = NoiseConfig(noise_type, 0.05)
        model = config.get_noise_model()
        print(f"\n✓ {noise_type} noise (5%): {type(model).__name__}")
