"""
Visualization and plot generation for experiment results.
Creates graphs, comparisons, and analysis visualizations.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Optional


class PlotGenerator:
    """Generates plots from experiment results."""
    
    def __init__(self, output_dir: str = "plots"):
        """
        Initialize plot generator.
        
        Args:
            output_dir: Directory for saving plots
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Set style
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (12, 6)
        plt.rcParams['font.size'] = 10
    
    def plot_resolution_scaling(self, df: pd.DataFrame) -> None:
        """Plot 1: Resolution vs execution time."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # Extract data
        resolutions = df['image_size'].values
        times = df['quantum_total_time'].values * 1000
        qubits = df['num_qubits'].values
        
        # Plot 1a: Time vs resolution
        ax1.plot(resolutions, times, 'o-', linewidth=2, markersize=8, label='Quantum')
        ax1.set_xlabel('Image Resolution (pixels per side)', fontsize=11)
        ax1.set_ylabel('Execution Time (ms)', fontsize=11)
        ax1.set_title('Execution Time vs Image Resolution', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.set_yscale('log')
        
        # Plot 1b: Qubits vs resolution
        ax2.plot(resolutions, qubits, 's-', linewidth=2, markersize=8, color='green', label='Qubits')
        ax2.set_xlabel('Image Resolution (pixels per side)', fontsize=11)
        ax2.set_ylabel('Number of Qubits', fontsize=11)
        ax2.set_title('Quantum Resources vs Image Resolution', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / "01_resolution_vs_time.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_shots_impact(self, df: pd.DataFrame) -> None:
        """Plot 2-3: Shot count impact on quality and time."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        shots = df['shots'].values
        psnr = df['psnr'].values
        times = df['quantum_total_time'].values * 1000
        
        # Plot 2: PSNR vs shots
        ax1.plot(shots, psnr, 'o-', linewidth=2, markersize=8, color='purple')
        ax1.set_xlabel('Number of Shots', fontsize=11)
        ax1.set_ylabel('PSNR (dB)', fontsize=11)
        ax1.set_title('Reconstruction Quality vs Shot Count', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.set_xscale('log')
        
        # Plot 3: Time vs shots
        ax2.plot(shots, times, 's-', linewidth=2, markersize=8, color='orange')
        ax2.set_xlabel('Number of Shots', fontsize=11)
        ax2.set_ylabel('Execution Time (ms)', fontsize=11)
        ax2.set_title('Execution Time vs Shot Count', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.set_xscale('log')
        ax2.set_yscale('log')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / "02_shots_impact.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_noise_sensitivity(self, df: pd.DataFrame) -> None:
        """Plot 4: Noise sensitivity analysis."""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        noise_types = df['noise_model'].unique()
        
        metrics = ['mse', 'psnr', 'ssim', 'correlation']
        colors = ['red', 'blue', 'green', 'purple', 'orange']
        
        for idx, metric in enumerate(metrics):
            ax = axes[idx // 2, idx % 2]
            
            for i, noise_type in enumerate(noise_types):
                mask = df['noise_model'] == noise_type
                subset = df[mask].sort_values('noise_probability')
                
                noise_probs = subset['noise_probability'].values * 100
                values = subset[metric].values
                
                ax.plot(noise_probs, values, 'o-', linewidth=2, markersize=6, 
                       label=noise_type, color=colors[i % len(colors)])
            
            ax.set_xlabel('Noise Probability (%)', fontsize=11)
            ax.set_ylabel(metric.upper(), fontsize=11)
            ax.set_title(f'{metric.upper()} vs Noise', fontsize=12, fontweight='bold')
            ax.legend()
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / "03_noise_sensitivity.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_circuit_complexity(self, df: pd.DataFrame) -> None:
        """Plot 5: Circuit complexity effects."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        circuit_types = df['circuit_type'].unique()
        
        # Map to numeric for plotting
        circuit_map = {'basic': 0, 'medium': 1, 'deep': 2}
        circuit_x = [circuit_map[c] for c in circuit_types]
        
        depths = [df[df['circuit_type'] == c]['circuit_depth'].iloc[0] for c in circuit_types]
        psnrs = [df[df['circuit_type'] == c]['psnr'].mean() for c in circuit_types]
        times = [df[df['circuit_type'] == c]['quantum_total_time'].mean() * 1000 for c in circuit_types]
        
        # Plot 1: PSNR vs circuit type
        ax1.bar(circuit_x, psnrs, color=['green', 'blue', 'red'], alpha=0.7)
        ax1.set_ylabel('PSNR (dB)', fontsize=11)
        ax1.set_title('Image Quality vs Circuit Complexity', fontsize=12, fontweight='bold')
        ax1.set_xticks(circuit_x)
        ax1.set_xticklabels(circuit_types)
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Plot 2: Time vs circuit type
        ax2_twin = ax2.twinx()
        bars = ax2.bar(circuit_x, times, color=['green', 'blue', 'red'], alpha=0.7, label='Execution time')
        line = ax2_twin.plot(circuit_x, depths, 'ko-', linewidth=2, markersize=8, label='Circuit depth')
        
        ax2.set_ylabel('Execution Time (ms)', fontsize=11)
        ax2_twin.set_ylabel('Circuit Depth', fontsize=11)
        ax2.set_title('Performance vs Circuit Complexity', fontsize=12, fontweight='bold')
        ax2.set_xticks(circuit_x)
        ax2.set_xticklabels(circuit_types)
        ax2.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / "04_circuit_complexity.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_quantum_vs_classical(self, df: pd.DataFrame) -> None:
        """Plot 6: Quantum vs Classical comparison."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        quantum_times = df['quantum_total_time'].values * 1000
        classical_times = df['classical_time'].values * 1000
        quantum_quality = df['psnr'].values
        classical_quality = df['classical_psnr'].values
        
        x = np.arange(len(df))
        width = 0.35
        
        # Plot 1: Execution time comparison
        ax1.bar(x - width/2, quantum_times, width, label='Quantum', alpha=0.8)
        ax1.bar(x + width/2, classical_times, width, label='Classical', alpha=0.8)
        ax1.set_ylabel('Execution Time (ms)', fontsize=11)
        ax1.set_title('Execution Time: Quantum vs Classical', fontsize=12, fontweight='bold')
        ax1.set_yscale('log')
        ax1.legend()
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Plot 2: Quality comparison
        ax2.bar(x - width/2, quantum_quality, width, label='Quantum', alpha=0.8)
        ax2.bar(x + width/2, classical_quality, width, label='Classical', alpha=0.8)
        ax2.set_ylabel('PSNR (dB)', fontsize=11)
        ax2.set_title('Image Quality: Quantum vs Classical', fontsize=12, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / "05_quantum_vs_classical.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_correlation_matrix(self, df: pd.DataFrame) -> None:
        """Plot 7: Correlation matrix of metrics."""
        numeric_cols = ['image_size', 'num_qubits', 'shots', 'circuit_depth', 
                       'mse', 'psnr', 'ssim', 'quantum_total_time', 'classical_time']
        
        # Select only available columns
        available_cols = [col for col in numeric_cols if col in df.columns]
        corr_matrix = df[available_cols].corr()
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', 
                   center=0, square=True, linewidths=1)
        plt.title('Correlation Matrix of Experiment Metrics', fontsize=12, fontweight='bold')
        plt.tight_layout()
        plt.savefig(self.output_dir / "06_correlation_matrix.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_all_plots(self, results_file: str = "results/experiments.csv") -> None:
        """Generate all plots from CSV results."""
        # Load results
        df = pd.read_csv(results_file)
        
        print("\nGenerating plots...")
        
        # Plot 1: Resolution
        resolution_df = df[df['experiment_type'] == 'resolution'].sort_values('image_size')
        if not resolution_df.empty:
            self.plot_resolution_scaling(resolution_df)
            print("✓ Plot 1: Resolution scaling")
        
        # Plot 2-3: Shots
        shots_df = df[df['experiment_type'] == 'shots'].sort_values('shots')
        if not shots_df.empty:
            self.plot_shots_impact(shots_df)
            print("✓ Plot 2-3: Shots impact")
        
        # Plot 4: Noise
        noise_df = df[df['experiment_type'] == 'noise']
        if not noise_df.empty:
            self.plot_noise_sensitivity(noise_df)
            print("✓ Plot 4: Noise sensitivity")
        
        # Plot 5: Circuit
        circuit_df = df[df['experiment_type'] == 'circuit']
        if not circuit_df.empty:
            self.plot_circuit_complexity(circuit_df)
            print("✓ Plot 5: Circuit complexity")
        
        # Plot 6: Quantum vs Classical
        baseline_df = df[df['experiment_type'] == 'baseline']
        if not baseline_df.empty:
            self.plot_quantum_vs_classical(baseline_df)
            print("✓ Plot 6: Quantum vs Classical")
        
        # Plot 7: Correlation
        self.plot_correlation_matrix(df)
        print("✓ Plot 7: Correlation matrix")
        
        print(f"\n✓ All plots saved to: {self.output_dir}")


if __name__ == "__main__":
    generator = PlotGenerator()
    generator.generate_all_plots()
