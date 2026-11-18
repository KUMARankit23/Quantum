"""
Quantum circuit builder for image processing.
Constructs circuits for state preparation and measurement.
"""

import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from typing import Optional, List
from src.quantum.encoding import AmplitudeEncoder


class CircuitBuilder:
    """
    Builds quantum circuits for image processing.
    
    Supports:
    - State preparation (amplitude encoding)
    - Processing circuits (basic, medium, deep)
    - Measurement operations
    """
    
    def __init__(self, encoding_method: str = "amplitude"):
        """
        Initialize circuit builder.
        
        Args:
            encoding_method: Encoding type ("amplitude" is primary)
        """
        self.encoding_method = encoding_method
    
    def build_state_preparation(self, image: np.ndarray, 
                               circuit_type: str = "basic") -> QuantumCircuit:
        """
        Build state preparation circuit for image.
        
        Args:
            image: Input image (2D array, normalized [0,1])
            circuit_type: Circuit complexity ("basic", "medium", "deep")
            
        Returns:
            QuantumCircuit with state preparation gates
        """
        # Get encoding
        encoder = AmplitudeEncoder(image)
        num_qubits = encoder.num_qubits
        
        # Create circuit
        qr = QuantumRegister(num_qubits, 'q')
        circuit = QuantumCircuit(qr, name="state_prep")
        
        # Get amplitudes
        amplitudes = encoder.encode()
        
        # Initialize state
        circuit.initialize(amplitudes, qr)
        
        # Add optional processing gates
        if circuit_type == "medium":
            self._add_medium_processing(circuit, qr)
        elif circuit_type == "deep":
            self._add_deep_processing(circuit, qr)
        
        return circuit
    
    def _add_medium_processing(self, circuit: QuantumCircuit, 
                              qr: QuantumRegister) -> None:
        """Add medium complexity processing (entanglement)."""
        num_qubits = len(qr)
        
        # Add Hadamard layer
        for i in range(num_qubits):
            circuit.h(qr[i])
        
        # Add CNOT chain for entanglement
        for i in range(num_qubits - 1):
            circuit.cx(qr[i], qr[i + 1])
        
        # Add phase rotations
        for i in range(num_qubits):
            circuit.rz(np.pi / 4, qr[i])
    
    def _add_deep_processing(self, circuit: QuantumCircuit, 
                            qr: QuantumRegister) -> None:
        """Add deep complexity processing (multiple layers)."""
        num_qubits = len(qr)
        
        # Layer 1: Hadamard
        for i in range(num_qubits):
            circuit.h(qr[i])
        
        # Layer 2: CNOT connections
        for i in range(num_qubits - 1):
            circuit.cx(qr[i], qr[i + 1])
        
        # Layer 3: Rotations
        for i in range(num_qubits):
            circuit.rx(np.pi / 6, qr[i])
            circuit.rz(np.pi / 3, qr[i])
        
        # Layer 4: More entanglement
        for i in range(num_qubits - 1):
            circuit.cz(qr[i], qr[i + 1])
        
        # Layer 5: Final rotations
        for i in range(num_qubits):
            circuit.ry(np.pi / 5, qr[i])
    
    def add_measurement(self, circuit: QuantumCircuit) -> QuantumCircuit:
        """
        Add measurement operations to circuit.
        
        Args:
            circuit: Input circuit
            
        Returns:
            Circuit with measurements added
        """
        # Get quantum register
        qr = circuit.qregs[0]
        num_qubits = len(qr)
        
        # Add classical register
        cr = ClassicalRegister(num_qubits, 'c')
        circuit.add_register(cr)
        
        # Measure all qubits
        circuit.measure(qr, cr)
        
        return circuit
    
    def build_complete_circuit(self, image: np.ndarray, 
                             circuit_type: str = "basic") -> QuantumCircuit:
        """
        Build complete circuit: state prep + measurement.
        
        Args:
            image: Input image
            circuit_type: Circuit complexity
            
        Returns:
            Complete circuit with measurement
        """
        circuit = self.build_state_preparation(image, circuit_type)
        circuit = self.add_measurement(circuit)
        return circuit
    
    def get_circuit_info(self, circuit: QuantumCircuit) -> dict:
        """
        Get circuit information.
        
        Args:
            circuit: Quantum circuit
            
        Returns:
            Dictionary with circuit metrics
        """
        num_qubits = circuit.num_qubits
        num_clbits = circuit.num_clbits
        depth = circuit.depth()
        
        # Count gates
        gate_counts = {}
        two_qubit_count = 0
        single_qubit_count = 0
        
        for instruction in circuit.data:
            gate_name = instruction.operation.name
            num_qubits_used = len(instruction.qubits)
            
            gate_counts[gate_name] = gate_counts.get(gate_name, 0) + 1
            
            if num_qubits_used == 1:
                single_qubit_count += 1
            elif num_qubits_used == 2:
                two_qubit_count += 1
        
        total_gates = sum(gate_counts.values())
        
        return {
            "num_qubits": num_qubits,
            "num_clbits": num_clbits,
            "circuit_depth": depth,
            "total_gates": total_gates,
            "single_qubit_gates": single_qubit_count,
            "two_qubit_gates": two_qubit_count,
            "gate_counts": gate_counts,
        }
    
    def visualize_circuit_qasm(self, circuit: QuantumCircuit) -> str:
        """
        Get circuit as OpenQASM string.
        
        Args:
            circuit: Quantum circuit
            
        Returns:
            QASM representation
        """
        return circuit.qasm()


