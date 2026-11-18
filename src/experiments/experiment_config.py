"""
Experiment configuration management.
"""

import json
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class ExperimentConfig:
    """Configuration for a single experiment."""
    
    # Image parameters
    image_type: str = "checkerboard"  # Image pattern type
    image_size: int = 4  # Image resolution (size × size)
    intensity_representation: str = "normalized"  # binary, grayscale, normalized
    
    # Quantum parameters
    encoding_method: str = "amplitude"  # Quantum encoding method
    circuit_type: str = "basic"  # Circuit complexity: basic, medium, deep
    shots: int = 1000  # Number of measurement shots
    
    # Noise parameters
    noise_model: str = "none"  # Noise type: none, bitflip, phaseflip, depolarizing, readout
    noise_probability: float = 0.0  # Noise level (0.0 - 1.0)
    
    # Reproducibility
    seed: int = 42  # Random seed
    
    # Experiment metadata
    experiment_id: str = "default"
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExperimentConfig':
        """Create from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
    
    @classmethod
    def from_json(cls, json_str: str) -> 'ExperimentConfig':
        """Create from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)


class ConfigurationManager:
    """Manages experiment configurations."""
    
    def __init__(self, config_dir: str = "configs"):
        """
        Initialize configuration manager.
        
        Args:
            config_dir: Directory for configuration files
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def save_config(self, config: ExperimentConfig, filename: str = None) -> str:
        """
        Save configuration to file.
        
        Args:
            config: ExperimentConfig to save
            filename: Filename (optional; uses experiment_id if not provided)
            
        Returns:
            Path to saved file
        """
        if filename is None:
            filename = f"{config.experiment_id}.json"
        
        filepath = self.config_dir / filename
        
        with open(filepath, 'w') as f:
            f.write(config.to_json())
        
        return str(filepath)
    
    def load_config(self, filename: str) -> ExperimentConfig:
        """
        Load configuration from file.
        
        Args:
            filename: Configuration filename
            
        Returns:
            Loaded ExperimentConfig
        """
        filepath = self.config_dir / filename
        
        with open(filepath, 'r') as f:
            config = ExperimentConfig.from_json(f.read())
        
        return config
    
    def create_default_configs(self) -> None:
        """Create default experiment configurations."""
        configs = {
            "resolution_2x2": ExperimentConfig(
                experiment_id="resolution_2x2",
                image_type="checkerboard",
                image_size=2,
                description="Resolution experiment: 2×2 image"
            ),
            "resolution_4x4": ExperimentConfig(
                experiment_id="resolution_4x4",
                image_type="checkerboard",
                image_size=4,
                description="Resolution experiment: 4×4 image"
            ),
            "resolution_8x8": ExperimentConfig(
                experiment_id="resolution_8x8",
                image_type="checkerboard",
                image_size=8,
                description="Resolution experiment: 8×8 image"
            ),
            "resolution_16x16": ExperimentConfig(
                experiment_id="resolution_16x16",
                image_type="checkerboard",
                image_size=16,
                description="Resolution experiment: 16×16 image"
            ),
            "shots_100": ExperimentConfig(
                experiment_id="shots_100",
                shots=100,
                description="Shots experiment: 100 shots"
            ),
            "shots_500": ExperimentConfig(
                experiment_id="shots_500",
                shots=500,
                description="Shots experiment: 500 shots"
            ),
            "shots_1000": ExperimentConfig(
                experiment_id="shots_1000",
                shots=1000,
                description="Shots experiment: 1000 shots"
            ),
            "shots_5000": ExperimentConfig(
                experiment_id="shots_5000",
                shots=5000,
                description="Shots experiment: 5000 shots"
            ),
            "noise_bitflip_1pct": ExperimentConfig(
                experiment_id="noise_bitflip_1pct",
                noise_model="bitflip",
                noise_probability=0.01,
                description="Noise experiment: 1% bit-flip"
            ),
            "noise_depolarizing_5pct": ExperimentConfig(
                experiment_id="noise_depolarizing_5pct",
                noise_model="depolarizing",
                noise_probability=0.05,
                description="Noise experiment: 5% depolarizing"
            ),
            "circuit_basic": ExperimentConfig(
                experiment_id="circuit_basic",
                circuit_type="basic",
                description="Circuit complexity: basic"
            ),
            "circuit_medium": ExperimentConfig(
                experiment_id="circuit_medium",
                circuit_type="medium",
                description="Circuit complexity: medium"
            ),
            "circuit_deep": ExperimentConfig(
                experiment_id="circuit_deep",
                circuit_type="deep",
                description="Circuit complexity: deep"
            ),
        }
        
        for name, config in configs.items():
            self.save_config(config, f"{name}.json")
        
        print(f"✓ Created {len(configs)} default configurations")


def get_default_config() -> ExperimentConfig:
    """Get default configuration."""
    return ExperimentConfig(
        experiment_id="default_experiment",
        image_type="checkerboard",
        image_size=4,
        shots=1000,
        noise_model="none",
        seed=42,
    )


if __name__ == "__main__":
    # Create and test configurations
    config_mgr = ConfigurationManager()
    
    # Create default configs
    config_mgr.create_default_configs()
    
    # Load and display one
    config = config_mgr.load_config("resolution_4x4.json")
    print("\nLoaded configuration:")
    print(config.to_json())
