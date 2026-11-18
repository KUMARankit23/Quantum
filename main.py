"""
Quantum Image Processing Performance Research Project
Main entry point for Phases 1-2

Phase 1: Foundation & Dataset
- Project structure
- Dataset generation
- Image preprocessing
- Classical baseline
- Evaluation metrics

Phase 2: Quantum Implementation
- Amplitude encoding
- Quantum circuits
- Measurement processing
- Image reconstruction
- Experiment runner
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.preprocessing.dataset import Dataset
from src.preprocessing.normalization import normalize_image, resize_image, quantize_intensity
from src.classical.baseline import ClassicalBaseline
from src.evaluation.metrics import calculate_all_metrics
from src.experiments.experiment_config import ConfigurationManager, get_default_config


def phase_1_initialization():
    """Phase 1: Initialize project foundation."""
    
    print("=" * 70)
    print("QUANTUM IMAGE PROCESSING PERFORMANCE RESEARCH")
    print("Phase 1: Foundation & Dataset Generation")
    print("=" * 70)
    
    # Step 1: Generate datasets
    print("\n[1/4] Generating test datasets...")
    dataset = Dataset("data/raw")
    datasets = dataset.generate_all_standard_datasets()
    print(f"✓ Generated {len(datasets)} image types across 4 resolutions")
    
    # Step 2: Test preprocessing pipeline
    print("\n[2/4] Testing preprocessing pipeline...")
    test_image = datasets["checkerboard"][4]
    print(f"  Original image shape: {test_image.shape}")
    print(f"  Original image range: [{test_image.min():.3f}, {test_image.max():.3f}]")
    
    # Test normalization
    normalized = normalize_image(test_image)
    print(f"  Normalized range: [{normalized.min():.3f}, {normalized.max():.3f}]")
    
    # Test resizing
    resized = resize_image(test_image, 8)
    print(f"  Resized to 8×8: {resized.shape}")
    
    # Test quantization
    quantized = quantize_intensity(test_image, levels=256)
    print(f"  Quantized to 256 levels: range [{quantized.min():.3f}, {quantized.max():.3f}]")
    
    print("✓ Preprocessing pipeline functional")
    
    # Step 3: Test classical baseline
    print("\n[3/4] Testing classical baseline...")
    baseline = ClassicalBaseline()
    
    test_sizes = [2, 4, 8]
    for size in test_sizes:
        image = datasets["checkerboard"][size]
        processed, elapsed = baseline.process(image, method="gaussian")
        metrics = calculate_all_metrics(image, processed)
        
        print(f"  {size}×{size} image: {elapsed*1000:.2f}ms (PSNR: {metrics['psnr']:.2f} dB)")
    
    print("✓ Classical baseline functional")
    
    # Step 4: Create experiment configurations
    print("\n[4/4] Creating experiment configurations...")
    config_mgr = ConfigurationManager("configs")
    config_mgr.create_default_configs()
    print("✓ Experiment configurations created")
    
    # Summary
    print("\n" + "=" * 70)
    print("PHASE 1 COMPLETE")
    print("=" * 70)
    print("\nNext steps:")
    print("  1. Review generated images in data/raw/")
    print("  2. Review configurations in configs/")
    print("  3. Proceed to Phase 2: Quantum encoding implementation")
    print("\nTo test individual components:")
    print("  python -m src.preprocessing.dataset")
    print("  python -m src.classical.baseline")
    print("  python -m src.evaluation.metrics")
    print("=" * 70)


def quick_test():
    """Quick functionality test (Phase 1 & 2)."""
    print("\n[QUICK TEST] Verifying all components...")
    
    try:
        # Phase 1: Core components
        from src.preprocessing.dataset import Dataset
        from src.preprocessing.normalization import normalize_image
        from src.classical.baseline import ClassicalBaseline
        from src.evaluation.metrics import calculate_all_metrics
        from src.experiments.experiment_config import get_default_config
        
        # Phase 2: Quantum components
        from src.quantum.encoding import AmplitudeEncoder
        from src.quantum.circuit_builder import CircuitBuilder
        from src.reconstruction.measurement_processor import CountsSimulator
        from src.reconstruction.image_reconstructor import ImageReconstructor
        
        # Create test image
        dataset = Dataset("data/raw")
        image = dataset.generate_checkerboard(4, save=False)
        
        # Test Phase 1
        baseline = ClassicalBaseline()
        processed, time_taken = baseline.process(image)
        metrics = calculate_all_metrics(image, processed)
        
        # Test Phase 2: Quantum encoding
        encoder = AmplitudeEncoder(image)
        amplitudes = encoder.encode()
        assert encoder.verify_encoding(), "Encoding verification failed"
        
        # Test Phase 2: Circuit building
        builder = CircuitBuilder()
        circuit = builder.build_state_preparation(image, "basic")
        circuit_info = builder.get_circuit_info(circuit)
        
        # Test Phase 2: Measurement & reconstruction
        probs = encoder.get_measurement_probabilities()
        counts = CountsSimulator.simulate_counts(probs, shots=100, seed=42)
        
        reconstructor = ImageReconstructor((4, 4))
        reconstructed = reconstructor.reconstruct_complete(counts)
        
        config = get_default_config()
        
        print("[OK] Phase 1 components verified successfully!")
        print("[OK] Phase 2 quantum components verified successfully!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error during verification: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Quantum Image Processing Research Project"
    )
    parser.add_argument(
        "--test", 
        action="store_true",
        help="Run quick functionality test"
    )
    
    args = parser.parse_args()
    
    if args.test:
        success = quick_test()
        sys.exit(0 if success else 1)
    else:
        phase_1_initialization()
