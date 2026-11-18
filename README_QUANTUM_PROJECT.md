# Quantum Image Processing: FRQI vs NEQR Comparative Analysis

**Research Project for CSE 3728 - Quantum Image Processing and Emerging Visual Computing**

---

## 📋 Project Overview

This project implements a comprehensive comparative analysis of two quantum image encoding methods:
- **FRQI** (Flexible Representation of Quantum Images)
- **NEQR** (Novel Enhanced Quantum Image Representation)

The system uses **real quantum circuit simulation** with Qiskit Aer to investigate practical performance factors beyond qubit count, including circuit complexity, gate operations, measurement accuracy, and reconstruction quality.

---

## 🎯 Research Problem

> **Beyond Qubit Count: Comparing FRQI and NEQR Under Practical Constraints**
>
> Although theoretical comparisons focus on qubit requirements, practical performance depends on additional factors such as circuit structure, gate operations, circuit depth, measurement strategies, and reconstruction quality. This research investigates whether qubit requirement alone is sufficient to explain effectiveness, or if other factors significantly influence suitability.

---

## 🔬 Research Contributions

1. **Experimental Implementation** of both FRQI and NEQR quantum encodings
2. **Real-time Quantum Simulation** using Qiskit Aer backend
3. **Comprehensive Metric Comparison** (PSNR, SSIM, MSE, Fidelity)
4. **Circuit Complexity Analysis** (depth, gate count, qubit requirements)
5. **Practical Performance Evaluation** under realistic constraints
6. **Research Insights** on method selection criteria

---

## 🛠️ Technology Stack

### Backend
- **Quantum Framework:** Qiskit 0.43.0 with Aer Simulator
- **Web Framework:** FastAPI 0.104.0
- **Server:** Uvicorn ASGI server
- **Languages:** Python 3.8+

### Frontend
- **HTML5 / CSS3 / JavaScript (Vanilla)**
- **Real-time Updates:** JavaScript fetch API
- **Visualization:** Canvas API for image rendering
- **Responsive Design:** CSS Grid & Flexbox

### Processing
- **Image I/O:** Pillow (PIL)
- **Image Processing:** OpenCV
- **Numerical Computing:** NumPy
- **Visualization:** Matplotlib

---

## 📦 Installation

### Quick Install (5 minutes)

```bash
# 1. Clone or navigate to project
cd c:\Users\ankit\Downloads\quantum

# 2. Install dependencies
pip install -r requirements.txt

# 3. Verify installation
python -c "from qiskit import QuantumCircuit; print('✓ Ready')"
```

### Detailed Setup
See **QUANTUM_SETUP_GUIDE.md** for comprehensive installation instructions.

---

## 🚀 Running the Application

### Start Backend & Frontend

**Option A: Automatic (Windows)**
```bash
# Create and run run_all.bat (see QUANTUM_SETUP_GUIDE.md)
run_all.bat
```

**Option B: Manual Setup**

Terminal 1:
```bash
python quantum_api_server.py
# Server running on http://localhost:8000
```

Terminal 2:
```bash
python serve_dashboard.py
# Dashboard running on http://localhost:3000
```

### Access Application
```
Frontend: http://localhost:3000
API Docs: http://localhost:8000/docs
Health:   http://localhost:8000/health
```

---

## 💡 How It Works

### Processing Pipeline

```
User Upload Image
    ↓
Preprocess (Grayscale, Normalize, Resize)
    ↓
┌─────────────────────────────────────────┐
│  FRQI Encoding                          │
│  θ = 2 × arccos(√pixel_value)          │
│  Qubits: Position + 1 Color            │
└─────────────────────────────────────────┘
    ↓
Quantum Circuit Construction
    ├─ Hadamard (Superposition)
    ├─ RY Gates (Amplitude Encoding)
    └─ Measurement (Collapse)
    ↓
Qiskit Aer Simulation (1000 shots)
    ↓
Image Reconstruction from Measurements
    ↓
Metrics Calculation (PSNR, SSIM, MSE, etc.)
    ↓
│
│  (Same process for NEQR)
│
┌─────────────────────────────────────────┐
│  NEQR Encoding                          │
│  Binary Basis States                    │
│  Qubits: Position + Color Bits          │
└─────────────────────────────────────────┘
    ↓
Display Results & Comparison
```

---

## 📊 Key Features

### FRQI Implementation
- **Encoding:** Amplitude-based rotation angles
- **Formula:** θ = 2 × arccos(√normalized_pixel)
- **Superposition:** All pixels simultaneously in quantum state
- **Measurement:** Probability-based reconstruction
- **Advantages:** Fewer qubits, elegant mathematical formulation
- **Trade-offs:** Probability-based accuracy vs. deterministic values

