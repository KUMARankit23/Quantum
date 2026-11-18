"""
Single experiment runner.
Executes one experiment from configuration to results.
"""

import time
import numpy as np
from typing import Dict, Optional
from src.experiments.experiment_config import ExperimentConfig
from src.preprocessing.dataset import Dataset
from src.preprocessing.normalization import resize_image
from src.quantum.encoding import AmplitudeEncoder
from src.quantum.circuit_builder import CircuitBuilder
from src.quantum.executor import QuantumExecutor
from src.quantum.noise_models import NoiseConfig
from src.reconstruction.image_reconstructor import ImageReconstructor
from src.classical.baseline import ClassicalBaseline
from src.evaluation.metrics import calculate_all_metrics
from src.evaluation.quantum_metrics import analyze_circuit


class ExperimentRunner:
    """Runs a single experiment."""
    
    def __init__(self, config: ExperimentConfig, verbose: bool = True):
        """
        Initialize experiment runner.
        
        Args:
            config: ExperimentConfig with all parameters
            verbose: Whether to print progress
        """
        self.config = config
        self.verbose = verbose
        
        # Set random seed
        np.random.seed(config.seed)
    
    def load_image(self) -> np.ndarray:
        """Load or generate test image."""
        dataset = Dataset()
        
        if self.config.image_type == "checkerboard":
            image = dataset.generate_checkerboard(self.config.image_size, save=False)
        elif "gradient" in self.config.image_type:
            direction = self.config.image_type.replace("gradient_", "")
            image = dataset.generate_gradient(self.config.image_size, direction, save=False)
        elif self.config.image_type == "circle":
            image = dataset.generate_circle(self.config.image_size, save=False)
        elif self.config.image_type == "square":
            image = dataset.generate_square(self.config.image_size, save=False)
        elif self.config.image_type == "random_binary":
            image = dataset.generate_random_binary(self.config.image_size, self.config.seed, save=False)
        elif self.config.image_type == "random_grayscale":
            image = dataset.generate_random_grayscale(self.config.image_size, self.config.seed, save=False)
        else:
            raise ValueError(f"Unknown image type: {self.config.image_type}")
        
        return image
    
    def run(self) -> Dict:
        """
        Run the complete experiment.
        
        Returns:
            Dictionary with all experiment results
        """
        if self.verbose:
            print(f"\n{'='*70}")
            print(f"Running Experiment: {self.config.experiment_id}")
            print(f"{'='*70}")
        
        # Load image
        if self.verbose:
            print(f"[1/6] Loading image ({self.config.image_size}×{self.config.image_size})...")
        image = self.load_image()
        
        # Preprocessing
        if self.verbose:
            print(f"[2/6] Preprocessing...")
        preprocessing_start = time.time()
        preprocessing_time = time.time() - preprocessing_start
        
        # Quantum encoding
        if self.verbose:
            print(f"[3/6] Quantum encoding...")
        encoding_start = time.time()
        encoder = AmplitudeEncoder(image)
        encoding_time = time.time() - encoding_start
        
        # Build circuit
        if self.verbose:
            print(f"[4/6] Building circuit ({self.config.circuit_type})...")
        builder = CircuitBuilder()
        circuit = builder.build_complete_circuit(image, self.config.circuit_type)
        circuit_info = analyze_circuit(circuit)
        
        # Execute
        if self.verbose:
            print(f"[5/6] Executing ({self.config.shots} shots)...")
        noise_config = NoiseConfig(self.config.noise_model, self.config.noise_probability)
        executor = QuantumExecutor(use_noise=True, noise_config=noise_config)
        execution_result = executor.execute(circuit, self.config.shots, self.config.seed)
        
        # Reconstruct
        if self.verbose:
            print(f"[6/6] Reconstructing image...")
        reconstruction_start = time.time()
        reconstructor = ImageReconstructor((self.config.image_size, self.config.image_size))
        reconstructed = reconstructor.reconstruct_complete(execution_result["counts"])
        reconstruction_time = time.time() - reconstruction_start
        
        # Evaluate
        if self.verbose:
            print(f"Evaluating metrics...")
        metrics = calculate_all_metrics(image, reconstructed)
        
        # Classical baseline
        if self.verbose:
            print(f"Running classical baseline...")
        baseline = ClassicalBaseline()
        classical_result, classical_time = baseline.process(image, method="gaussian")
        classical_metrics = calculate_all_metrics(image, classical_result)
        
        # Compile results
        results = {
            "experiment_id": self.config.experiment_id,
            "image_name": self.config.image_type,
            "image_size": self.config.image_size,
            "intensity_levels": 256,  # 8-bit
            "encoding_method": self.config.encoding_method,
            "num_qubits": encoder.num_qubits,
            "gate_count": circuit_info["total_gates"],
            "two_qubit_gates": circuit_info["two_qubit_gates"],
            "circuit_depth": circuit_info["circuit_depth"],
            "shots": self.config.shots,
            "noise_model": self.config.noise_model,
            "noise_probability": self.config.noise_probability,
            
            # Quantum timing
            "preprocessing_time": preprocessing_time,
            "encoding_time": encoding_time,
            "circuit_execution_time": execution_result["execution_time"],
            "reconstruction_time": reconstruction_time,
            "quantum_total_time": preprocessing_time + encoding_time + execution_result["execution_time"] + reconstruction_time,
            
            # Quantum metrics
            "mse": metrics["mse"],
            "psnr": metrics["psnr"],
            "ssim": metrics["ssim"],
            "mae": metrics["mae"],
            "correlation": metrics["correlation"],
            
            # Classical comparison
            "classical_time": classical_time,
            "classical_mse": classical_metrics["mse"],
            "classical_psnr": classical_metrics["psnr"],
            "classical_ssim": classical_metrics["ssim"],
            "time_ratio": execution_result["execution_time"] / classical_time if classical_time > 0 else float('inf'),
            
            # Success indicators
            "success": True,
        }
        
        if self.verbose:
            print(f"\n{'─'*70}")
            print(f"Results:")
            print(f"  Quantum MSE: {results['mse']:.6f}")
            print(f"  Quantum PSNR: {results['psnr']:.2f} dB")
            print(f"  Classical MSE: {results['classical_mse']:.6f}")
            print(f"  Quantum time: {results['quantum_total_time']*1000:.2f} ms")
            print(f"  Classical time: {results['classical_time']*1000:.2f} ms")
            print(f"  Time ratio: {results['time_ratio']:.1f}×")
            print(f"{'='*70}\n")
        
        return results


class BatchExperimentRunner:
    """Runs multiple experiments."""
    
    def __init__(self, configs: list, verbose: bool = True):
        """
        Initialize batch runner.
        
        Args:
            configs: List of ExperimentConfig objects
            verbose: Whether to print progress
        """
        self.configs = configs
        self.verbose = verbose
    
    def run_all(self) -> list:
        """
        Run all experiments.
        
        Returns:
            List of results dictionaries
        """
        results = []
        total = len(self.configs)
        
        for i, config in enumerate(self.configs):
            if self.verbose:
                print(f"\n[{i+1}/{total}] ", end="")
            
            runner = ExperimentRunner(config, verbose=self.verbose)
            result = runner.run()
            results.append(result)
        
        return results


if __name__ == "__main__":
    # Quick test
    from src.experiments.experiment_config import get_default_config
    
    config = get_default_config()
    runner = ExperimentRunner(config, verbose=True)
    result = runner.run()
    
    print("\nExperiment completed!")
    print(f"Keys in result: {list(result.keys())}")
