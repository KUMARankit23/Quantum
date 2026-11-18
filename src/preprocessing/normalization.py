"""
Image normalization and preprocessing utilities.
"""

import numpy as np
from typing import Tuple
from PIL import Image


def normalize_image(image: np.ndarray) -> np.ndarray:
    """
    Normalize image to [0, 1] range.
    
    Args:
        image: Input image array
        
    Returns:
        Normalized image
    """
    image_min = image.min()
    image_max = image.max()
    
    if image_max == image_min:
        # All pixels same value - return 0.5
        return np.full_like(image, 0.5, dtype=float)
    
    return (image - image_min) / (image_max - image_min)


def resize_image(image: np.ndarray, target_size: int) -> np.ndarray:
    """
    Resize image to target size using PIL (bicubic interpolation).
    
    Args:
        image: Input image array (normalized or 0-255)
        target_size: Target size (square: target_size × target_size)
        
    Returns:
        Resized image as numpy array
    """
    # Convert to 0-255 for PIL
    if image.max() <= 1.0:
        image_8bit = (image * 255).astype(np.uint8)
    else:
        image_8bit = np.clip(image, 0, 255).astype(np.uint8)
    
    # Resize using PIL
    pil_image = Image.fromarray(image_8bit, mode='L')
    resized = pil_image.resize((target_size, target_size), Image.BICUBIC)
    
    # Convert back to normalized [0, 1]
    return np.array(resized, dtype=float) / 255.0


def flatten_image(image: np.ndarray) -> np.ndarray:
    """
    Flatten 2D image to 1D pixel array.
    
    Args:
        image: 2D image array
        
    Returns:
        1D flattened array
    """
    return image.flatten()


def unflatten_image(pixels: np.ndarray, size: int) -> np.ndarray:
    """
    Reshape 1D pixel array to 2D image.
    
    Args:
        pixels: 1D pixel array
        size: Target image size (square: size × size)
        
    Returns:
        2D image array
    """
    return pixels.reshape((size, size))


def clip_image(image: np.ndarray) -> np.ndarray:
    """
    Clip image values to [0, 1] range.
    
    Args:
        image: Input image
        
    Returns:
        Clipped image
    """
    return np.clip(image, 0, 1)


def quantize_intensity(image: np.ndarray, levels: int = 256) -> np.ndarray:
    """
    Quantize image intensities to discrete levels.
    
    Args:
        image: Input image (assumed normalized [0, 1])
        levels: Number of quantization levels
        
    Returns:
        Quantized image
    """
    quantized = np.round(image * (levels - 1)) / (levels - 1)
    return np.clip(quantized, 0, 1)


def preprocess_image(image_path: str, target_size: int, 
                     quantize: bool = True, 
                     quantization_levels: int = 256) -> np.ndarray:
    """
    Full preprocessing pipeline: load → normalize → resize → quantize.
    
    Args:
        image_path: Path to image file
        target_size: Target image size (square)
        quantize: Whether to quantize
        quantization_levels: Number of quantization levels
        
    Returns:
        Preprocessed image
    """
    # Load
    image = Image.open(image_path).convert('L')
    array = np.array(image, dtype=float) / 255.0
    
    # Normalize
    normalized = normalize_image(array)
    
    # Resize
    resized = resize_image(normalized, target_size)
    
    # Quantize
    if quantize:
        quantized = quantize_intensity(resized, quantization_levels)
    else:
        quantized = resized
    
    return quantized
