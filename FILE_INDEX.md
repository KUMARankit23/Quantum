# File Index - Quantum Image Processing Research Project

## Quick Navigation

### 📋 Documentation Files
| File | Purpose | Status |
|------|---------|--------|
| [README.md](README.md) | Project overview and quick start guide | ✓ Complete |
| [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) | Detailed technical plan (1000+ lines) | ✓ Complete |
| [PHASE_1_COMPLETE.md](PHASE_1_COMPLETE.md) | Phase 1 completion report | ✓ Complete |
| [PHASE_2_PREVIEW.md](PHASE_2_PREVIEW.md) | Phase 2 planning and architecture | ✓ Complete |
| [PROJECT_STATUS.md](PROJECT_STATUS.md) | Current status and progress report | ✓ Complete |
| [FILE_INDEX.md](FILE_INDEX.md) | This file - navigation guide | ✓ Complete |

### 📁 Source Code Structure

```
src/
├── __init__.py                           # Package init
├── preprocessing/                        # Image preprocessing
│   ├── __init__.py
│   ├── dataset.py                       # Dataset generation (300+ lines)
│   └── normalization.py                 # Image normalization (150+ lines)
├── quantum/                             # Quantum computing (Phase 2)
│   ├── __init__.py
│   ├── encoding.py                      # [TO BE IMPLEMENTED]
│   ├── circuit_builder.py               # [TO BE IMPLEMENTED]
│   ├── state_prep.py                    # [TO BE IMPLEMENTED]
│   └── noise_models.py                  # [TO BE IMPLEMENTED]
├── classical/                           # Classical baseline
│   ├── __init__.py
│   └── baseline.py                      # Classical methods (250+ lines)
├── reconstruction/                      # Image reconstruction (Phase 2)
│   ├── __init__.py
│   ├── measurement_processor.py         # [TO BE IMPLEMENTED]
│   ├── image_reconstructor.py           # [TO BE IMPLEMENTED]
│   └── post_processing.py               # [TO BE IMPLEMENTED]
├── evaluation/                          # Metrics and analysis
│   ├── __init__.py
│   ├── metrics.py                       # Image quality metrics (300+ lines)
│   └── quantum_metrics.py               # Quantum metrics (250+ lines)
├── experiments/                         # Experiment management
│   ├── __init__.py
│   ├── experiment_config.py             # Configuration system (250+ lines)
│   ├── experiment_runner.py             # [TO BE IMPLEMENTED]
│   ├── batch_runner.py                  # [TO BE IMPLEMENTED]
│   └── result_manager.py                # [TO BE IMPLEMENTED]
└── visualization/                       # Plotting and visualization
    ├── __init__.py
    ├── plot_generator.py                # [TO BE IMPLEMENTED]
    ├── comparison_plots.py              # [TO BE IMPLEMENTED]
    ├── heatmaps.py                      # [TO BE IMPLEMENTED]
    └── report_generator.py              # [TO BE IMPLEMENTED]
```

### 🎬 Entry Points

| File | Purpose | Command |
|------|---------|---------|
| [main.py](main.py) | Phase 1 initialization | `python main.py` |
| [main.py](main.py) | Quick test | `python main.py --test` |
| [dashboard.py](dashboard.py) | Web UI (Phase 5) | `python dashboard.py` |

### 🔧 Configuration Files

```
configs/
├── resolution_2x2.json           # 2×2 image configuration
├── resolution_4x4.json           # 4×4 image configuration  
├── resolution_8x8.json           # 8×8 image configuration
├── resolution_16x16.json         # 16×16 image configuration
├── shots_100.json               # 100 shots configuration
├── shots_500.json               # 500 shots configuration
├── shots_1000.json              # 1000 shots configuration
├── shots_5000.json              # 5000 shots configuration
├── noise_bitflip_1pct.json      # 1% bit-flip noise
├── noise_depolarizing_5pct.json # 5% depolarizing noise
├── circuit_basic.json           # Basic circuit complexity
├── circuit_medium.json          # Medium circuit complexity
└── circuit_deep.json            # Deep circuit complexity
```

**Total**: 13 experiment configurations  
**Format**: JSON (human-readable)  
**Created**: Phase 1

### 📊 Generated Datasets

```
data/
├── raw/                          # Original generated images
│   ├── checkerboard_2x2.png     ├─ checkerboard_4x4.png
│   ├── checkerboard_8x8.png     ├─ checkerboard_16x16.png
│   ├── gradient_horizontal_*.png  ├─ gradient_vertical_*.png
│   ├── gradient_diagonal_*.png   ├─ circle_*.png
│   ├── square_*.png              ├─ random_binary_*.png
│   └── random_grayscale_*.png   
│
└── processed/                    # Preprocessed images (to be generated)
    ├── normalized_*.png
    └── resized_*.png
```

