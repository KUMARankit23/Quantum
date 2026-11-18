"""
FastAPI Server for Quantum Image Processing
Serves FRQI vs NEQR comparison with real-time quantum simulation
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import io
import json
import base64
import numpy as np
from PIL import Image
import asyncio
import threading
from datetime import datetime
from pathlib import Path
import uuid

# Import quantum processors
from backend_quantum_processor import QuantumImageProcessor, FRQIEncoder, NEQREncoder
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

app = FastAPI(title="Quantum Image Processing API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store processing jobs
processing_jobs = {}
job_lock = threading.Lock()

class ProcessingJob:
    def __init__(self, job_id: str):
        self.job_id = job_id
        self.status = "pending"  # pending, processing, completed, failed
        self.progress = 0
        self.results = None
        self.error = None
        self.created_at = datetime.now()

def image_to_base64(image_array: np.ndarray) -> str:
    """Convert numpy array to base64 string"""
    # Normalize to 0-255
    normalized = (image_array * 255).astype(np.uint8)
    
    # Create PIL image
    pil_image = Image.fromarray(normalized, mode='L')
    
    # Convert to base64
    buffered = io.BytesIO()
    pil_image.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode()
    
    return f"data:image/png;base64,{img_base64}"

def generate_circuit_image(circuit, filename: str) -> str:
    """Generate circuit diagram and return as base64"""
    try:
        fig, ax = plt.subplots(figsize=(12, 8))
        circuit.draw(output='mpl', ax=ax)
        
        buffered = io.BytesIO()
        plt.savefig(buffered, format="PNG", dpi=100, bbox_inches='tight')
        buffered.seek(0)
        plt.close(fig)
        
        circuit_base64 = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/png;base64,{circuit_base64}"
    except Exception as e:
        print(f"Error generating circuit image: {e}")
        return None

@app.get("/")
async def root():
    return {
        "message": "Quantum Image Processing API",
        "endpoints": {
            "upload": "/upload",
            "process_frqi": "/process/frqi",
            "process_neqr": "/process/neqr",
            "compare": "/compare",
            "job_status": "/job/{job_id}",
            "health": "/health"
        }
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "backend": "Qiskit Aer"
    }

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    """Upload and preprocess image"""
    try:
        # Read file
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Convert to numpy
        image_array = np.array(image)
        
        return {
            "filename": file.filename,
            "size": list(image_array.shape),
            "uploaded_at": datetime.now().isoformat(),
            "message": "Image uploaded successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/process/frqi")
async def process_frqi(file: UploadFile = File(...), image_size: int = 8, shots: int = 1000):
    """Process image with FRQI encoding"""
    try:
        # Create job
        job_id = str(uuid.uuid4())
        job = ProcessingJob(job_id)
        job.status = "processing"
        job.progress = 10
        
        with job_lock:
            processing_jobs[job_id] = job
        
        # Read and preprocess image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        processor = QuantumImageProcessor(image_size=image_size, shots=shots)
        preprocessed = processor.preprocess_image(image)
        
        job.progress = 30
        
        # Process with FRQI
        result = processor.process_with_frqi(preprocessed)
        
        job.progress = 70
        
        # Generate circuit image
        circuit_img = generate_circuit_image(result['circuit'], f"frqi_{job_id}.png")
        
        job.progress = 90
        
        # Prepare results
        frqi_results = {
            "job_id": job_id,
            "method": "FRQI",
            "image_size": image_size,
            "shots": shots,
            "preprocessing": {
                "input_shape": list(image.size),
                "output_shape": list(preprocessed.shape),
                "normalized": True
            },
            "original_image": image_to_base64(preprocessed),
            "reconstructed_image": image_to_base64(result['reconstructed']),
            "circuit_diagram": circuit_img,
            "metrics": {
                "mse": result['metrics'].mse,
                "psnr": result['metrics'].psnr,
                "ssim": result['metrics'].ssim,
                "fidelity": result['metrics'].fidelity,
                "reconstruction_error": result['metrics'].reconstruction_error,
                "circuit_depth": result['metrics'].circuit_depth,
                "gate_count": result['metrics'].gate_count,
                "qubit_count": result['metrics'].qubit_count,
                "measurement_shots": result['metrics'].measurement_shots,
                "execution_time_ms": result['metrics'].execution_time * 1000
            },
            "encoding_info": {
                "position_qubits": processor.frqi_encoder.n_position_qubits,
                "color_qubits": processor.frqi_encoder.n_color_qubits,
                "total_qubits": processor.frqi_encoder.total_qubits,
                "encoding_formula": "θ = 2 * arccos(sqrt(pixel_value))",
                "gate_types": ["Hadamard", "RY (Rotation)", "Measurement"]
            }
        }
        
        job.results = frqi_results
        job.status = "completed"
        job.progress = 100
        
        return frqi_results
        
    except Exception as e:
        job.status = "failed"
        job.error = str(e)
        with job_lock:
            processing_jobs[job_id] = job
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process/neqr")
async def process_neqr(file: UploadFile = File(...), image_size: int = 8, shots: int = 1000, color_bits: int = 4):
    """Process image with NEQR encoding"""
    try:
        # Create job
        job_id = str(uuid.uuid4())
        job = ProcessingJob(job_id)
        job.status = "processing"
        job.progress = 10
        
        with job_lock:
            processing_jobs[job_id] = job
        
        # Read and preprocess image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        processor = QuantumImageProcessor(image_size=image_size, shots=shots)
        preprocessed = processor.preprocess_image(image)
        
        job.progress = 30
        
        # Process with NEQR
        result = processor.process_with_neqr(preprocessed)
        
        job.progress = 70
        
        # Generate circuit image
        circuit_img = generate_circuit_image(result['circuit'], f"neqr_{job_id}.png")
        
        job.progress = 90
        
        # Prepare results
        neqr_results = {
            "job_id": job_id,
            "method": "NEQR",
            "image_size": image_size,
            "shots": shots,
            "color_bits": color_bits,
            "preprocessing": {
                "input_shape": list(image.size),
                "output_shape": list(preprocessed.shape),
                "normalized": True
            },
            "original_image": image_to_base64(preprocessed),
            "reconstructed_image": image_to_base64(result['reconstructed']),
            "circuit_diagram": circuit_img,
            "metrics": {
                "mse": result['metrics'].mse,
                "psnr": result['metrics'].psnr,
                "ssim": result['metrics'].ssim,
                "fidelity": result['metrics'].fidelity,
                "reconstruction_error": result['metrics'].reconstruction_error,
                "circuit_depth": result['metrics'].circuit_depth,
                "gate_count": result['metrics'].gate_count,
                "qubit_count": result['metrics'].qubit_count,
                "measurement_shots": result['metrics'].measurement_shots,
                "execution_time_ms": result['metrics'].execution_time * 1000
            },
            "encoding_info": {
                "position_qubits": processor.neqr_encoder.n_position_qubits,
                "color_qubits": processor.neqr_encoder.color_bits,
                "total_qubits": processor.neqr_encoder.total_qubits,
                "intensity_levels": 2 ** color_bits,
                "encoding_formula": "Binary computational basis states",
                "gate_types": ["Hadamard", "X (Pauli-X)", "Measurement"]
            }
        }
        
        job.results = neqr_results
        job.status = "completed"
        job.progress = 100
        
        return neqr_results
        
    except Exception as e:
        job.status = "failed"
        job.error = str(e)
        with job_lock:
            processing_jobs[job_id] = job
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/compare")
async def compare_methods(file: UploadFile = File(...), image_size: int = 8, shots: int = 1000):
    """Compare FRQI and NEQR on the same image"""
    try:
        job_id = str(uuid.uuid4())
        job = ProcessingJob(job_id)
        job.status = "processing"
        job.progress = 5
        
        with job_lock:
            processing_jobs[job_id] = job
        
        # Read and preprocess
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        processor = QuantumImageProcessor(image_size=image_size, shots=shots)
        preprocessed = processor.preprocess_image(image)
        
        job.progress = 20
        
        # Compare methods
        comparison_results = processor.compare_methods(preprocessed)
        
        job.progress = 85
        
        # Prepare comprehensive comparison
        frqi_data = comparison_results['frqi']
        neqr_data = comparison_results['neqr']
        comparison = comparison_results['comparison']
        
        # Generate circuit images
        frqi_circuit_img = generate_circuit_image(frqi_data['circuit'], f"frqi_compare_{job_id}.png")
        neqr_circuit_img = generate_circuit_image(neqr_data['circuit'], f"neqr_compare_{job_id}.png")
        
        job.progress = 95
        
        response = {
            "job_id": job_id,
            "comparison_timestamp": datetime.now().isoformat(),
            "image_size": image_size,
            "measurement_shots": shots,
            "original_image": image_to_base64(preprocessed),
            
            "frqi": {
                "reconstructed_image": image_to_base64(frqi_data['reconstructed']),
                "circuit_diagram": frqi_circuit_img,
                "metrics": {
                    "psnr": frqi_data['metrics'].psnr,
                    "ssim": frqi_data['metrics'].ssim,
                    "mse": frqi_data['metrics'].mse,
                    "fidelity": frqi_data['metrics'].fidelity,
                    "reconstruction_error": frqi_data['metrics'].reconstruction_error,
                    "circuit_depth": frqi_data['metrics'].circuit_depth,
                    "gate_count": frqi_data['metrics'].gate_count,
                    "qubit_count": frqi_data['metrics'].qubit_count,
                    "execution_time_ms": frqi_data['metrics'].execution_time * 1000
                }
            },
            
            "neqr": {
                "reconstructed_image": image_to_base64(neqr_data['reconstructed']),
                "circuit_diagram": neqr_circuit_img,
                "metrics": {
                    "psnr": neqr_data['metrics'].psnr,
                    "ssim": neqr_data['metrics'].ssim,
                    "mse": neqr_data['metrics'].mse,
                    "fidelity": neqr_data['metrics'].fidelity,
                    "reconstruction_error": neqr_data['metrics'].reconstruction_error,
                    "circuit_depth": neqr_data['metrics'].circuit_depth,
                    "gate_count": neqr_data['metrics'].gate_count,
                    "qubit_count": neqr_data['metrics'].qubit_count,
                    "execution_time_ms": neqr_data['metrics'].execution_time * 1000
                }
            },
            
            "comparison_analysis": {
                "qubit_efficiency": {
                    "frqi_qubits": comparison['qubit_advantage']['frqi_qubits'],
                    "neqr_qubits": comparison['qubit_advantage']['neqr_qubits'],
                    "difference": comparison['qubit_advantage']['difference'],
                    "winner": "FRQI" if comparison['qubit_advantage']['difference'] > 0 else "NEQR",
                    "analysis": "FRQI uses fewer qubits due to amplitude encoding"
                },
                
                "quality_metrics": {
                    "psnr_winner": comparison['quality_comparison']['psnr']['winner'],
                    "ssim_winner": comparison['quality_comparison']['ssim']['winner'],
                    "mse_winner": comparison['quality_comparison']['mse']['winner'],
                    "psnr_frqi": comparison['quality_comparison']['psnr']['frqi'],
                    "psnr_neqr": comparison['quality_comparison']['psnr']['neqr'],
                    "ssim_frqi": comparison['quality_comparison']['ssim']['frqi'],
                    "ssim_neqr": comparison['quality_comparison']['ssim']['neqr']
                },
                
                "circuit_complexity": {
                    "depth_frqi": comparison['circuit_complexity']['depth']['frqi'],
                    "depth_neqr": comparison['circuit_complexity']['depth']['neqr'],
                    "depth_difference": comparison['circuit_complexity']['depth']['difference'],
                    "gates_frqi": comparison['circuit_complexity']['gates']['frqi'],
                    "gates_neqr": comparison['circuit_complexity']['gates']['neqr'],
                    "gates_difference": comparison['circuit_complexity']['gates']['difference']
                },
                
                "execution_performance": {
                    "faster_method": comparison['execution_time']['faster'],
                    "frqi_time_ms": comparison['execution_time']['frqi'] * 1000,
                    "neqr_time_ms": comparison['execution_time']['neqr'] * 1000
                }
            },
            
            "research_insights": {
                "qubit_requirement": "FRQI encodes color as amplitude, NEQR uses basis states",
                "practical_factors": [
                    "Circuit depth affects quantum noise accumulation",
                    "FRQI more efficient for small images",
                    "NEQR provides better color fidelity",
                    "Both methods scalable to larger images"
                ],
                "recommendations": [
                    "Use FRQI for qubit-limited devices",
                    "Use NEQR when precision color is critical",
                    "Consider circuit depth for noise-sensitive systems"
                ]
            }
        }
        
        job.results = response
        job.status = "completed"
        job.progress = 100
        
        return response
        
    except Exception as e:
        job.status = "failed"
        job.error = str(e)
        with job_lock:
            processing_jobs[job_id] = job
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/job/{job_id}")
async def get_job_status(job_id: str):
    """Get processing job status"""
    with job_lock:
        if job_id not in processing_jobs:
            raise HTTPException(status_code=404, detail="Job not found")
        
        job = processing_jobs[job_id]
        
        return {
            "job_id": job_id,
            "status": job.status,
            "progress": job.progress,
            "created_at": job.created_at.isoformat(),
            "error": job.error,
            "has_results": job.results is not None
        }

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("Quantum Image Processing API Server")
    print("Powered by Qiskit Aer Simulator")
    print("="*60)
    print("\nStarting server on http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