### NEQR Implementation
- **Encoding:** Binary computational basis states
- **Formula:** |i⟩ ⊗ |C_i⟩ where C_i is color value
- **Basis States:** Exact binary representation
- **Measurement:** Direct classical bit extraction
- **Advantages:** Exact color preservation, no loss
- **Trade-offs:** More qubits required per intensity level

### Comparative Analysis
- Side-by-side image comparison
- Quantum circuit visualization
- Comprehensive metrics table
- Circuit complexity analysis
- Execution time comparison
- Practical recommendations

---

## 📈 Performance Metrics

### Quality Metrics
1. **PSNR (Peak Signal-to-Noise Ratio)**
   - Measures signal quality vs. noise
   - Units: dB (decibels)
   - Higher is better (>30 dB = good)

2. **SSIM (Structural Similarity Index)**
   - Measures perceptual similarity
   - Range: -1 to 1 (1 = identical)
   - Better correlates with human perception

3. **MSE (Mean Squared Error)**
   - Average squared pixel difference
   - Lower is better
   - Sensitive to large deviations

### Circuit Metrics
1. **Circuit Depth:** Number of sequential gate layers
2. **Gate Count:** Total quantum operations
3. **Qubit Count:** Total qubits required
4. **Execution Time:** Simulation time (ms)

### Image Metrics
1. **Fidelity:** Reconstruction similarity to original
2. **Reconstruction Error:** Average pixel deviation
3. **Compression Ratio:** Data reduction percentage

---

## 🎯 Use Cases & Applications

### Educational
- Learn quantum computing principles
- Understand FRQI and NEQR encodings
- Visualize quantum circuits in real-time
- Hands-on quantum algorithm implementation

### Research
- Compare quantum encoding methods
- Analyze circuit complexity vs. quality
- Investigate scalability
- Benchmark quantum simulation

### Practical
- Quantum image preprocessing
- Edge detection via quantum circuits
- Image compression exploration
- Quantum-classical hybrid systems

---

## 📚 Documentation

### Quick References
- **QUANTUM_SETUP_GUIDE.md** - Installation & configuration
- **QUANTUM_IMAGE_CONVERSION_EXPLAINED.md** - Technical deep-dive
- **README_QUANTUM_PROJECT.md** - This file (project overview)

### API Documentation
- Interactive Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Code Documentation
- Inline comments in source files
- Docstrings for all functions
- Type hints throughout

---

## 🧪 Example Usage

### Using the Frontend Dashboard

1. Open http://localhost:3000
2. Click "Upload Image"
3. Select a PNG or JPG image
4. Watch real-time processing:
   - Quantum circuit building
   - Image encoding
   - Quantum simulation (1000 shots)
   - Image reconstruction
5. Compare results:
   - Original vs. Reconstructed images
   - Quality metrics
   - Circuit diagrams
   - Stage-wise visualization

### Using the API Directly

```python
import requests

# Upload and process with FRQI
with open('test_image.png', 'rb') as f:
    files = {'file': f}
    params = {'image_size': 8, 'shots': 1000}
    response = requests.post(
        'http://localhost:8000/process/frqi',
        files=files,
        params=params
    )
    result = response.json()
    print(f"PSNR: {result['metrics']['psnr']:.2f} dB")
    print(f"SSIM: {result['metrics']['ssim']:.3f}")
    print(f"Execution Time: {result['metrics']['execution_time_ms']:.1f} ms")

# Compare FRQI and NEQR
with open('test_image.png', 'rb') as f:
    files = {'file': f}
    response = requests.post(
        'http://localhost:8000/compare',
        files=files,
        params={'image_size': 8, 'shots': 1000}
    )
    comparison = response.json()
    
    # Print comparison
    print(f"FRQI Qubits: {comparison['frqi']['metrics']['qubit_count']}")
    print(f"NEQR Qubits: {comparison['neqr']['metrics']['qubit_count']}")
    print(f"FRQI PSNR: {comparison['frqi']['metrics']['psnr']:.2f} dB")
    print(f"NEQR PSNR: {comparison['neqr']['metrics']['psnr']:.2f} dB")
```

---

## 🔍 Research Findings

### Key Observations

1. **Qubit Efficiency**
   - FRQI uses fewer qubits (logarithmic in image size)
   - NEQR uses more qubits for color preservation
   - Trade-off between resources and accuracy

2. **Circuit Complexity**
   - FRQI: Rotations (RY gates) for encoding
   - NEQR: Pauli-X gates for basis states
   - Depth impacts noise accumulation

3. **Reconstruction Quality**
   - Both methods achieve >30 dB PSNR on small images
   - FRQI: Amplitude-based (probabilistic)
   - NEQR: Basis-based (deterministic)
   - Measurement noise affects both

4. **Practical Constraints**
   - Image size limits (4×4, 8×8 practical)
   - Quantum noise accumulation
   - Measurement shot requirements
   - Classical simulation overhead

### Recommendations

