# Quantum Image Processing - Complete Setup Guide

## 🚀 Quick Start (5 minutes)

### Step 1: Install Dependencies

```bash
# Navigate to project directory
cd c:\Users\ankit\Downloads\quantum

# Install Python dependencies
pip install qiskit qiskit-aer fastapi uvicorn python-multipart pillow opencv-python numpy matplotlib

# Or use requirements file (create if needed)
pip install -r requirements.txt
```

### Step 2: Start the Quantum Backend Server

```bash
# Terminal 1: Start the FastAPI server
python quantum_api_server.py

# Server will start on http://localhost:8000
# API docs available at http://localhost:8000/docs
```

### Step 3: Start the Frontend Dashboard

```bash
# Terminal 2: Start the dashboard server (keep existing server running)
python serve_dashboard.py

# Dashboard available at http://localhost:3000
```

### Step 4: Access the Application

Open browser and go to: **http://localhost:3000**

---

## 📋 Installation Details

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- 2GB+ RAM
- 500MB disk space

### Full Installation Steps

#### 1. Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv quantum_env

# Activate it
# On Windows:
quantum_env\Scripts\activate

# On macOS/Linux:
source quantum_env/bin/activate
```

#### 2. Install All Dependencies
```bash
pip install --upgrade pip

# Core quantum computing
pip install qiskit==0.43.0 qiskit-aer==0.12.0

# Web framework
pip install fastapi==0.104.0 uvicorn==0.24.0 python-multipart==0.0.6

# Image processing
pip install pillow==10.0.0 opencv-python==4.8.0 numpy==1.24.0

# Visualization
pip install matplotlib==3.7.0

# Optional: For better performance
pip install pydantic==2.4.0
```

#### 3. Verify Installation
```bash
# Test Qiskit
python -c "from qiskit import QuantumCircuit; print('✓ Qiskit installed')"

# Test FastAPI
python -c "import fastapi; print('✓ FastAPI installed')"

# Test image libraries
python -c "from PIL import Image; import cv2; print('✓ Image libraries installed')"
```

---

## 🎯 Running the Application

### Option A: Run Both Servers Automatically (Recommended)

Create `run_all.bat` (Windows) or `run_all.sh` (Linux/Mac):

**Windows (run_all.bat):**
```batch
@echo off
echo Starting Quantum Image Processing System...
echo.
echo [Terminal 1] Starting FastAPI Backend...
start cmd /k "python quantum_api_server.py"
echo [Terminal 2] Starting Frontend Dashboard...
timeout /t 3 /nobreak
start cmd /k "python serve_dashboard.py"
echo.
echo All servers started! Open browser to http://localhost:3000
```

**Linux/Mac (run_all.sh):**
```bash
#!/bin/bash
echo "Starting Quantum Image Processing System..."
echo ""
echo "[Terminal 1] Starting FastAPI Backend..."
python quantum_api_server.py &
echo "[Terminal 2] Starting Frontend Dashboard..."
sleep 2
python serve_dashboard.py &
echo ""
echo "All servers started! Open browser to http://localhost:3000"
```

### Option B: Manual Terminal Setup

**Terminal 1 - Backend:**
```bash
cd c:\Users\ankit\Downloads\quantum
python quantum_api_server.py
```

**Terminal 2 - Frontend:**
```bash
cd c:\Users\ankit\Downloads\quantum
python serve_dashboard.py
```

---

## 📊 API Endpoints Reference

### Health Check
```
GET http://localhost:8000/health
```

### Process with FRQI
```
POST http://localhost:8000/process/frqi
Content-Type: multipart/form-data

Parameters:
- file: Image file (PNG, JPG, etc.)
- image_size: 4, 8, or 16 (default: 8)
- shots: Measurement shots (default: 1000)
```

### Process with NEQR
```
POST http://localhost:8000/process/neqr
Content-Type: multipart/form-data

Parameters:
- file: Image file
- image_size: 4, 8, or 16 (default: 8)
- shots: Measurement shots (default: 1000)
- color_bits: 4-8 (default: 4)
```

### Compare Both Methods
```
POST http://localhost:8000/compare
Content-Type: multipart/form-data

Parameters:
- file: Image file
- image_size: 4, 8, or 16 (default: 8)
- shots: Measurement shots (default: 1000)
```

### Check Job Status
```
GET http://localhost:8000/job/{job_id}
```

### API Documentation (Interactive)
```
http://localhost:8000/docs
```

---

## 🔧 Configuration

### Backend Configuration (`quantum_api_server.py`)

Modify these defaults in the API handlers:

```python
# Default image size
image_size: int = 8  # Can be 4, 8, or 16

# Default measurement shots
shots: int = 1000  # More shots = more accurate but slower

# Color bits for NEQR
color_bits: int = 4  # 4 = 16 intensity levels, 8 = 256 levels
```

### Frontend Configuration (`serve_dashboard.py`)

No configuration needed - served from current directory.

---

## 🧪 Testing

### Test 1: Check Backend Health
```bash
# Terminal with backend running
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-...",
  "backend": "Qiskit Aer"
}
```

### Test 2: Process Sample Image via API
```bash
# Create a simple test image first, then:
curl -X POST -F "file=@test_image.png" \
  "http://localhost:8000/process/frqi?image_size=8&shots=1000"