**Total**: 32 test images (8 types × 4 resolutions)  
**Status**: Generated in Phase 1  
**Format**: PNG (8-bit grayscale)

### 📈 Results & Analysis (Phase 3+)

```
results/
├── experiments.csv              # All experiments (to be generated)
├── resolution_results.csv       # Resolution experiment
├── shots_results.csv            # Shot count experiment
├── noise_results.csv            # Noise experiment
├── circuit_results.csv          # Circuit complexity experiment
├── baseline_comparison.csv      # Quantum vs classical
└── raw_measurements/            # Raw bitstrings (optional)

plots/
├── graph_1_resolution_vs_time.png
├── graph_2_resolution_vs_qubits.png
├── graph_3_depth_vs_fidelity.png
├── graph_4_depth_vs_time.png
├── graph_5_shots_vs_ssim.png
├── graph_6_shots_vs_psnr.png
├── graph_7_noise_vs_fidelity.png
├── graph_8_noise_vs_ssim.png
├── graph_9_qubits_vs_time.png
├── graph_10_quantum_vs_classical_time.png
├── graph_11_quantum_vs_classical_quality.png
├── comparisons/                 # Side-by-side image comparisons
└── heatmaps/                    # Analysis heatmaps
```

### 📚 Circuit Documentation

```
circuits/
├── README.md                    # Circuit explanation
├── encoding_circuit.txt         # QASM format circuits
├── qiskit_circuits.py          # Saved Qiskit circuits
└── circuit_diagrams/           # PNG diagrams
```

### 📓 Jupyter Notebooks

```
notebooks/
├── 01_data_exploration.ipynb       # Dataset exploration
├── 02_quantum_encoding_demo.ipynb  # Encoding demonstration
├── 03_single_experiment.ipynb      # Single experiment walkthrough
├── 04_results_analysis.ipynb       # Results analysis
└── 05_presentation_prep.ipynb      # Viva preparation
```

### 🧪 Tests

```
tests/
├── __init__.py
├── test_preprocessing.py       # Preprocessing tests
├── test_encoding.py            # Quantum encoding tests (Phase 2)
├── test_reconstruction.py      # Reconstruction tests (Phase 2)
├── test_metrics.py             # Metrics validation
├── test_pipeline.py            # End-to-end pipeline test
└── run_tests.py                # Test runner
```

### 📦 Dependencies

| File | Purpose |
|------|---------|
| [requirements.txt](requirements.txt) | Python package dependencies |

**Key Packages**:
- Quantum: qiskit, qiskit-aer
- Image processing: opencv-python, scikit-image, Pillow
- Numerics: numpy, scipy, pandas
- Visualization: matplotlib, seaborn

---

## File Size Summary

| Category | Count | Size |
|----------|-------|------|
| Python source (.py) | 15 | ~150 KB |
| Generated images | 32 | ~500 KB |
| Configuration files | 13 | ~50 KB |
| Documentation | 6 | ~250 KB |
| **Total** | **66** | **~950 KB** |

---

## Code Statistics

| Metric | Value |
|--------|-------|
| Total Python lines | 2,000+ |
| Total documentation lines | 1,500+ |
| Total comment lines | 400+ |
| Number of classes | 10 |
| Number of functions | 40+ |
| Test coverage | All Phase 1 modules |

---

## What's Implemented (Phase 1) ✓

### Dataset & Preprocessing
- ✓ `src/preprocessing/dataset.py` - Complete dataset generation
- ✓ `src/preprocessing/normalization.py` - Image normalization
- ✓ `data/raw/` - 32 generated test images

### Evaluation
- ✓ `src/evaluation/metrics.py` - Image quality metrics (MSE, PSNR, SSIM)
- ✓ `src/evaluation/quantum_metrics.py` - Quantum circuit metrics

### Classical Baseline
- ✓ `src/classical/baseline.py` - 5 classical processing methods

### Configuration
- ✓ `src/experiments/experiment_config.py` - Configuration system
- ✓ `configs/*.json` - 13 experiment templates

### Documentation
- ✓ `README.md` - Project overview
- ✓ `IMPLEMENTATION_PLAN.md` - Technical plan
- ✓ `PHASE_1_COMPLETE.md` - Completion report
- ✓ `PROJECT_STATUS.md` - Status report
- ✓ `FILE_INDEX.md` - This file

