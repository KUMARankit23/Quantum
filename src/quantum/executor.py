"""
Quantum circuit execution on simulators.
Handles execution with Qiskit Aer (with fallback for testing).
"""

import time
import numpy as np
from typing import Dict, Optional
from qiskit import QuantumCircuit
from src.quantum.noise_models import NoiseConfig

# Try importing AerSimulator, fallback to mock for testing
try:
    from qiskit_aer import AerSimulator
    SIMULATOR_AVAILABLE = True
except ImportError:
    SIMULATOR_AVAILABLE = False
    print("[INFO] Qiskit Aer not available, using mock simulator for testing")
    
    class AerSimulator:
        """Mock simulator for testing when Qiskit Aer unavailable."""
        def __init__(self, noise_model=None):
            self.noise_model = noise_model
        
        def run(self, circuit, shots=1000, seed_simulator=42):
            """Mock run returns simulated results."""
            return MockJob()


class MockJob:
    """Mock job for testing."""
    def result(self):
        return MockResult()


class MockResult:
    """Mock result for testing."""
    def get_counts(self, circuit):
        """Return mock measurement counts."""
        num_qubits = circuit.num_qubits
        num_states = 2 ** num_qubits
        
        # Return uniform distribution
        counts_per_state = 1000 // num_states
        counts = {}
        for i in range(num_states):
            bitstring = format(i, f'0{num_qubits}b')
            counts[bitstring] = counts_per_state
        
        return counts


class QuantumExecutor:
    """Executes quantum circuits on simulators."""
    
    def __init__(self, use_noise: bool = False, noise_config: Optional[NoiseConfig] = None):
        """
        Initialize quantum executor.
        
        Args:
            use_noise: Whether to use noise simulation
            noise_config: NoiseConfig object (if use_noise=True)
        """
        self.use_noise = use_noise
        self.noise_config = noise_config or NoiseConfig("none", 0.0)
        
        # Create simulator
        if use_noise and self.noise_config.is_noisy():
            self.simulator = AerSimulator(noise_model=self.noise_config.get_noise_model())
        else:
            self.simulator = AerSimulator()
    
    def execute(self, circuit: QuantumCircuit, shots: int = 1000, 
               seed: int = 42) -> Dict:
        """
        Execute quantum circuit.
        
        Args:
            circuit: Qiskit QuantumCircuit to execute
            shots: Number of measurement shots
            seed: Random seed for reproducibility
            
        Returns:
            Dictionary with execution results
        """
        start_time = time.time()
        
        # Execute circuit
        job = self.simulator.run(circuit, shots=shots, seed_simulator=seed)
        result = job.result()
        
        execution_time = time.time() - start_time
        
        # Extract counts
        counts = result.get_counts(circuit)
        
        return {
            "counts": counts,
            "shots": shots,
            "execution_time": execution_time,
            "noise_model": self.noise_config.noise_type,
            "noise_probability": self.noise_config.noise_prob,
        }
    
    def execute_with_timing(self, circuit: QuantumCircuit, shots: int = 1000,
                           seed: int = 42) -> Dict:
        """
        Execute circuit with detailed timing information.
        
        Args:
            circuit: Quantum circuit
            shots: Number of shots
            seed: Random seed
            
        Returns:
            Results with timing breakdown
        """
        # Measure different timing components
        timing = {}
        
        # Preprocessing
        preprocess_start = time.time()
        # (Already done during circuit building)
        timing["preprocessing"] = time.time() - preprocess_start
        
        # Execution
        exec_start = time.time()
        result = self.execute(circuit, shots, seed)
        timing["execution"] = result["execution_time"]
        
        # Measurement (included in execution)
        timing["measurement"] = timing["execution"] * 0.1  # Estimate
        
        timing["total"] = timing["preprocessing"] + timing["execution"]
        
        result["timing"] = timing
        return result
    
    def batch_execute(self, circuits: list, shots: int = 1000, 
                     seed: int = 42) -> list:
        """
        Execute multiple circuits.
        
        Args:
            circuits: List of QuantumCircuits
            shots: Shots per circuit
            seed: Random seed
            
        Returns:
            List of results
        """
        results = []
        for i, circuit in enumerate(circuits):
            result = self.execute(circuit, shots, seed=seed + i)
            result["circuit_index"] = i
            results.append(result)
        
        return results
    
    def get_simulator_info(self) -> dict:
        """
        Get information about the simulator.
        
        Returns:
            Simulator information dictionary
        """
        return {
            "simulator_type": str(type(self.simulator).__name__),
            "noise_enabled": self.use_noise and self.noise_config.is_noisy(),
            "noise_type": self.noise_config.noise_type,
            "noise_probability": self.noise_config.noise_prob,
        }


class CircuitExecutionPipeline:
    """Full pipeline from image to measurement counts."""
    
    def __init__(self, use_noise: bool = False, 
                noise_config: Optional[NoiseConfig] = None):
        """Initialize execution pipeline."""
        self.executor = QuantumExecutor(use_noise, noise_config)
    
    def run(self, circuit: QuantumCircuit, shots: int = 1000, 
           seed: int = 42) -> dict:
        """
        Run full execution pipeline.
        
        Args:
            circuit: Quantum circuit to execute
            shots: Number of measurement shots
            seed: Random seed
            
        Returns:
            Execution results
        """
        result = self.executor.execute_with_timing(circuit, shots, seed)
        return result


if __name__ == "__main__":
    # Quick test
    from src.quantum.circuit_builder import CircuitBuilder
    from src.preprocessing.dataset import Dataset
    
    dataset = Dataset()
    image = dataset.generate_checkerboard(4, save=False)
    
    # Build circuit
    builder = CircuitBuilder()
    circuit = builder.build_complete_circuit(image)
    
    # Execute (ideal)
    executor = QuantumExecutor(use_noise=False)
    result = executor.execute(circuit, shots=100, seed=42)
    
    print(f"Ideal execution (100 shots):")
    print(f"  Execution time: {result['execution_time']*1000:.2f} ms")
    print(f"  Counts: {result['counts']}")
    
    # Execute with noise
    from src.quantum.noise_models import NoiseConfig
    noise_config = NoiseConfig("depolarizing", 0.05)
    executor_noisy = QuantumExecutor(use_noise=True, noise_config=noise_config)
    result_noisy = executor_noisy.execute(circuit, shots=100, seed=42)
    
    print(f"\nNoisy execution (5% depolarizing, 100 shots):")
    print(f"  Execution time: {result_noisy['execution_time']*1000:.2f} ms")
    print(f"  Counts: {result_noisy['counts']}")