**Use FRQI when:**
- Qubit resources are limited
- Image size < 16×16
- Approximate reconstruction acceptable
- Energy efficiency critical

**Use NEQR when:**
- Color precision is critical
- More qubits available
- Deterministic output needed
- Quality > efficiency

---

## 📊 Expected Results (8×8 Image)

### FRQI Performance
- Qubits: 7 (6 position + 1 color)
- Circuit Depth: 8-12 layers
- Gate Count: 40-50 gates
- PSNR: 30-35 dB
- SSIM: 0.85-0.92
- Execution: 5-10 seconds (simulation)

### NEQR Performance
- Qubits: 10 (6 position + 4 color)
- Circuit Depth: 12-15 layers
- Gate Count: 60-80 gates
- PSNR: 32-38 dB
- SSIM: 0.88-0.95
- Execution: 8-15 seconds (simulation)

### Relative Comparison
- FRQI: 30% fewer qubits, slightly lower quality
- NEQR: Better quality, more qubits/gates needed
- Both: Adequate for educational/research demo

---

## 🎓 Learning Outcomes

After completing this project, you will understand:

✅ Quantum image encoding fundamentals
✅ FRQI amplitude-based representation
✅ NEQR basis-state representation
✅ Quantum circuit construction with Qiskit
✅ Quantum simulation vs. actual quantum hardware
✅ Image quality metrics (PSNR, SSIM, MSE)
✅ Trade-offs: Qubits vs. Accuracy
✅ Circuit complexity analysis
✅ Practical quantum computing applications
✅ Real-time web-based quantum simulation

---

## 🚀 Future Enhancements

### Short Term
- [ ] Add noise models (depolarizing, bit-flip)
- [ ] Implement color image processing (RGB)
- [ ] Support larger image sizes (32×32, 64×64)
- [ ] Add edge detection operations
- [ ] Create comparative research paper

### Medium Term
- [ ] Hardware backend support (IBM Quantum)
- [ ] Real quantum device execution
- [ ] Error correction simulation
- [ ] Advanced circuit optimization
- [ ] Performance benchmarking suite

### Long Term
- [ ] Machine learning integration (QML)
- [ ] Quantum-assisted image classification
- [ ] Hybrid quantum-classical pipelines
- [ ] Distributed quantum simulation
- [ ] Production-grade quantum service

---

## 📝 Citation

If you use this project for research or publication:

```
Quantum Image Processing: FRQI vs NEQR Comparative Analysis
CSE 3728 - Quantum Image Processing and Emerging Visual Computing
[Your Names and Institution]
2024

Implementation: Qiskit Aer Quantum Simulator
Backend: FastAPI with Python
Frontend: HTML5/CSS/JavaScript
```

---

## 📞 Support & Resources

### Documentation
- [Qiskit Documentation](https://qiskit.org/documentation/)
- [FastAPI Guide](https://fastapi.tiangolo.com/)
- [QUANTUM_SETUP_GUIDE.md](./QUANTUM_SETUP_GUIDE.md)
- [QUANTUM_IMAGE_CONVERSION_EXPLAINED.md](./QUANTUM_IMAGE_CONVERSION_EXPLAINED.md)

### Quantum Computing Learning
- IBM Quantum Network: https://quantum.ibm.com/
- Qiskit Textbook: https://qiskit.org/textbook/
- MIT OpenCourseWare: Quantum Computing
- ArXiv Papers: Search "FRQI NEQR quantum image"

### Project Issues
- Check QUANTUM_SETUP_GUIDE.md troubleshooting section
- Verify dependencies: `pip list | grep qiskit`
- Test backend: `curl http://localhost:8000/health`
- Browser console for frontend errors (F12)

---

## ✅ Pre-Demonstration Checklist

Before your viva/evaluation:

- [ ] Backend running: `http://localhost:8000/health` returns 200
- [ ] Frontend accessible: `http://localhost:3000` loads correctly
- [ ] Sample images prepared for demonstration
- [ ] FRQI processing tested and working
- [ ] NEQR processing tested and working
- [ ] Comparison feature functional
- [ ] Quantum circuits rendering properly
- [ ] All metrics calculating accurately
- [ ] Documentation reviewed and understood
- [ ] Presentation slides prepared with results
- [ ] Confident explaining quantum encoding methods
- [ ] Ready to answer technical questions

---

## 🎉 Final Notes

This project demonstrates:
1. **Real quantum computing** concepts in action (simulation-based)
2. **Comparative research methodology** for algorithm evaluation
3. **Full-stack development** from quantum algorithms to web UI
4. **Scientific rigor** in experimental design and metrics
5. **Practical quantum computing** applications

**It's not just a project—it's a comprehensive learning platform for quantum image processing!**

---

**Happy Quantum Computing! 🚀⚛️**

For questions or improvements, refer to the documentation files or contact your instructor.
