"""
Quantum circuit and performance metrics.
"""

import numpy as np
from typing import Dict, List, Any
from qiskit import QuantumCircuit


def analyze_circuit(circuit: QuantumCircuit) -> Dict[str, Any]:
    """
    Analyze quantum circuit properties.
    
    Args:
        circuit: Qiskit QuantumCircuit
        
    Returns:
        Dictionary with circuit metrics
    """
    # Get circuit information
    num_qubits = circuit.num_qubits
    num_clbits = circuit.num_clbits
    
    # Count gates
    gate_counts = {}
    two_qubit_count = 0
    single_qubit_count = 0
    
    for instruction in circuit.data:
        gate_name = instruction.operation.name
        num_qubits_used = len(instruction.qubits)
        
        # Count gate types
        gate_counts[gate_name] = gate_counts.get(gate_name, 0) + 1
        
        # Count qubit types
        if num_qubits_used == 1:
            single_qubit_count += 1
        elif num_qubits_used == 2:
            two_qubit_count += 1
    
    # Calculate circuit depth
    depth = circuit.depth()
    
    # Total gates
    total_gates = sum(gate_counts.values())
    
    return {
        "num_qubits": num_qubits,
        "num_clbits": num_clbits,
        "total_gates": total_gates,
        "single_qubit_gates": single_qubit_count,
        "two_qubit_gates": two_qubit_count,
        "circuit_depth": depth,
        "gate_counts": gate_counts,
    }


def calculate_circuit_complexity(circuit: QuantumCircuit) -> float:
    """
    Calculate a simple circuit complexity metric.
    
    Complexity = total_gates × circuit_depth / num_qubits
    
    Args:
        circuit: Qiskit QuantumCircuit
        
    Returns:
        Complexity score
    """
    metrics = analyze_circuit(circuit)
    
    if metrics["num_qubits"] == 0:
        return 0.0
    
    complexity = (metrics["total_gates"] * metrics["circuit_depth"]) / metrics["num_qubits"]
    
    return float(complexity)


def estimate_required_shots(target_accuracy: float, num_outcomes: int) -> int:
    """
    Estimate number of shots needed to achieve target accuracy.
    
    For uniform distribution over n outcomes:
    N_shots = (z² × n) / (4 × accuracy²)
    
    where z ≈ 2 for ~95% confidence
    
    Args:
        target_accuracy: Desired accuracy (probability estimate error)
        num_outcomes: Number of possible measurement outcomes
        
    Returns:
        Estimated number of shots
    """
    z = 2  # ~95% confidence level
    shots = (z ** 2 * num_outcomes) / (4 * target_accuracy ** 2)
    
    return int(np.ceil(shots))


class QuantumMetricsCollector:
    """Collects and tracks quantum metrics across experiments."""
    
    def __init__(self):
        """Initialize metrics collector."""
        self.metrics = []
    
    def record(self, experiment_id: str, circuit: QuantumCircuit, 
              execution_time: float, num_shots: int, 
              fidelity: float = None) -> None:
        """
        Record quantum metrics for an experiment.
        
        Args:
            experiment_id: Experiment identifier
            circuit: Quantum circuit used
            execution_time: Execution time in seconds
            num_shots: Number of measurement shots
            fidelity: State fidelity (optional)
        """
        circuit_metrics = analyze_circuit(circuit)
        
        record = {
            "experiment_id": experiment_id,
            "num_qubits": circuit_metrics["num_qubits"],
            "total_gates": circuit_metrics["total_gates"],
            "two_qubit_gates": circuit_metrics["two_qubit_gates"],
            "circuit_depth": circuit_metrics["circuit_depth"],
            "execution_time": execution_time,
            "num_shots": num_shots,
            "fidelity": fidelity,
            "time_per_shot": execution_time / num_shots if num_shots > 0 else 0,
        }
        
        self.metrics.append(record)
    
    def get_summary(self) -> Dict:
        """
        Get summary statistics of collected metrics.
        
        Returns:
            Summary dictionary
        """
        if not self.metrics:
            return {}
        
        qubits = [m["num_qubits"] for m in self.metrics]
        gates = [m["total_gates"] for m in self.metrics]
        times = [m["execution_time"] for m in self.metrics]
        
        return {
            "num_experiments": len(self.metrics),
            "avg_qubits": np.mean(qubits),
            "avg_gates": np.mean(gates),
            "avg_time": np.mean(times),
            "min_time": np.min(times),
            "max_time": np.max(times),
        }


if __name__ == "__main__":
    from qiskit import QuantumCircuit, QuantumRegister
    
    # Create a simple test circuit
    qr = QuantumRegister(2, 'q')
    circuit = QuantumCircuit(qr)
    circuit.h(qr[0])
    circuit.cx(qr[0], qr[1])
    circuit.measure_all()
    
    metrics = analyze_circuit(circuit)
    print("Circuit metrics:", metrics)
    print("Complexity:", calculate_circuit_complexity(circuit))
    print("Estimated shots for 0.05 accuracy:", estimate_required_shots(0.05, 4))
