"""
Image quality evaluation metrics.
Implements MSE, PSNR, SSIM, and fidelity measures.
"""

import numpy as np
from typing import Tuple
from scipy.ndimage import uniform_filter


def calculate_mse(image1: np.ndarray, image2: np.ndarray) -> float:
    """
    Calculate Mean Squared Error.
    
    MSE = (1/N) Σ (I1[i] - I2[i])²
    
    Args:
        image1: First image (reference or original)
        image2: Second image (test or reconstructed)
        
    Returns:
        MSE value (0 = identical, 1 = completely different)
    """
    if image1.shape != image2.shape:
        raise ValueError(f"Image shapes differ: {image1.shape} vs {image2.shape}")
    
    mse = np.mean((image1 - image2) ** 2)
    return float(mse)


def calculate_psnr(image1: np.ndarray, image2: np.ndarray, 
                   max_value: float = 1.0) -> float:
    """
    Calculate Peak Signal-to-Noise Ratio.
    
    PSNR = 10 · log₁₀(MAX²/MSE) dB
    
    Args:
        image1: Reference image
        image2: Test image
        max_value: Maximum possible pixel value (default 1.0 for normalized images)
        
    Returns:
        PSNR in dB (higher is better; >20 dB is reasonable, >30 dB is good)
    """
    mse = calculate_mse(image1, image2)
    
    if mse == 0:
        # Identical images
        return float('inf')
    
    psnr = 10 * np.log10((max_value ** 2) / mse)
    return float(psnr)


def calculate_ssim(image1: np.ndarray, image2: np.ndarray, 
                   window_size: int = 11) -> float:
    """
    Calculate Structural Similarity Index Measure (SSIM).
    
    Simplified version: single-scale SSIM without windowing.
    
    Args:
        image1: Reference image
        image2: Test image
        window_size: Window size for local computation (must be odd)
        
    Returns:
        SSIM value (-1 to 1, typically 0 to 1; 1 = identical)
    """
    if image1.shape != image2.shape:
        raise ValueError(f"Image shapes differ: {image1.shape} vs {image2.shape}")
    
    # Constants to avoid division by zero
    c1 = (0.01) ** 2
    c2 = (0.03) ** 2
    
    # Compute means
    mu1 = uniform_filter(image1.astype(float), size=window_size)
    mu2 = uniform_filter(image2.astype(float), size=window_size)
    
    # Compute variances
    sigma1_sq = uniform_filter(image1.astype(float) ** 2, size=window_size) - mu1 ** 2
    sigma2_sq = uniform_filter(image2.astype(float) ** 2, size=window_size) - mu2 ** 2
    sigma12 = uniform_filter(image1.astype(float) * image2.astype(float), 
                             size=window_size) - mu1 * mu2
    
    # Compute SSIM
    numerator = (2 * mu1 * mu2 + c1) * (2 * sigma12 + c2)
    denominator = (mu1 ** 2 + mu2 ** 2 + c1) * (sigma1_sq + sigma2_sq + c2)
    
    ssim_map = numerator / denominator
    
    # Return mean SSIM
    return float(np.mean(ssim_map))


def calculate_fidelity(original_probs: np.ndarray, 
                      reconstructed_probs: np.ndarray) -> float:
    """
    Calculate state fidelity between two probability distributions.
    
    For normalized distributions, approximates quantum fidelity.
    
    Fidelity = (Σ √(p_i · q_i))²
    
    Args:
        original_probs: Original probability distribution (normalized)
        reconstructed_probs: Reconstructed distribution (normalized)
        
    Returns:
        Fidelity value (0 to 1; 1 = identical distributions)
    """
    if len(original_probs) != len(reconstructed_probs):
        raise ValueError("Probability distributions have different lengths")
    
    # Ensure normalized
    original_probs = np.asarray(original_probs)
    reconstructed_probs = np.asarray(reconstructed_probs)
    
    original_probs = original_probs / np.sum(original_probs)
    reconstructed_probs = reconstructed_probs / np.sum(reconstructed_probs)
    
    # Calculate fidelity
    fidelity = np.sum(np.sqrt(original_probs * reconstructed_probs)) ** 2
    
    return float(np.clip(fidelity, 0, 1))


def calculate_correlation(image1: np.ndarray, image2: np.ndarray) -> float:
    """
    Calculate Pearson correlation coefficient between images.
    
    Args:
        image1: First image
        image2: Second image
        
    Returns:
        Correlation (-1 to 1; 1 = perfectly correlated)
    """
    if image1.shape != image2.shape:
        raise ValueError(f"Image shapes differ: {image1.shape} vs {image2.shape}")
    
    # Flatten images
    flat1 = image1.flatten()
    flat2 = image2.flatten()
    
    # Calculate correlation
    correlation = np.corrcoef(flat1, flat2)[0, 1]
    
    return float(correlation)


def calculate_mae(image1: np.ndarray, image2: np.ndarray) -> float:
    """
    Calculate Mean Absolute Error.
    
    MAE = (1/N) Σ |I1[i] - I2[i]|
    
    Args:
        image1: First image
        image2: Second image
        
    Returns:
        MAE value
    """
    if image1.shape != image2.shape:
        raise ValueError(f"Image shapes differ: {image1.shape} vs {image2.shape}")
    
    mae = np.mean(np.abs(image1 - image2))
    return float(mae)


def calculate_all_metrics(original: np.ndarray, 
                         reconstructed: np.ndarray) -> dict:
    """
    Calculate all available metrics at once.
    
    Args:
        original: Original image
        reconstructed: Reconstructed image
        
    Returns:
        Dictionary with all metric values
    """
    return {
        "mse": calculate_mse(original, reconstructed),
        "psnr": calculate_psnr(original, reconstructed),
        "ssim": calculate_ssim(original, reconstructed),
        "mae": calculate_mae(original, reconstructed),
        "correlation": calculate_correlation(original, reconstructed),
    }


if __name__ == "__main__":
    # Quick test
    from src.preprocessing.dataset import Dataset
    
    dataset = Dataset()
    image1 = dataset.generate_checkerboard(4, save=False)
    image2 = image1.copy()
    image2[0, 0] = 1 - image2[0, 0]  # Flip one pixel
    
    print(f"MSE: {calculate_mse(image1, image2):.6f}")
    print(f"PSNR: {calculate_psnr(image1, image2):.2f} dB")
    print(f"SSIM: {calculate_ssim(image1, image2):.6f}")
    print(f"Correlation: {calculate_correlation(image1, image2):.6f}")
