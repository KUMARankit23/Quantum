"""
Dataset generator for quantum image processing experiments.
Creates reproducible, deterministic test images.
"""

import numpy as np
from PIL import Image, ImageDraw
import os
from pathlib import Path
from typing import Tuple, Dict, Optional


class Dataset:
    """Generates and manages test datasets."""
    
    def __init__(self, data_dir: str = "data/raw"):
        """
        Initialize dataset generator.
        
        Args:
            data_dir: Directory to save generated images
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_checkerboard(self, size: int, save: bool = True) -> np.ndarray:
        """
        Generate checkerboard pattern.
        
        Args:
            size: Image size (size × size pixels)
            save: Whether to save as PNG
            
        Returns:
            Image as numpy array, normalized [0, 1]
        """
        # Create alternating 0 and 1 pattern
        checker = np.zeros((size, size))
        for i in range(size):
            for j in range(size):
                if (i + j) % 2 == 0:
                    checker[i, j] = 1.0
                else:
                    checker[i, j] = 0.0
        
        if save:
            filename = self.data_dir / f"checkerboard_{size}x{size}.png"
            self._save_normalized_image(checker, filename)
        
        return checker
    
    def generate_gradient(self, size: int, direction: str = "horizontal", 
                         save: bool = True) -> np.ndarray:
        """
        Generate gradient pattern.
        
        Args:
            size: Image size
            direction: "horizontal", "vertical", or "diagonal"
            save: Whether to save as PNG
            
        Returns:
            Image as numpy array, normalized [0, 1]
        """
        gradient = np.zeros((size, size))
        
        if direction == "horizontal":
            for j in range(size):
                gradient[:, j] = j / (size - 1) if size > 1 else 0.5
        elif direction == "vertical":
            for i in range(size):
                gradient[i, :] = i / (size - 1) if size > 1 else 0.5
        elif direction == "diagonal":
            for i in range(size):
                for j in range(size):
                    gradient[i, j] = (i + j) / (2 * (size - 1)) if size > 1 else 0.5
        
        if save:
            filename = self.data_dir / f"gradient_{direction}_{size}x{size}.png"
            self._save_normalized_image(gradient, filename)
        
        return gradient
    
    def generate_circle(self, size: int, save: bool = True) -> np.ndarray:
        """
        Generate image with centered circle.
        
        Args:
            size: Image size
            save: Whether to save as PNG
            
        Returns:
            Image as numpy array, normalized [0, 1]
        """
        circle = np.zeros((size, size))
        center = size / 2
        radius = size / 3
        
        for i in range(size):
            for j in range(size):
                distance = np.sqrt((i - center) ** 2 + (j - center) ** 2)
                if distance <= radius:
                    circle[i, j] = 1.0
                else:
                    circle[i, j] = 0.0
        
        if save:
            filename = self.data_dir / f"circle_{size}x{size}.png"
            self._save_normalized_image(circle, filename)
        
        return circle
    
    def generate_square(self, size: int, save: bool = True) -> np.ndarray:
        """
        Generate image with centered square.
        
        Args:
            size: Image size
            save: Whether to save as PNG
            
        Returns:
            Image as numpy array, normalized [0, 1]
        """
        square = np.zeros((size, size))
        margin = size // 4
        
        for i in range(margin, size - margin):
            for j in range(margin, size - margin):
                square[i, j] = 1.0
        
        if save:
            filename = self.data_dir / f"square_{size}x{size}.png"
            self._save_normalized_image(square, filename)
        
        return square
    
    def generate_random_binary(self, size: int, seed: int = 42, 
                               save: bool = True) -> np.ndarray:
        """
        Generate random binary image.
        
        Args:
            size: Image size
            seed: Random seed for reproducibility
            save: Whether to save as PNG
            
        Returns:
            Image as numpy array, normalized [0, 1]
        """
        np.random.seed(seed)
        binary = np.random.randint(0, 2, size=(size, size)).astype(float)
        
        if save:
            filename = self.data_dir / f"random_binary_{size}x{size}_seed{seed}.png"
            self._save_normalized_image(binary, filename)
        
        return binary
    
    def generate_random_grayscale(self, size: int, seed: int = 42, 
                                  save: bool = True) -> np.ndarray:
        """
        Generate random grayscale image.
        
        Args:
            size: Image size
            seed: Random seed for reproducibility
            save: Whether to save as PNG
            
        Returns:
            Image as numpy array, normalized [0, 1]
        """
        np.random.seed(seed)
        grayscale = np.random.rand(size, size).astype(float)
        
        if save:
            filename = self.data_dir / f"random_grayscale_{size}x{size}_seed{seed}.png"
            self._save_normalized_image(grayscale, filename)
        
        return grayscale
    
    def generate_all_standard_datasets(self) -> Dict[str, Dict[int, np.ndarray]]:
        """
        Generate all standard test images for all resolutions.
        
        Returns:
            Dictionary: {image_type: {size: image_array}}
        """
        resolutions = [2, 4, 8, 16]
        datasets = {}
        
        for size in resolutions:
            print(f"Generating images for {size}×{size} resolution...")
            
            # Checkerboard
            if "checkerboard" not in datasets:
                datasets["checkerboard"] = {}
            datasets["checkerboard"][size] = self.generate_checkerboard(size)
            
            # Gradients
            for direction in ["horizontal", "vertical", "diagonal"]:
                key = f"gradient_{direction}"
                if key not in datasets:
                    datasets[key] = {}
                datasets[key][size] = self.generate_gradient(size, direction)
            
            # Shapes
            if "circle" not in datasets:
                datasets["circle"] = {}
            datasets["circle"][size] = self.generate_circle(size)
            
            if "square" not in datasets:
                datasets["square"] = {}
            datasets["square"][size] = self.generate_square(size)
            
            # Random
            if "random_binary" not in datasets:
                datasets["random_binary"] = {}
            datasets["random_binary"][size] = self.generate_random_binary(size)
            
            if "random_grayscale" not in datasets:
                datasets["random_grayscale"] = {}
            datasets["random_grayscale"][size] = self.generate_random_grayscale(size)
        
        print(f"✓ Generated {len(datasets)} image types × {len(resolutions)} resolutions")
        return datasets
    
    @staticmethod
    def _save_normalized_image(image: np.ndarray, filepath: Path) -> None:
        """
        Save normalized image (0-1) as PNG file.
        
        Args:
            image: Normalized image array
            filepath: Where to save
        """
        # Convert to 8-bit
        image_8bit = (np.clip(image, 0, 1) * 255).astype(np.uint8)
        
        # Save
        pil_image = Image.fromarray(image_8bit, mode='L')
        pil_image.save(filepath)
    
    @staticmethod
    def load_image(filepath: str) -> np.ndarray:
        """
        Load image from file and normalize to [0, 1].
        
        Args:
            filepath: Path to image file
            
        Returns:
            Normalized image array
        """
        image = Image.open(filepath).convert('L')
        array = np.array(image, dtype=float)
        return array / 255.0
    
    @staticmethod
    def add_gaussian_noise(image: np.ndarray, stddev: float, 
                          seed: int = 42) -> np.ndarray:
        """
        Add Gaussian noise to image.
        
        Args:
            image: Image array [0, 1]
            stddev: Standard deviation of noise
            seed: Random seed
            
        Returns:
            Noisy image (clipped to [0, 1])
        """
        np.random.seed(seed)
        noise = np.random.normal(0, stddev, image.shape)
        noisy = np.clip(image + noise, 0, 1)
        return noisy


if __name__ == "__main__":
    # Generate all datasets
    dataset = Dataset("data/raw")
    datasets = dataset.generate_all_standard_datasets()
    print("\nDataset generation complete!")
    print(f"Images saved to: {dataset.data_dir}")
