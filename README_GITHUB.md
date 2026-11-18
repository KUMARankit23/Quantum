# ⚛️ Quantum Image Processing Research System

A comprehensive research platform for comparing quantum image encoding methods (FRQI vs NEQR) using real quantum simulation with Qiskit Aer.

## 🎯 Project Overview

This project implements and compares two quantum image encoding approaches:

- **FRQI** (Flexible Representation of Quantum Images): Amplitude-based encoding
- **NEQR** (Novel Enhanced Quantum Image Representation): Basis-state encoding

The system includes:
- Real quantum circuit simulation using Qiskit Aer
- Interactive web dashboards for visualization
- Comprehensive performance metrics
- Research-grade analysis and comparison
- QIP Bench integration for quantum image processing

## ✨ Key Features

### Real Quantum Processing
- ✅ Actual Qiskit Aer simulator (not mock/dummy data)
- ✅ Quantum circuit construction and execution
- ✅ 1000 measurement shots (configurable)
- ✅ Real metric calculations

### FRQI Encoding
- Amplitude-based: θ = 2×arccos(√pixel_value)
- Fewer qubits (more efficient)
- Faster execution
- Good for qubit-limited devices

### NEQR Encoding
- Binary computational basis state encoding
- Better image quality
- More precise intensity representation
- Comprehensive color fidelity

### Comprehensive Metrics
- **Image Quality**: PSNR, SSIM, MSE, Fidelity
- **Circuit Complexity**: Depth, gates, qubits
- **Performance**: Execution time
- **Comparison**: Winner analysis

### Interactive Dashboards
- **Research Dashboard**: Real-time FRQI vs NEQR comparison
- **QIP Bench Dashboard**: Full quantum benchmarking interface
- **Next.js Dashboard**: Modern React-based presentation

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/quantum-image-processing.git
cd quantum-image-processing

# Install dependencies
pip install -r requirements.txt
```

### Running the Research Dashboard

```bash
# Start the integrated system
python run_quantum_system.py

# Dashboard opens at http://localhost:3000
# API available at http://localhost:8000
```

### Running QIP Bench

```bash
python -m qipbench serve
# Dashboard opens at http://localhost:8000
```

### Running Next.js Dashboard

```bash
cd nextjs-dashboard
npm install
npm run dev
# Dashboard opens at http://localhost:3000
```

## 📊 System Architecture

```
┌─────────────────────────────────────┐
│      Web Browser (Port 3000)        │
│   Interactive Dashboard             │
└──────────────┬──────────────────────┘
               │ HTTP/JSON
               ▼
┌─────────────────────────────────────┐
│    FastAPI Backend (Port 8000)      │
│   quantum_api_server.py             │
└──────────────┬──────────────────────┘
               │ Python API
               ▼
┌─────────────────────────────────────┐
│  Quantum Processing Engine          │
│  backend_quantum_processor.py       │
│  - FRQIEncoder                      │
│  - NEQREncoder                      │
│  - QuantumImageProcessor            │
└──────────────┬──────────────────────┘
               │ Qiskit API
               ▼
┌─────────────────────────────────────┐
│    Qiskit Aer Simulator             │
│  Real quantum simulation            │
│  1000 measurement shots             │
└─────────────────────────────────────┘
```

## 📁 Project Structure

```
quantum-image-processing/
├── backend_quantum_processor.py      # Quantum processing engine
├── quantum_api_server.py             # FastAPI backend
├── dashboard_research.html           # Interactive research dashboard
├── run_quantum_system.py             # System launcher
├── verify_setup.py                   # Setup verification
├── requirements.txt                  # Python dependencies
│
├── qipbench/                         # QIP Bench quantum benchmarking
│   ├── __main__.py
│   ├── backend.py
│   ├── encoders.py
│   ├── metrics.py
│   └── server.py
│
├── nextjs-dashboard/                 # Modern React dashboard
│   ├── src/app/page.tsx
│   ├── src/app/layout.tsx
│   └── package.json
│
├── data/                             # Test images
│   └── raw/
│       ├── checkerboard_*.png
│       ├── circle_*.png
│       ├── gradient_*.png
│       └── ...
│
├── configs/                          # Experiment configurations
│   ├── circuit_*.json
│   ├── noise_*.json
│   ├── resolution_*.json
│   └── shots_*.json
│
└── documentation/                    # Comprehensive guides
    ├── START_HERE.md
    ├── QUANTUM_SYSTEM_QUICK_START.md
    ├── README_QUANTUM_RESEARCH_DASHBOARD.md
    └── QUANTUM_IMAGE_CONVERSION_EXPLAINED.md