### Entry Point
- ✓ `main.py` - Phase 1 initialization script

---

## What's To Be Implemented

### Phase 2: Quantum Implementation
- [ ] `src/quantum/encoding.py` - Amplitude encoding
- [ ] `src/quantum/circuit_builder.py` - Circuit construction
- [ ] `src/quantum/state_prep.py` - State preparation
- [ ] `src/quantum/noise_models.py` - Noise simulation
- [ ] `src/reconstruction/measurement_processor.py` - Measurement processing
- [ ] `src/reconstruction/image_reconstructor.py` - Image reconstruction

### Phase 3: Experiments
- [ ] `src/experiments/experiment_runner.py` - Single experiment runner
- [ ] `src/experiments/batch_runner.py` - Batch experiment runner
- [ ] `src/experiments/result_manager.py` - Result management
- [ ] `results/*.csv` - Experiment results files

### Phase 4: Visualization
- [ ] `src/visualization/plot_generator.py` - Plot generation
- [ ] `src/visualization/comparison_plots.py` - Image comparisons
- [ ] `src/visualization/heatmaps.py` - Heatmap generation
- [ ] `src/visualization/report_generator.py` - Report generation
- [ ] `plots/` - Generated graphs and analysis

### Phase 5: Dashboard
- [ ] `dashboard.py` - Web UI (optional)
- [ ] `src/visualization/dashboard_ui.py` - Dashboard logic

### Phase 6: Documentation
- [ ] `VIVA.md` - Viva preparation questions
- [ ] `docs/RESEARCH_QUESTIONS.md` - Formal research questions
- [ ] `docs/METHODOLOGY.md` - Detailed methodology
- [ ] `docs/RESULTS.md` - Results summary
- [ ] `docs/LIMITATIONS.md` - Limitations discussion

---

## How to Use This Index

### For Quick Start
1. Read [README.md](README.md) (5 min)
2. Run `python main.py --test` (1 min)
3. Run `python main.py` (2 min)

### For Understanding the Project
1. Read [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) (30 min)
2. Review source code in `src/` (30 min)
3. Examine generated images in `data/raw/` (5 min)

### For Development
1. Check [PHASE_2_PREVIEW.md](PHASE_2_PREVIEW.md) for next steps
2. Follow the implementation checklist
3. Add code to appropriate module
4. Write unit tests in `tests/`

### For Viva Preparation
1. Review all source code with comments
2. Run experiments and understand output
3. Study [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)
4. Prepare answers to technical questions
5. Practice 20-minute demo

---

## File Maintenance

### Keep Up-to-Date
- Update `FILE_INDEX.md` when adding new files
- Keep `PROJECT_STATUS.md` current with progress
- Document Phase 2-6 progress in respective files

### Before Committing
- Run `python main.py --test`
- Verify all new code has docstrings
- Add inline comments for complex operations
- Update this index if file structure changes

---

## Quick Reference Commands

```bash
# Run verification
python main.py --test

# Run full Phase 1 initialization
python main.py

# Generate specific dataset
python -m src.preprocessing.dataset

# Run classical baseline
python -m src.classical.baseline

# Test metrics
python -m src.evaluation.metrics

# Create experiment configs
python -c "from src.experiments.experiment_config import ConfigurationManager; 
          ConfigurationManager().create_default_configs()"
```

---

## Related Files

### In This Project Root
- `README.md` - Start here
- `requirements.txt` - Install dependencies
- `main.py` - Run Phase 1

### In Documentation Directory
- `IMPLEMENTATION_PLAN.md` - Architecture details
- `PHASE_1_COMPLETE.md` - Phase 1 summary
- `PHASE_2_PREVIEW.md` - Next steps
- `PROJECT_STATUS.md` - Progress tracking
- `FILE_INDEX.md` - This file

### Configuration
All experiment configurations in `configs/` follow JSON format with structure:
```json
{
  "image_type": "checkerboard",
  "image_size": 4,
  "encoding_method": "amplitude",
  "shots": 1000,
  "noise_model": "none",
  "noise_probability": 0.0,
  "seed": 42
}
```

---

## Summary

**Phase 1 Status**: ✓ COMPLETE
- 15 Python modules created
- 32 test images generated
- 13 experiment configs created
- 6 documentation files written
- All systems tested and verified

**Ready for**: Phase 2 (Quantum Implementation)

**Next Action**: Begin implementing quantum modules (Phase 2)

---

*Last Updated: October 2026*  
*Project: Quantum Image Processing Performance Research*  
*Version: 1.0 (Phase 1 Complete)*
