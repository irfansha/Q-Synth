# result class for quantum circuit initial mapping final mapping
import base64
import io
import json
from typing import Optional

from qiskit import qpy
from dataclasses import dataclass
from qiskit import QuantumCircuit


def circuit_to_str(circuit: QuantumCircuit) -> str:
    """Serialize a QuantumCircuit to a Base64 string via QPY."""
    buffer = io.BytesIO()
    qpy.dump(circuit, buffer)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def str_to_circuit(data: str) -> QuantumCircuit:
    """Deserialize a Base64 string back to a QuantumCircuit via QPY."""
    buffer = io.BytesIO(base64.b64decode(data))
    return qpy.load(buffer)[0]  # qpy.load returns a list of circuits


def convert_int_keys_to_str(the_dict):
    return "None" if the_dict is None else {str(k): v for k, v in the_dict.items()}


def convert_str_keys_to_int(the_dict):
    return None if the_dict == "None" else {int(k): v for k, v in the_dict.items()}


@dataclass
class MappingResult:
    """
    Class to hold the results of a mapping operation.

    Attributes:
        circuit (QuantumCircuit): quantum circuit after mapping.
        initial_mapping (dict[int, int]): initial mapping of logical qubits to physical qubits.
        final_mapping (dict[int, int]): final mapping of logical qubits to physical qubits.
        timed_out (bool): Indicates if the mapping operation timed out.
        no_plan_found (bool): Indicates if no mapping plan was found.
    """

    circuit: QuantumCircuit
    initial_mapping: dict[int, int]
    final_mapping: dict[int, int]
    timed_out: bool
    no_plan_found: bool

    def __str__(self):
        return f"MappingResult(circuit={self.circuit}, initial_mapping={self.initial_mapping}, final_mapping={self.final_mapping}, timed_out={self.timed_out}, no_plan_found={self.no_plan_found})"

    def __repr__(self):
        return self.__str__()

    def __init__(
            self,
            circuit: QuantumCircuit,
            initial_mapping: Optional[dict[int, int]]=None,
            final_mapping: Optional[dict[int, int]]=None,
            timed_out=False,
            no_plan_found=False
    ):
        """
        Constructs a MappingResult object containing a circuit, initial and final mappings, and information on whether
        the optimization was successful, timed out, or no plan was found. If no initial/final mapping is provided,
        a 1:1 mapping is assumed.
        """
        self.circuit = circuit
        if initial_mapping is None:
            initial_mapping = {i:i for i in range(circuit.num_qubits)}
        if final_mapping is None:
            final_mapping = {i:i for i in range(circuit.num_qubits)}
        self.initial_mapping = initial_mapping
        self.final_mapping = final_mapping
        self.timed_out = timed_out
        self.no_plan_found = no_plan_found

    def to_json(self) -> str:
        """
        Convert mapping result to a JSON string by saving the circuit as a serialized base64 string with QPY.
        """
        return json.dumps({
            "circuit": circuit_to_str(self.circuit),
            "initial_mapping": convert_int_keys_to_str(self.initial_mapping),
            "final_mapping": convert_int_keys_to_str(self.final_mapping),
            "timed_out": self.timed_out,
            "no_plan_found": self.no_plan_found,
        })

    @classmethod
    def from_json(cls, data):
        """
        Convert JSON string to mapping result by deserializing a QuantumCircuit from a base64 string using QPY.
        """
        obj = json.loads(data)
        return cls(
            circuit=str_to_circuit(obj["circuit"]),
            initial_mapping=convert_str_keys_to_int(obj["initial_mapping"]),
            final_mapping=convert_str_keys_to_int(obj["final_mapping"]),
            timed_out=obj["timed_out"],
            no_plan_found=obj["no_plan_found"],
        )