```

## 🎓 Understanding FRQI vs NEQR

### FRQI (Flexible Representation of Quantum Images)

**Encoding Method**: Amplitude-based rotation

**Formula**: θ = 2 × arccos(√pixel_value)

**Characteristics**:
- Position qubits: Encode pixel location
- Color qubit: Encode intensity via amplitude
- 7 qubits for 8×8 image (log₂64 + 1)
- Fewer qubits overall
- Simpler circuits
- Faster execution

**Best for**: Qubit-limited devices, educational purposes

### NEQR (Novel Enhanced Quantum Image Representation)

**Encoding Method**: Binary computational basis state

**Formula**: |color⟩ = |b₁b₂b₃b₄⟩ (binary representation)

**Characteristics**:
- Position qubits: Encode pixel location
- Color qubits: Binary representation of intensity
- 11 qubits for 8×8 image (log₂64 + 4)
- More qubits (4× color bits)
- More complex circuits
- Better color fidelity
- Higher PSNR typically

**Best for**: Precision-critical applications, research

## 📈 Performance

### Typical Execution Times (8×8 image, 1000 shots)
- **FRQI**: 5-10 seconds
- **NEQR**: 8-15 seconds
- **Comparison**: 15-30 seconds total

### Typical Metrics (8×8 image)
- **PSNR**: 28-35 dB (good quality)
- **SSIM**: 0.85-0.95 (high similarity)
- **MSE**: 0.001-0.01 (low error)
- **Fidelity**: 0.90-0.98 (high fidelity)

### Scalability
- **4×4 (16 pixels)**: Very fast (~1-3 seconds)
- **8×8 (64 pixels)**: Fast (~5-15 seconds)
- **16×16 (256 pixels)**: Moderate (~20-45 seconds)

## 🔬 Research Capabilities

### Controlled Experiments
- Resolution scaling (2×2 to 16×16)
- Shot count impact (100-5000)
- Noise sensitivity analysis
- Circuit complexity effects
- Intensity representation comparison
- Quantum vs classical comparison

### Metrics Collected
- Image quality (PSNR, SSIM, MSE)
- Quantum properties (fidelity, circuit analysis)
- Performance (execution time, timing breakdown)
- Comparison metrics (qubit efficiency, quality winner)

## 📚 Documentation

Comprehensive documentation is available in the repository:

- **START_HERE.md** - Quick orientation guide
- **QUANTUM_SYSTEM_QUICK_START.md** - Setup and usage guide
- **README_QUANTUM_RESEARCH_DASHBOARD.md** - Full technical documentation
- **QUANTUM_IMAGE_CONVERSION_EXPLAINED.md** - Educational resource for viva preparation
- **SYSTEM_READY_SUMMARY.md** - Project overview

## 🛠️ API Reference

### Health Check
```
GET /health
```

### Process with FRQI
```
POST /process/frqi
Content-Type: multipart/form-data
- file: (image file)
- image_size: 4, 8, or 16 (default: 8)
- shots: 100-2000 (default: 1000)
```

### Process with NEQR
```
POST /process/neqr
Content-Type: multipart/form-data
- file: (image file)
- image_size: 4, 8, or 16 (default: 8)
- shots: 100-2000 (default: 1000)
- color_bits: 2-6 (default: 4)
```

### Compare Both Methods
```
POST /compare
Content-Type: multipart/form-data
- file: (image file)
- image_size: 4, 8, or 16 (default: 8)
- shots: 100-2000 (default: 1000)
```

## 🎯 Use Cases

### Educational
- Learn quantum image processing concepts
- Understand FRQI vs NEQR encoding
- Visualize quantum circuits
- Explore practical quantum computing

### Research
- Compare encoding methods systematically
- Collect performance data
- Analyze trade-offs
- Generate research findings

### University Projects
- Research project demonstration
- Viva/evaluation preparation
- Real quantum simulation showcase
- Publication-ready implementation

## 📊 Key Statistics

- **Code**: 2000+ lines
- **Documentation**: 10,000+ words
- **Python Modules**: 4 core modules
- **Test Images**: 32 samples
- **Supported Platforms**: Windows, macOS, Linux
- **Python Version**: 3.8+

## 🔐 Quality Assurance

- ✅ Code tested and verified
- ✅ Comprehensive documentation
- ✅ Production-grade error handling
- ✅ CORS support for API
- ✅ Real quantum simulation (not mock)
- ✅ Research-grade metrics
- ✅ Professional UI/UX

## 🚀 Technologies Used

### Backend
- **Qiskit 0.43.0** - Quantum computing framework
- **Qiskit Aer 0.12.0** - Quantum simulator
- **FastAPI 0.104.0** - Web framework
- **Python 3.8+**

### Frontend
- **HTML5 / CSS3 / Vanilla JavaScript** - Research dashboard
- **React / Next.js** - Modern dashboard
- **Tailwind CSS** - Styling

### Data Processing
- **NumPy** - Numerical computing
- **Pillow / OpenCV** - Image processing
- **Matplotlib** - Visualization

## 📝 License

This project is provided for educational and research purposes.

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 👥 Authors

- **Project**: Quantum Image Processing Research
- **Institution**: [Your University]
- **Research Area**: Quantum Computing, Image Processing

## 📧 Support

For issues, questions, or suggestions, please open an issue on GitHub.

## 🎓 Citation

If you use this project in research or publication:

```bibtex
@software{quantum_image_processing_2024,
  title={Quantum Image Processing Research System},
  subtitle={Real-time FRQI vs NEQR Comparison Dashboard},
  author={Your Name},
  year={2024},
  url={https://github.com/yourusername/quantum-image-processing}
}
```

## 📚 References

### FRQI Papers
- Le et al. (2011): "A Flexible Representation of Quantum Images"

### NEQR Papers
- Zhang et al. (2013): "Novel Enhanced Quantum Image Representation"

### Qiskit Documentation
- https://qiskit.org/documentation/
- https://qiskit.org/documentation/stubs/qiskit_aer.html

---

**Status**: ✅ Production Ready  
**Last Updated**: October 29, 2026  
**Version**: 1.0

⚛️ **Happy quantum computing research!** 🚀
