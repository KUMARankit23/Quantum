"""
Batch experiment runner for executing multiple experiments.
Orchestrates all 6 controlled experiments.
"""

import os
import json
import pandas as pd
import time
from typing import List, Dict, Optional
from pathlib import Path
from src.experiments.experiment_runner import ExperimentRunner
from src.experiments.experiment_config import ExperimentConfig, ConfigurationManager


class BatchExperimentRunner:
    """Manages and executes batches of experiments."""
    
    def __init__(self, results_dir: str = "results", verbose: bool = True):
        """
        Initialize batch runner.
        
        Args:
            results_dir: Directory for saving results
            verbose: Print progress
        """
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
        self.verbose = verbose
        self.results = []
    
    def run_experiment(self, config: ExperimentConfig) -> Dict:
        """Run single experiment."""
        runner = ExperimentRunner(config, verbose=self.verbose)
        return runner.run()
    
    def run_resolution_experiments(self) -> List[Dict]:
        """Experiment A: Resolution scaling (2×2 → 4×4 → 8×8 → 16×16)."""
        if self.verbose:
            print("\n" + "="*70)
            print("EXPERIMENT A: RESOLUTION SCALING")
            print("="*70)
        
        configs = [
            ExperimentConfig(
                experiment_id="resolution_2x2",
                image_type="checkerboard",
                image_size=2,
                shots=1000,
                description="2×2 resolution"
            ),
            ExperimentConfig(
                experiment_id="resolution_4x4",
                image_type="checkerboard",
                image_size=4,
                shots=1000,
                description="4×4 resolution"
            ),
            ExperimentConfig(
                experiment_id="resolution_8x8",
                image_type="checkerboard",
                image_size=8,
                shots=1000,
                description="8×8 resolution"
            ),
            ExperimentConfig(
                experiment_id="resolution_16x16",
                image_type="checkerboard",
                image_size=16,
                shots=1000,
                description="16×16 resolution"
            ),
        ]
        
        results = []
        for config in configs:
            result = self.run_experiment(config)
            results.append(result)
        
        return results
    
    def run_shots_experiments(self) -> List[Dict]:
        """Experiment B: Shot count impact (100 → 500 → 1000 → 5000)."""
        if self.verbose:
            print("\n" + "="*70)
            print("EXPERIMENT B: SHOT COUNT IMPACT")
            print("="*70)
        
        configs = [
            ExperimentConfig(
                experiment_id="shots_100",
                image_type="checkerboard",
                image_size=4,
                shots=100,
                description="100 shots"
            ),
            ExperimentConfig(
                experiment_id="shots_500",
                image_type="checkerboard",
                image_size=4,
                shots=500,
                description="500 shots"
            ),
            ExperimentConfig(
                experiment_id="shots_1000",
                image_type="checkerboard",
                image_size=4,
                shots=1000,
                description="1000 shots"
            ),
            ExperimentConfig(
                experiment_id="shots_5000",
                image_type="checkerboard",
                image_size=4,
                shots=5000,
                description="5000 shots"
            ),
        ]
        
        results = []
        for config in configs:
            result = self.run_experiment(config)
            results.append(result)
        
        return results
    
    def run_noise_experiments(self) -> List[Dict]:
        """Experiment C: Noise sensitivity (5 types × 3 levels)."""
        if self.verbose:
            print("\n" + "="*70)
            print("EXPERIMENT C: NOISE SENSITIVITY")
            print("="*70)
        
        noise_types = ["none", "bitflip", "phaseflip", "depolarizing", "readout"]
        noise_levels = [0.0, 0.05, 0.10]
        
        configs = []
        for noise_type in noise_types:
            for noise_level in noise_levels:
                if noise_type == "none" and noise_level > 0:
                    continue  # Skip invalid combinations
                
                config = ExperimentConfig(
                    experiment_id=f"noise_{noise_type}_{int(noise_level*100)}pct",
                    image_type="checkerboard",
                    image_size=4,
                    shots=1000,
                    noise_model=noise_type,
                    noise_probability=noise_level,
                    description=f"{noise_type} noise ({int(noise_level*100)}%)"
                )
                configs.append(config)
        
        results = []
        for config in configs:
            result = self.run_experiment(config)
            results.append(result)
        
        return results
    
    def run_circuit_experiments(self) -> List[Dict]:
        """Experiment D: Circuit complexity (basic, medium, deep)."""
        if self.verbose:
            print("\n" + "="*70)
            print("EXPERIMENT D: CIRCUIT COMPLEXITY")
            print("="*70)
        
        configs = [
            ExperimentConfig(
                experiment_id="circuit_basic",
                image_type="checkerboard",
                image_size=4,
                circuit_type="basic",
                shots=1000,
                description="Basic circuit"
            ),
            ExperimentConfig(
                experiment_id="circuit_medium",
                image_type="checkerboard",
                image_size=4,
                circuit_type="medium",
                shots=1000,
                description="Medium circuit"
            ),
            ExperimentConfig(
                experiment_id="circuit_deep",
                image_type="checkerboard",
                image_size=4,
                circuit_type="deep",
                shots=1000,
                description="Deep circuit"
            ),
        ]
        
        results = []
        for config in configs:
            result = self.run_experiment(config)
            results.append(result)
        
        return results
    
    def run_representation_experiments(self) -> List[Dict]:
        """Experiment E: Intensity representation (binary, grayscale, normalized)."""
        if self.verbose:
            print("\n" + "="*70)
            print("EXPERIMENT E: INTENSITY REPRESENTATION")
            print("="*70)
        
        image_types = ["checkerboard", "circle", "square"]
        
        configs = []
        for image_type in image_types:
            config = ExperimentConfig(
                experiment_id=f"representation_{image_type}",
                image_type=image_type,
                image_size=4,
                shots=1000,
                description=f"{image_type} image"
            )
            configs.append(config)
        
        results = []
        for config in configs:
            result = self.run_experiment(config)
            results.append(result)
        
        return results
    
    def run_baseline_experiments(self) -> List[Dict]:
        """Experiment F: Quantum vs Classical baseline."""
        if self.verbose:
            print("\n" + "="*70)
            print("EXPERIMENT F: QUANTUM VS CLASSICAL BASELINE")
            print("="*70)
        
        # Run same images with quantum and classical
        configs = []
        for size in [2, 4, 8]:
            config = ExperimentConfig(
                experiment_id=f"baseline_{size}x{size}",
                image_type="checkerboard",
                image_size=size,
                shots=1000,
                description=f"Baseline comparison {size}×{size}"
            )
            configs.append(config)
        
        results = []
        for config in configs:
            result = self.run_experiment(config)
            results.append(result)
        
        return results
    
    def run_all_experiments(self) -> Dict:
        """Run all 6 experiments."""
        if self.verbose:
            print("\n" + "="*70)
            print("QUANTUM IMAGE PROCESSING - ALL CONTROLLED EXPERIMENTS")
            print("="*70)
        
        start_time = time.time()
        
        all_results = {
            "resolution": self.run_resolution_experiments(),
            "shots": self.run_shots_experiments(),
            "noise": self.run_noise_experiments(),
            "circuit": self.run_circuit_experiments(),
            "representation": self.run_representation_experiments(),
            "baseline": self.run_baseline_experiments(),
        }
        
        total_time = time.time() - start_time
        
        if self.verbose:
            print("\n" + "="*70)
            print("ALL EXPERIMENTS COMPLETE")
            print(f"Total time: {total_time:.1f} seconds ({total_time/60:.1f} minutes)")
            print("="*70)
        
        return all_results
    
    def save_results_to_csv(self, results: Dict) -> None:
        """Save all results to CSV files."""
        # Flatten results
        all_results = []
        for exp_type, exp_results in results.items():
            for result in exp_results:
                result["experiment_type"] = exp_type
                all_results.append(result)
        
        # Create main results DataFrame
        df_all = pd.DataFrame(all_results)
        
        # Save main file
        main_file = self.results_dir / "experiments.csv"
        df_all.to_csv(main_file, index=False)
        if self.verbose:
            print(f"✓ Saved main results: {main_file}")
        
        # Save by experiment type
        for exp_type, exp_results in results.items():
            df = pd.DataFrame(exp_results)
            file_path = self.results_dir / f"{exp_type}_results.csv"
            df.to_csv(file_path, index=False)
            if self.verbose:
                print(f"✓ Saved {exp_type} results: {file_path}")
    
    def generate_summary_statistics(self, results: Dict) -> Dict:
        """Generate summary statistics from all experiments."""
        summary = {}
        
        for exp_type, exp_results in results.items():
            df = pd.DataFrame(exp_results)
            
            # Calculate key statistics
            summary[exp_type] = {
                "num_experiments": len(exp_results),
                "avg_mse": df["mse"].mean(),
                "avg_psnr": df["psnr"].mean(),
                "avg_ssim": df["ssim"].mean(),
                "avg_quantum_time": df["quantum_total_time"].mean(),
                "avg_classical_time": df["classical_time"].mean(),
                "avg_time_ratio": df["time_ratio"].mean(),
                "min_psnr": df["psnr"].min(),
                "max_psnr": df["psnr"].max(),
            }
        
        return summary
    
    def print_summary(self, summary: Dict) -> None:
        """Print summary statistics."""
        print("\n" + "="*70)
        print("EXPERIMENT SUMMARY STATISTICS")
        print("="*70)
        
        for exp_type, stats in summary.items():
            print(f"\n{exp_type.upper()}:")
            print(f"  Experiments: {stats['num_experiments']}")
            print(f"  Avg MSE: {stats['avg_mse']:.6f}")
            print(f"  Avg PSNR: {stats['avg_psnr']:.2f} dB")
            print(f"  Avg SSIM: {stats['avg_ssim']:.4f}")
            print(f"  Avg quantum time: {stats['avg_quantum_time']*1000:.2f} ms")
            print(f"  Avg classical time: {stats['avg_classical_time']*1000:.2f} ms")
            print(f"  Time ratio (Q/C): {stats['avg_time_ratio']:.1f}×")
            print(f"  PSNR range: [{stats['min_psnr']:.2f}, {stats['max_psnr']:.2f}]")
        
        print("\n" + "="*70)


if __name__ == "__main__":
    # Run all experiments
    batch = BatchExperimentRunner(verbose=True)
    results = batch.run_all_experiments()
    
    # Save results
    batch.save_results_to_csv(results)
    
    # Print summary
    summary = batch.generate_summary_statistics(results)
    batch.print_summary(summary)
