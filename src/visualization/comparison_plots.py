"""
Image comparison visualization.
Creates side-by-side comparisons of original, reconstructed, and difference images.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Tuple
from src.preprocessing.dataset import Dataset
from src.quantum.encoding import AmplitudeEncoder
from src.reconstruction.measurement_processor import CountsSimulator
from src.reconstruction.image_reconstructor import ImageReconstructor


class ImageComparisonPlotter:
    """Creates visual comparisons of quantum image processing results."""
    
    def __init__(self, output_dir: str = "plots/comparisons"):
        """
        Initialize comparison plotter.
        
        Args:
            output_dir: Directory for saving comparisons
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.dataset = Dataset()
    
    def plot_single_experiment_comparison(self, image_size: int, 
                                         image_type: str = "checkerboard",
                                         shots: int = 1000) -> None:
        """
        Create comparison plot for single experiment.
        
        Shows: Original | Encoded | Reconstructed | Difference
        """
        # Generate image
        if image_type == "checkerboard":
            original = self.dataset.generate_checkerboard(image_size, save=False)
        elif image_type == "circle":
            original = self.dataset.generate_circle(image_size, save=False)
        else:
            original = self.dataset.generate_square(image_size, save=False)
        
        # Encode
        encoder = AmplitudeEncoder(original)
        probs = encoder.get_measurement_probabilities()
        
        # Simulate measurement
        counts = CountsSimulator.simulate_counts(probs, shots=shots, seed=42)
        
        # Reconstruct
        reconstructor = ImageReconstructor((image_size, image_size))
        reconstructed = reconstructor.reconstruct_complete(counts)
        
        # Calculate difference
        difference = np.abs(original - reconstructed)
        
        # Create visualization
        fig, axes = plt.subplots(1, 4, figsize=(16, 4))
        
        # Original
        im0 = axes[0].imshow(original, cmap='gray', vmin=0, vmax=1)
        axes[0].set_title(f'Original ({image_size}×{image_size})', fontsize=11, fontweight='bold')
        axes[0].axis('off')
        plt.colorbar(im0, ax=axes[0], fraction=0.046, pad=0.04)
        
        # Measurement probabilities
        prob_image = probs[:image_size*image_size].reshape((image_size, image_size))
        im1 = axes[1].imshow(prob_image, cmap='gray', vmin=0, vmax=prob_image.max())
        axes[1].set_title('Measurement Probs', fontsize=11, fontweight='bold')
        axes[1].axis('off')
        plt.colorbar(im1, ax=axes[1], fraction=0.046, pad=0.04)
        
        # Reconstructed
        im2 = axes[2].imshow(reconstructed, cmap='gray', vmin=0, vmax=1)
        axes[2].set_title(f'Reconstructed ({shots} shots)', fontsize=11, fontweight='bold')
        axes[2].axis('off')
        plt.colorbar(im2, ax=axes[2], fraction=0.046, pad=0.04)
        
        # Difference
        im3 = axes[3].imshow(difference, cmap='hot')
        axes[3].set_title('Absolute Error', fontsize=11, fontweight='bold')
        axes[3].axis('off')
        plt.colorbar(im3, ax=axes[3], fraction=0.046, pad=0.04)
        
        plt.suptitle(f'{image_type.capitalize()} Image: Quantum Processing Pipeline', 
                    fontsize=13, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        filename = f"{image_type}_{image_size}x{image_size}_{shots}shots.png"
        plt.savefig(self.output_dir / filename, dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_resolution_comparison(self) -> None:
        """Create comparisons for different resolutions."""
        sizes = [2, 4, 8, 16]
        
        for size in sizes:
            try:
                self.plot_single_experiment_comparison(
                    image_size=size,
                    image_type="checkerboard",
                    shots=1000
                )
            except Exception as e:
                print(f"  Note: Could not create {size}×{size} comparison: {e}")
    
    def plot_noise_comparison(self) -> None:
        """Create comparisons with different noise levels."""
        from src.quantum.noise_models import NoiseConfig
        
        noise_configs = [
            ("none", 0.0),
            ("bitflip", 0.05),
            ("depolarizing", 0.05),
        ]
        
        # TODO: Requires full execution pipeline with noise
        pass
    
    def generate_all_comparisons(self) -> None:
        """Generate all comparison plots."""
        print("\nGenerating image comparisons...")
        self.plot_resolution_comparison()
        print(f"✓ Image comparisons saved to: {self.output_dir}")


if __name__ == "__main__":
    plotter = ImageComparisonPlotter()
    plotter.generate_all_comparisons()
