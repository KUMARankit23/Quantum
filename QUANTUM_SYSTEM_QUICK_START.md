# ⚛️ Quantum Image Processing Research System - Quick Start

## Overview

This is a **research-grade quantum image processing system** that compares two quantum encoding methods:
- **FRQI** (Flexible Representation of Quantum Images)
- **NEQR** (Novel Enhanced Quantum Image Representation)

The system provides:
✅ **Real-time quantum simulation** using Qiskit Aer  
✅ **Interactive web dashboard** for image upload and processing  
✅ **Side-by-side comparison** of FRQI vs NEQR  
✅ **Real quantum circuits** with visualization  
✅ **Performance metrics** (PSNR, SSIM, MSE, Fidelity, etc.)  
✅ **Research-grade analysis** beyond qubit count

---

## Prerequisites

### System Requirements
- Python 3.8 or higher
- 4GB RAM minimum (for quantum simulation)
- Windows, macOS, or Linux

### Dependencies
All dependencies are listed in `requirements.txt`

---

## Installation (5 minutes)

### Step 1: Install Python Dependencies
```bash
pip install -r requirements.txt
```

If you encounter issues:
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

**Windows Note**: If installation fails with Visual C++ errors, install [Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

### Step 2: Verify Installation
```bash
python -c "import qiskit; import fastapi; print('✓ All dependencies installed')"
```

---

## Running the System

### Option 1: Automatic (Recommended)
```bash
python run_quantum_system.py
```

This will:
1. Start the FastAPI backend on port 8000
2. Start the HTML dashboard on port 3000
3. Automatically open the dashboard in your browser

### Option 2: Manual Start

**Terminal 1 - Start Backend API:**
```bash
python quantum_api_server.py
```
Expected output:
```
Quantum Image Processing API Server
Powered by Qiskit Aer Simulator
Starting server on http://localhost:8000
```

**Terminal 2 - Start Dashboard:**
```bash
python serve_dashboard.py
```

**Browser - Open Dashboard:**
```
http://localhost:3000
```

### Option 3: Verify Setup
If you just want to test the quantum processors:
```bash
python backend_quantum_processor.py
```

This will process a test 8×8 image and compare FRQI vs NEQR.

---

## Using the Dashboard

### Step 1: Upload Image
- Drag & drop any image file
- OR click the upload area to browse
- Supported formats: JPG, PNG, GIF, BMP

### Step 2: Configure Parameters
- **Image Size**: 4×4, 8×8, or 16×16 (default: 8×8)
- **Measurement Shots**: 100-2000 (default: 1000)
- **NEQR Color Bits**: 2-6 bits (default: 4)

### Step 3: Process Image
Choose one of three options:

**Option A: Process with FRQI only**
- Click "⚛️ Process with FRQI"
- See FRQI encoding, circuit, and metrics

**Option B: Process with NEQR only**
- Click "⚛️ Process with NEQR"
- See NEQR encoding, circuit, and metrics

**Option C: Compare both methods** *(Recommended)*
- Click "🔄 Compare FRQI vs NEQR"
- See side-by-side comparison
- View detailed analysis and research insights

### Step 4: Interpret Results

**Original vs Reconstructed Images**
- Shows quantum encoding/decoding quality
- Large display (300px+ images)

**Quantum Circuit Diagrams**
- Visual representation of the quantum circuit
- Shows qubits, gates, and measurements

**Performance Metrics**
- **PSNR** (Peak Signal-to-Noise Ratio): Higher is better (typical: 20-40 dB)
- **SSIM** (Structural Similarity): Higher is better (range: -1 to 1)
- **MSE** (Mean Squared Error): Lower is better
- **Fidelity**: State fidelity (0-1)

**Circuit Complexity**
- **Qubits**: Number of quantum bits used
- **Depth**: Circuit layers (affects noise)
- **Gates**: Total gate operations

**Execution Time**
- Time to run quantum simulation

**Comparison Analysis**
- Which method uses fewer qubits?
- Which produces better image quality?
- Which has simpler circuits?
- Which is faster?

---

## Understanding FRQI vs NEQR

### FRQI (Flexible Representation of Quantum Images)
**Encoding Method**: Amplitude-based rotation  
**Formula**: θ = 2 × arccos(√pixel_value)

**Advantages**:
- Uses fewer qubits (more efficient)
- Faster circuit execution
- Good for qubit-limited devices

**Disadvantages**:
- Lower precision per qubit
- Sensitive to measurement outcomes

### NEQR (Novel Enhanced Quantum Image Representation)
**Encoding Method**: Binary computational basis states  
**Formula**: |color⟩ = |b₁b₂...bₙ⟩ (binary states)

**Advantages**:
- Better color/intensity fidelity
- More precise representation
- Clearer intensity levels

**Disadvantages**:
- Uses more qubits
- More complex circuits
- Slower execution

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│          Web Browser (Port 3000)                    │
│  dashboard_research.html - Interactive Dashboard    │
└────────────────┬────────────────────────────────────┘
                 │ REST API (JSON)
                 ▼
┌─────────────────────────────────────────────────────┐
│     FastAPI Backend (Port 8000)                     │
│  quantum_api_server.py                              │
│  - /process/frqi                                    │
│  - /process/neqr                                    │
│  - /compare                                         │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│    Quantum Processing Engine                        │
│  backend_quantum_processor.py                       │
│  ├─ FRQIEncoder (Amplitude encoding)                │
│  └─ NEQREncoder (Basis state encoding)              │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│     Qiskit Aer Simulator                            │
│  - Builds quantum circuits                          │
│  - Executes simulations (1000 shots default)        │
│  - Measures quantum states                          │
│  - Reconstructs images                              │
└─────────────────────────────────────────────────────┘
```

---

## API Endpoints

If you want to use the API directly (e.g., with cURL or Python):

### Health Check
```bash
curl http://localhost:8000/health
```

### Process with FRQI
```bash
curl -X POST -F "file=@image.jpg" -F "image_size=8" -F "shots=1000" \
  http://localhost:8000/process/frqi
```

### Process with NEQR
```bash
curl -X POST -F "file=@image.jpg" -F "image_size=8" -F "shots=1000" \
  http://localhost:8000/process/neqr
```

### Compare Both Methods
```bash
curl -X POST -F "file=@image.jpg" -F "image_size=8" -F "shots=1000" \
  http://localhost:8000/compare
```

**Response includes**:
- Original and reconstructed images (base64)
- Quantum circuit diagrams (base64)
- Metrics for both methods
- Comparison analysis

---

## Troubleshooting

### Issue: "Port 8000 already in use"
**Solution**: Kill the process on port 8000
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:8000 | xargs kill -9
```

### Issue: "Port 3000 already in use"
**Solution**: Kill the process on port 3000
```bash
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:3000 | xargs kill -9
```

### Issue: "Module not found" errors
**Solution**: Install missing dependencies
```bash
pip install --upgrade -r requirements.txt
```

### Issue: "Cannot connect to localhost:8000"
**Solution**: Check if API server is running
- Look at Terminal 1 for error messages
- Verify port 8000 is available
- Check firewall settings

### Issue: Quantum simulation is slow
**Reason**: This is expected! Quantum simulation is computationally intensive.
- First run takes longer (Qiskit initialization)
- Larger images = longer computation
- More shots = longer computation
- More qubits = exponentially longer

**Optimization**:
- Start with 4×4 images
- Use 500 shots instead of 1000
- Larger images use 16×16 instead of processing many 8×8

---

## Example Usage Scenarios

### Scenario 1: Quick Comparison
1. Upload a small JPG
2. Keep default settings (8×8, 1000 shots)
3. Click "Compare FRQI vs NEQR"
4. Wait ~10-30 seconds
5. See side-by-side results

### Scenario 2: Educational Demo
1. Upload a simple image (checkerboard, gradient)
2. Process with FRQI
3. See quantum circuit
4. Process with NEQR
5. Compare results
6. Explain to audience

### Scenario 3: Research Experiment
1. Upload multiple different images
2. Use 16×16 size for more qubits
3. Try different shot counts
4. Collect metrics for paper
5. Compare trends across images

---

## Learning Resources

### Quantum Concepts
- **Amplitude Encoding**: Encodes data in qubit amplitudes
- **Basis State Encoding**: Uses computational basis |0⟩, |1⟩ states
- **Quantum Circuit**: Sequence of quantum gates
- **Measurement**: Collapses quantum state to classical outcome
- **Fidelity**: How well quantum state matches target state

### FRQI Deep Dive
- Position qubits: Encode pixel location
- Color qubit: Encode intensity via amplitude
- Controlled rotations: RY(θ) gates
- θ = 2×arccos(√pixel) formula

### NEQR Deep Dive
- Position qubits: Encode pixel location
- Color qubits: Binary representation of intensity
- X gates: Set basis states
- Better precision with more color qubits

---

## Performance Benchmarks

Typical execution times on modern PC:

| Image Size | Method | Shots | Time |
|-----------|--------|-------|------|
| 4×4 (16 pixels) | FRQI | 1000 | ~1-2 sec |
| 4×4 | NEQR | 1000 | ~2-3 sec |
| 8×8 (64 pixels) | FRQI | 1000 | ~5-10 sec |
| 8×8 | NEQR | 1000 | ~8-15 sec |
| 16×16 (256 pixels) | FRQI | 1000 | ~20-30 sec |
| 16×16 | NEQR | 1000 | ~30-45 sec |

*Times vary by hardware. First run slower due to Qiskit initialization.*

---

## For University Evaluation/Viva

### Key Points to Explain

1. **What does your system do?**
   - Compare quantum image encoding methods
   - Use real quantum simulation (Qiskit Aer)
   - Measure practical performance factors

2. **Why FRQI vs NEQR?**
   - Different encoding approaches
   - Different qubit requirements
   - Different circuit complexity
   - Different reconstruction quality

3. **How does FRQI work?**
   - Position qubits for pixel location
   - RY rotations encode intensity
   - Formula: θ = 2×arccos(√pixel)

4. **How does NEQR work?**
   - Position qubits for pixel location
   - Color qubits as binary representation
   - X gates set basis states
   - More precise intensity encoding

5. **Why real quantum simulation?**
   - Reproducible experiments
   - Fair comparison framework
   - Honest about limitations
   - No claiming quantum advantage

6. **What metrics do you measure?**
   - Image quality: PSNR, SSIM, MSE
   - Circuit metrics: Depth, gates, qubits
   - Performance: Execution time, fidelity

7. **What are your findings?**
   - FRQI uses fewer qubits (more efficient)
   - NEQR produces better image quality
   - NEQR has more complex circuits
   - Trade-off between efficiency and quality

### Demo Script (5 minutes)

1. **Start the system** (30 seconds)
   ```bash
   python run_quantum_system.py
   ```

2. **Upload a simple image** (30 seconds)
   - Use a small checkerboard or gradient
   - Keep 8×8 size

3. **Process with FRQI** (15 seconds)
   - Click button
   - Wait for completion
   - Show circuit and metrics

4. **Process with NEQR** (15 seconds)
   - Click button
   - Show circuit and metrics

5. **Compare side-by-side** (30 seconds)
   - Click compare button
   - Show original vs reconstructed
   - Point out qubit difference
   - Explain metric differences

6. **Discuss findings** (2 minutes)
   - FRQI efficiency vs NEQR quality
   - Circuit complexity trade-off
   - Practical considerations
   - Research implications

---

## File Structure

```
quantum/
├── dashboard_research.html          # Main interactive dashboard
├── run_quantum_system.py             # System launcher (start here!)
├── quantum_api_server.py             # FastAPI backend
├── backend_quantum_processor.py       # FRQI/NEQR implementations
├── serve_dashboard.py                # Legacy dashboard server
├── requirements.txt                  # Python dependencies
├── QUANTUM_SYSTEM_QUICK_START.md    # This file
├── QUANTUM_SETUP_GUIDE.md           # Detailed setup guide
└── data/
    └── raw/                         # Test images
```

---

## Next Steps

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Start system**: `python run_quantum_system.py`
3. **Open browser**: Navigate to `http://localhost:3000`
4. **Upload image**: Drag & drop any image
5. **Compare methods**: Click "Compare FRQI vs NEQR"
6. **Interpret results**: Read metrics and analysis

---

## Support & Issues

### Check Logs
- **API Server**: Look at Terminal 1 for errors
- **Dashboard**: Look at Browser Console (F12)
- **Backend**: Run `python backend_quantum_processor.py` directly

### Test Components
```bash
# Test quantum processor
python backend_quantum_processor.py

# Test API server alone
python quantum_api_server.py

# Test both together
python run_quantum_system.py
```

### Verify Setup
```bash
# Check Python version
python --version  # Must be 3.8+

# Check dependencies
python -c "import qiskit; import fastapi; import qiskit_aer; print('OK')"

# Check ports
netstat -ano | findstr :8000  # Should be empty
netstat -ano | findstr :3000  # Should be empty
```

---

## Research References

### FRQI Original Papers
- Le et al. (2011): "A Flexible Representation of Quantum Images"
- Flexible amplitude-based encoding
- Position superposition with color rotation

### NEQR Original Papers
- Zhang et al. (2013): "Novel Enhanced Quantum Image Representation"
- Binary computational basis encoding
- Multiple color qubits for precision

### Comparison Papers
- Recent work on quantum image encoding comparison
- Focus on practical constraints
- Analysis beyond theoretical qubit count

---

## License & Citation

This is a research project for educational purposes.

**Citation**:
```
Quantum Image Processing Research System
FRQI vs NEQR Comparison Dashboard
Quantum Computing Lab - [Your University]
```

---

**Last Updated**: October 29, 2026  
**Status**: ✅ Production Ready  
**Tested On**: Python 3.8+, Windows/macOS/Linux  

---

Happy quantum computing research! 🚀⚛️
