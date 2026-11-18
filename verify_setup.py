#!/usr/bin/env python3
"""
Quantum System Setup Verification Script
Checks all dependencies and components before running
"""

import sys
import subprocess
from pathlib import Path

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def check_python_version():
    """Check Python version"""
    print_header("1️⃣  Python Version Check")
    version = sys.version_info
    print(f"Current: Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 8:
        print("✅ Python version OK (3.8+)")
        return True
    else:
        print("❌ Python 3.8 or higher required")
        return False

def check_dependencies():
    """Check all required dependencies"""
    print_header("2️⃣  Dependencies Check")
    
    required = {
        'qiskit': 'Qiskit (quantum framework)',
        'qiskit_aer': 'Qiskit Aer (simulator)',
        'fastapi': 'FastAPI (web framework)',
        'uvicorn': 'Uvicorn (ASGI server)',
        'PIL': 'Pillow (image processing)',
        'cv2': 'OpenCV (image processing)',
        'numpy': 'NumPy (numerical)',
        'matplotlib': 'Matplotlib (plotting)',
    }
    
    all_ok = True
    for module, name in required.items():
        try:
            __import__(module)
            print(f"✅ {name:.<50} OK")
        except ImportError:
            print(f"❌ {name:.<50} MISSING")
            all_ok = False
    
    return all_ok

def check_files():
    """Check required files exist"""
    print_header("3️⃣  Required Files Check")
    
    required_files = [
        'dashboard_research.html',
        'backend_quantum_processor.py',
        'quantum_api_server.py',
        'run_quantum_system.py',
        'requirements.txt',
    ]
    
    base_path = Path(__file__).parent
    all_ok = True
    
    for filename in required_files:
        filepath = base_path / filename
        if filepath.exists():
            size = filepath.stat().st_size / 1024  # KB
            print(f"✅ {filename:.<50} OK ({size:.1f} KB)")
        else:
            print(f"❌ {filename:.<50} MISSING")
            all_ok = False
    
    return all_ok

def test_quantum_processor():
    """Test quantum processor with simple image"""
    print_header("4️⃣  Quantum Processor Test")
    
    try:
        print("Importing quantum processor...")
        from backend_quantum_processor import QuantumImageProcessor
        print("✅ Quantum processor imported")
        
        print("\nCreating test image...")
        import numpy as np
        test_image = np.array([
            [0.2, 0.4, 0.6, 0.8],
            [0.4, 0.6, 0.8, 1.0],
            [0.6, 0.8, 1.0, 0.8],
            [0.8, 1.0, 0.8, 0.6],
        ])
        print("✅ Test image created (4×4)")
        
        print("\nInitializing processor (image_size=4, shots=100)...")
        processor = QuantumImageProcessor(image_size=4, shots=100)
        print("✅ Processor initialized")
        
        print("\nProcessing with FRQI...")
        frqi_result = processor.process_with_frqi(test_image)
        print(f"✅ FRQI processing complete")
        print(f"   - PSNR: {frqi_result['metrics'].psnr:.2f} dB")
        print(f"   - SSIM: {frqi_result['metrics'].ssim:.4f}")
        print(f"   - Qubits: {frqi_result['metrics'].qubit_count}")
        print(f"   - Time: {frqi_result['metrics'].execution_time*1000:.2f} ms")
        
        print("\nProcessing with NEQR...")
        neqr_result = processor.process_with_neqr(test_image)
        print(f"✅ NEQR processing complete")
        print(f"   - PSNR: {neqr_result['metrics'].psnr:.2f} dB")
        print(f"   - SSIM: {neqr_result['metrics'].ssim:.4f}")
        print(f"   - Qubits: {neqr_result['metrics'].qubit_count}")
        print(f"   - Time: {neqr_result['metrics'].execution_time*1000:.2f} ms")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_ports():
    """Check if required ports are available"""
    print_header("5️⃣  Port Availability Check")
    
    import socket
    ports = {
        3000: "Dashboard",
        8000: "API Server",
    }
    
    all_ok = True
    for port, service in ports.items():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('localhost', port))
                print(f"✅ Port {port} available ({service})")
            except OSError:
                print(f"❌ Port {port} in use ({service})")
                all_ok = False
    
    return all_ok

def main():
    """Run all checks"""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  ⚛️  QUANTUM SYSTEM SETUP VERIFICATION  ⚛️".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")
    
    results = {
        "Python Version": check_python_version(),
        "Dependencies": check_dependencies(),
        "Required Files": check_files(),
        "Ports Available": check_ports(),
        "Quantum Processor": test_quantum_processor(),
    }
    
    print_header("✅ VERIFICATION SUMMARY")
    
    for check, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check:.<50} {status}")
    
    all_pass = all(results.values())
    
    if all_pass:
        print("\n" + "="*70)
        print("🎉 ALL CHECKS PASSED! System ready to run.")
        print("="*70)
        print("\nStart the system with:")
        print("  python run_quantum_system.py")
        print("\nOr run components separately:")
        print("  python quantum_api_server.py      # Terminal 1: API backend")
        print("  python serve_dashboard.py         # Terminal 2: Dashboard")
        print("  http://localhost:3000             # Browser: Open dashboard")
        print("\n")
        return 0
    else:
        print("\n" + "="*70)
        print("❌ SETUP INCOMPLETE - Issues found above")
        print("="*70)
        print("\nTo fix dependencies:")
        print("  pip install --upgrade -r requirements.txt")
        print("\nFor more help, see:")
        print("  QUANTUM_SYSTEM_QUICK_START.md")
        print("\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