class StatePreparationCircuit:
    """Helper class for state preparation circuit construction."""
    
    @staticmethod
    def create_uniform_superposition(num_qubits: int) -> QuantumCircuit:
        """
        Create uniform superposition state.
        
        Returns: 1/√(2^n) Σ |i⟩
        """
        qr = QuantumRegister(num_qubits, 'q')
        circuit = QuantumCircuit(qr, name="uniform_superposition")
        
        for i in range(num_qubits):
            circuit.h(qr[i])
        
        return circuit
    
    @staticmethod
    def create_product_state(num_qubits: int, state_string: str) -> QuantumCircuit:
        """
        Create product state from string like "0101".
        
        Args:
            num_qubits: Number of qubits
            state_string: State string (e.g., "0101")
            
        Returns:
            Circuit preparing the state
        """
        if len(state_string) != num_qubits:
            raise ValueError(f"State string length {len(state_string)} != {num_qubits}")
        
        qr = QuantumRegister(num_qubits, 'q')
        circuit = QuantumCircuit(qr, name="product_state")
        
        # Apply X gates to set |1⟩ states
        for i, bit in enumerate(state_string):
            if bit == '1':
                circuit.x(qr[i])
        
        return circuit
    
    @staticmethod
    def create_bell_pair(q0: int, q1: int) -> QuantumCircuit:
        """Create Bell state (maximally entangled)."""
        num_qubits = max(q0, q1) + 1
        qr = QuantumRegister(num_qubits, 'q')
        circuit = QuantumCircuit(qr, name="bell_pair")
        
        circuit.h(qr[q0])
        circuit.cx(qr[q0], qr[q1])
        
        return circuit


if __name__ == "__main__":
    # Quick test
    from src.preprocessing.dataset import Dataset
    
    dataset = Dataset()
    image = dataset.generate_checkerboard(4, save=False)
    
    builder = CircuitBuilder()
    
    # Build state prep circuit
    circuit_basic = builder.build_state_preparation(image, circuit_type="basic")
    info_basic = builder.get_circuit_info(circuit_basic)
    
    # Build complete circuit
    circuit_full = builder.build_complete_circuit(image)
    info_full = builder.get_circuit_info(circuit_full)
    
    print(f"Image shape: {image.shape}")
    print(f"\nBasic State Preparation Circuit:")
    print(f"  Qubits: {info_basic['num_qubits']}")
    print(f"  Depth: {info_basic['circuit_depth']}")
    print(f"  Total gates: {info_basic['total_gates']}")
    print(f"  2-qubit gates: {info_basic['two_qubit_gates']}")
    
    print(f"\nComplete Circuit (with measurement):")
    print(f"  Qubits: {info_full['num_qubits']}")
    print(f"  Classical bits: {info_full['num_clbits']}")
    print(f"  Depth: {info_full['circuit_depth']}")
    print(f"  Total gates: {info_full['total_gates']}")
