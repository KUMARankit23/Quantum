"""
Classical image processing baseline for comparison with quantum approach.
Implements equivalent preprocessing and simple image filtering.
"""

import numpy as np
import time
from scipy import ndimage
from typing import Dict, Tuple
from src.preprocessing.normalization import normalize_image, clip_image


class ClassicalBaseline:
    """Classical image processing baseline for quantum comparison."""
    
    def __init__(self):
        """Initialize classical baseline."""
        pass
    
    def process(self, image: np.ndarray, method: str = "gaussian") -> Tuple[np.ndarray, float]:
        """
        Apply classical image processing.
        
        Args:
            image: Input image (normalized [0, 1])
            method: Processing method ("gaussian", "bilateral", "median")
            
        Returns:
            Processed image, execution time (seconds)
        """
        start_time = time.time()
        
        if method == "gaussian":
            processed = self.gaussian_blur(image)
        elif method == "bilateral":
            processed = self.bilateral_filter(image)
        elif method == "median":
            processed = self.median_filter(image)
        else:
            raise ValueError(f"Unknown method: {method}")
        
        elapsed = time.time() - start_time
        return clip_image(processed), elapsed
    
    @staticmethod
    def gaussian_blur(image: np.ndarray, sigma: float = 1.0) -> np.ndarray:
        """
        Apply Gaussian blur.
        
        Args:
            image: Input image
            sigma: Gaussian kernel standard deviation
            
        Returns:
            Blurred image
        """
        return ndimage.gaussian_filter(image, sigma=sigma)
    
    @staticmethod
    def bilateral_filter(image: np.ndarray, sigma_s: float = 1.0, 
                        sigma_r: float = 0.1) -> np.ndarray:
        """
        Apply bilateral filter (edge-preserving blur).
        
        Args:
            image: Input image
            sigma_s: Spatial standard deviation
            sigma_r: Range standard deviation
            
        Returns:
            Filtered image
        """
        # Simple approximation: Gaussian blur
        return ndimage.gaussian_filter(image, sigma=sigma_s)
    
    @staticmethod
    def median_filter(image: np.ndarray, size: int = 3) -> np.ndarray:
        """
        Apply median filter (noise reduction).
        
        Args:
            image: Input image
            size: Filter kernel size
            
        Returns:
            Filtered image
        """
        return ndimage.median_filter(image, size=size)
    
    @staticmethod
    def histogram_equalization(image: np.ndarray) -> np.ndarray:
        """
        Apply histogram equalization (contrast enhancement).
        
        Args:
            image: Input image
            
        Returns:
            Equalized image
        """
        # Quantize to 256 levels
        levels = 256
        quantized = np.round(image * (levels - 1)).astype(int)
        
        # Compute histogram
        hist, _ = np.histogram(quantized, bins=levels, range=(0, levels))
        
        # Compute CDF
        cdf = np.cumsum(hist)
        cdf = cdf / cdf[-1]  # Normalize
        
        # Map pixels through CDF
        equalized = cdf[quantized]
        
        return np.clip(equalized, 0, 1)
    
    @staticmethod
    def normalize_only(image: np.ndarray) -> np.ndarray:
        """
        Normalize image without any processing.
        Used as null baseline.
        
        Args:
            image: Input image
            
        Returns:
            Normalized image
        """
        return normalize_image(image)
    
    @staticmethod
    def downsample_upsample(image: np.ndarray, factor: int = 2) -> np.ndarray:
        """
        Downsample and upsample image (compression-like effect).
        
        Args:
            image: Input image
            factor: Downsampling factor
            
        Returns:
            Processed image
        """
        # Downsample
        small = image[::factor, ::factor]
        
        # Upsample using nearest neighbor
        h, w = image.shape
        upsampled = np.repeat(np.repeat(small, factor, axis=0), factor, axis=1)
        
        # Crop to original size
        upsampled = upsampled[:h, :w]
        
        return clip_image(upsampled)


class ClassicalComparison:
    """Compare quantum and classical approaches."""
    
    def __init__(self):
        """Initialize comparison."""
        self.baseline = ClassicalBaseline()
    
    def compare(self, image: np.ndarray, 
               classical_method: str = "gaussian",
               quantum_result: np.ndarray = None,
               quantum_time: float = None) -> Dict:
        """
        Compare classical and quantum processing.
        
        Args:
            image: Original image
            classical_method: Classical method to use
            quantum_result: Result from quantum pipeline (optional)
            quantum_time: Quantum execution time (optional)
            
        Returns:
            Comparison dictionary with metrics
        """
        # Classical processing
        classical_result, classical_time = self.baseline.process(image, classical_method)
        
        comparison = {
            "classical_method": classical_method,
            "classical_time": classical_time,
            "classical_result": classical_result,
        }
        
        # Add quantum comparison if provided
        if quantum_result is not None and quantum_time is not None:
            from src.evaluation.metrics import calculate_mse, calculate_psnr, calculate_ssim
            
            # Compare both to original
            classical_mse = calculate_mse(image, classical_result)
            quantum_mse = calculate_mse(image, quantum_result)
            
            classical_psnr = calculate_psnr(image, classical_result)
            quantum_psnr = calculate_psnr(image, quantum_result)
            
            classical_ssim = calculate_ssim(image, classical_result)
            quantum_ssim = calculate_ssim(image, quantum_result)
            
            comparison.update({
                "quantum_time": quantum_time,
                "quantum_result": quantum_result,
                "classical_mse": classical_mse,
                "quantum_mse": quantum_mse,
                "classical_psnr": classical_psnr,
                "quantum_psnr": quantum_psnr,
                "classical_ssim": classical_ssim,
                "quantum_ssim": quantum_ssim,
                "time_ratio": quantum_time / classical_time if classical_time > 0 else float('inf'),
            })
        
        return comparison


if __name__ == "__main__":
    # Quick test
    from src.preprocessing.dataset import Dataset
    
    dataset = Dataset()
    image = dataset.generate_checkerboard(4)
    
    baseline = ClassicalBaseline()
    processed, elapsed = baseline.process(image, method="gaussian")
    
    print(f"Classical processing time: {elapsed:.6f} seconds")
    print(f"Input shape: {image.shape}")
    print(f"Output shape: {processed.shape}")