```

### Test 3: Access Frontend
```
Open: http://localhost:3000
```

---

## 📈 Performance Optimization

### Reduce Processing Time

1. **Lower Image Size:**
   - 4×4: ~2-5 seconds
   - 8×8: ~5-10 seconds
   - 16×16: ~15-30 seconds

2. **Reduce Measurement Shots:**
   - 100 shots: Faster, less accurate
   - 500 shots: Balanced
   - 1000+ shots: Accurate, slower

3. **Use Fewer Color Bits (NEQR):**
   - 2-3 bits: Faster
   - 4 bits: Balanced
   - 8 bits: Slow but accurate

### System Requirements

**Minimum:**
- Python 3.8+
- 2GB RAM
- 500MB disk

**Recommended:**
- Python 3.10+
- 4GB+ RAM
- 2GB disk
- Multi-core processor

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'qiskit'"

**Solution:**
```bash
pip install qiskit qiskit-aer --upgrade
```

### Issue: "Port 8000 already in use"

**Solution:**
```bash
# Change port in quantum_api_server.py:
# uvicorn.run(app, host="0.0.0.0", port=8001)  # Use 8001 instead

# Or kill existing process:
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:8000 | xargs kill -9
```

### Issue: "Port 3000 already in use"

**Solution:**
```bash
# Change port in serve_dashboard.py:
# httpd.server_port = 3001  # Use 3001 instead

# Or kill existing process:
# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:3000 | xargs kill -9
```

### Issue: "CORS error" or "Cross-Origin Request Blocked"

**Solution:** Already configured in `quantum_api_server.py` with:
```python
CORSMiddleware with allow_origins=["*"]
```

### Issue: Images not uploading

**Solution:**
1. Check file size (< 10MB)
2. Use supported format (PNG, JPG)
3. Ensure backend is running on port 8000
4. Check browser console for errors (F12)

---

## 📚 Project Structure

```
quantum/
├── quantum_api_server.py          # FastAPI backend
├── backend_quantum_processor.py   # FRQI & NEQR implementations
├── serve_dashboard.py             # Frontend server
├── dashboard_frqi_animated.html   # Main dashboard UI
├── QUANTUM_IMAGE_CONVERSION_EXPLAINED.md  # Technical docs
├── QUANTUM_SETUP_GUIDE.md        # This file
└── data/
    ├── raw/                      # Sample images
    └── processed/                # Results
```

---

## 🎓 Understanding the Implementation

### FRQI Encoding
- **Formula:** θ = 2 × arccos(√pixel_value)
- **Qubits:** Position qubits + 1 color qubit
- **Advantage:** Fewer qubits
- **Limitation:** Probability-based intensity

### NEQR Encoding
- **Formula:** Binary computational basis states
- **Qubits:** Position qubits + color_bits
- **Advantage:** Exact color values, no loss
- **Limitation:** More qubits needed

### Key Metrics

1. **PSNR (Peak Signal-to-Noise Ratio)**
   - Formula: 10 × log₁₀(1/MSE)
   - Higher = Better quality
   - > 30 dB = Good quality

2. **SSIM (Structural Similarity)**
   - Range: -1 to 1
   - Closer to 1 = More similar
   - Better correlates with human perception

3. **MSE (Mean Squared Error)**
   - Lower = Better reconstruction
   - Average squared difference per pixel

---

## 🔬 Research Workflow

### For Your Viva/Evaluation:

1. **Demonstrate FRQI Processing**
   - Upload test image
   - Show quantum circuit
   - Display metrics
   - Explain encoding process

2. **Demonstrate NEQR Processing**
   - Same image
   - Compare circuits
   - Show different metrics
   - Explain basis encoding

3. **Show Comparison Analysis**
   - Side-by-side results
   - Metric comparison table
   - Circuit complexity analysis
   - Practical recommendations

4. **Explain Trade-offs**
   - FRQI: Efficient qubits vs. probability-based
   - NEQR: More qubits vs. exact values
   - Circuit complexity impact
   - Scalability considerations

---

## 📞 Support & Resources

### Qiskit Documentation
- https://qiskit.org/documentation/
- https://qiskit.org/textbook/

### FastAPI Documentation
- https://fastapi.tiangolo.com/

### Quantum Computing Concepts
- IBM Quantum Learning: https://quantum.ibm.com/
- Quantum Image Processing Papers: Search "FRQI NEQR quantum image"

---

## ✅ Verification Checklist

Before demonstration:

- [ ] Backend runs on http://localhost:8000
- [ ] Frontend runs on http://localhost:3000
- [ ] API docs available at http://localhost:8000/docs
- [ ] Sample image uploads successfully
- [ ] FRQI processing works and shows metrics
- [ ] NEQR processing works and shows metrics
- [ ] Comparison feature works
- [ ] Quantum circuits display correctly
- [ ] All metrics calculate properly
- [ ] Documentation is clear and accessible

---

## 🎉 You're Ready!

Your quantum image processing system is now fully operational with:
- ✅ Real quantum circuit simulation (Qiskit Aer)
- ✅ FRQI and NEQR encoding implementations
- ✅ Live performance metrics and visualization
- ✅ Interactive frontend dashboard
- ✅ RESTful API backend
- ✅ Research-grade comparison analysis

**Open http://localhost:3000 and start exploring quantum image processing!**
