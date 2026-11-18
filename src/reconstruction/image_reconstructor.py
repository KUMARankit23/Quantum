"""
Image reconstruction from quantum measurements.
Converts measurement results back to image format.
"""

import numpy as np
from typing import Dict, Tuple, Optional
from src.reconstruction.measurement_processor import MeasurementProcessor


class ImageReconstructor:
    """Reconstructs images from quantum measurement results."""
    
    def __init__(self, image_size: Tuple[int, int]):
        """
        Initialize image reconstructor.
        
        Args:
            image_size: Target image size (height, width)
        """
        self.image_height, self.image_width = image_size
        self.num_pixels = image_size[0] * image_size[1]
        self.num_qubits = int(np.ceil(np.log2(self.num_pixels)))
        self.processor = MeasurementProcessor(self.num_qubits, image_size)
    
    def reconstruct_from_counts(self, counts: Dict[str, int]) -> np.ndarray:
        """
        Reconstruct image from measurement counts.
        
        Args:
            counts: Measurement counts dictionary
            
        Returns:
            Reconstructed image (2D array, normalized [0,1])
        """
        # Convert counts to probabilities
        probabilities = self.processor.process_counts(counts)
        
        # Take only valid pixels
        pixel_probs = probabilities[:self.num_pixels]
        
        # Normalize to [0,1]
        if np.max(pixel_probs) > 0:
            pixel_probs = pixel_probs / np.max(pixel_probs)
        
        # Reshape to 2D image
        image = pixel_probs.reshape((self.image_height, self.image_width))
        
        return np.clip(image, 0, 1)
    
    def reconstruct_from_probabilities(self, probabilities: np.ndarray) -> np.ndarray:
        """
        Reconstruct image from probability distribution.
        
        Args:
            probabilities: Probability distribution (shape: 2^num_qubits)
            
        Returns:
            Reconstructed image
        """
        # Take only valid pixels
        pixel_probs = probabilities[:self.num_pixels]
        
        # Normalize
        if np.max(pixel_probs) > 0:
            pixel_probs = pixel_probs / np.max(pixel_probs)
        
        # Reshape to image
        image = pixel_probs.reshape((self.image_height, self.image_width))
        
        return np.clip(image, 0, 1)
    
    def handle_missing_outcomes(self, image: np.ndarray, 
                               fill_method: str = "interpolate") -> np.ndarray:
        """
        Handle pixels with zero/missing measurement outcomes.
        
        Args:
            image: Reconstructed image
            fill_method: How to handle missing pixels
                        ("interpolate", "zero", "mean")
            
        Returns:
            Processed image
        """
        image = image.copy()
        
        if fill_method == "zero":
            # Leave as zero (default)
            pass
        
        elif fill_method == "mean":
            # Replace zeros with mean of non-zero values
            nonzero_mean = np.mean(image[image > 0]) if np.any(image > 0) else 0
            zero_mask = image == 0
            image[zero_mask] = nonzero_mean
        
        elif fill_method == "interpolate":
            # Simple interpolation: average neighbors
            for i in range(self.image_height):
                for j in range(self.image_width):
                    if image[i, j] == 0:
                        neighbors = []
                        for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            ni, nj = i + di, j + dj
                            if 0 <= ni < self.image_height and 0 <= nj < self.image_width:
                                if image[ni, nj] > 0:
                                    neighbors.append(image[ni, nj])
                        
                        if neighbors:
                            image[i, j] = np.mean(neighbors)
        
        return np.clip(image, 0, 1)
    
    def normalize_reconstruction(self, image: np.ndarray, 
                                method: str = "minmax") -> np.ndarray:
        """
        Normalize reconstructed image to [0,1].
        
        Args:
            image: Reconstructed image
            method: Normalization method ("minmax", "maxonly", "none")
            
        Returns:
            Normalized image
        """
        image = image.copy()
        
        if method == "none":
            return np.clip(image, 0, 1)
        
        elif method == "maxonly":
            # Scale by maximum value only
            if np.max(image) > 0:
                image = image / np.max(image)
        
        elif method == "minmax":
            # Min-max normalization
            min_val = np.min(image)
            max_val = np.max(image)
            if max_val > min_val:
                image = (image - min_val) / (max_val - min_val)
            else:
                image = np.zeros_like(image)
        
        return np.clip(image, 0, 1)
    
    def reconstruct_complete(self, counts: Dict[str, int], 
                            fill_method: str = "interpolate",
                            normalize_method: str = "minmax") -> np.ndarray:
        """
        Complete reconstruction pipeline.
        
        Args:
            counts: Measurement counts
            fill_method: Missing pixel handling
            normalize_method: Normalization method
            
        Returns:
            Final reconstructed image
        """
        # Basic reconstruction
        image = self.reconstruct_from_counts(counts)
        
        # Handle missing outcomes
        image = self.handle_missing_outcomes(image, fill_method)
        
        # Normalize
        image = self.normalize_reconstruction(image, normalize_method)
        
        return image
    
    def get_reconstruction_quality(self, original: np.ndarray, 
                                  reconstructed: np.ndarray) -> dict:
        """
        Assess reconstruction quality.
        
        Args:
            original: Original image
            reconstructed: Reconstructed image
            
        Returns:
            Quality metrics dictionary
        """
        from src.evaluation.metrics import calculate_all_metrics
        
        # Ensure same shape
        if original.shape != reconstructed.shape:
            raise ValueError(f"Shape mismatch: {original.shape} vs {reconstructed.shape}")
        
        metrics = calculate_all_metrics(original, reconstructed)
        
        return metrics


class ReconstructionPipeline:
    """Full pipeline from quantum circuit to reconstructed image."""
    
    def __init__(self, image_size: Tuple[int, int]):
        """Initialize reconstruction pipeline."""
        self.image_size = image_size
        self.reconstructor = ImageReconstructor(image_size)
    
    def run(self, counts: Dict[str, int], 
           original_image: Optional[np.ndarray] = None) -> dict:
        """
        Run full reconstruction pipeline.
        
        Args:
            counts: Measurement counts from quantum circuit
            original_image: Optional original image for comparison
            
        Returns:
            Dictionary with results
        """
        # Reconstruct image
        reconstructed = self.reconstructor.reconstruct_complete(counts)
        
        result = {
            "reconstructed_image": reconstructed,
            "counts": counts,
            "num_shots": sum(counts.values()),
        }
        
        # Compare with original if provided
        if original_image is not None:
            metrics = self.reconstructor.get_reconstruction_quality(
                original_image, reconstructed
            )
            result["quality_metrics"] = metrics
            result["original_image"] = original_image
        
        return result


if __name__ == "__main__":
    # Quick test
    from src.reconstruction.measurement_processor import CountsSimulator
    from src.preprocessing.dataset import Dataset
    
    dataset = Dataset()
    original_image = dataset.generate_checkerboard(4, save=False)
    
    # Simulate measurement counts
    ideal_probs = np.array([0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25,
                            0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25])
    counts = CountsSimulator.simulate_counts(ideal_probs, shots=1000, seed=42)
    
    # Reconstruct
    reconstructor = ImageReconstructor((4, 4))
    reconstructed = reconstructor.reconstruct_complete(counts)
    
    print(f"Original shape: {original_image.shape}")
    print(f"Reconstructed shape: {reconstructed.shape}")
    print(f"Reconstruction range: [{reconstructed.min():.3f}, {reconstructed.max():.3f}]")
    
    # Quality metrics
    metrics = reconstructor.get_reconstruction_quality(original_image, reconstructed)
    print(f"\nQuality metrics:")
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.6f}")
