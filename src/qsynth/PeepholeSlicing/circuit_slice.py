# Irfansha Shaik, Aarhus, 05 January 2023.


class CircuitSlice:

    # In a cirucit, depending on optimization criteria
    # we divide into two types of slices
    def __init__(self):
        self.optimization_slice = []
        self.non_optimization_slice = []
        self.unused_qubits_optimization_slice = []
        self.used_qubits_optimization_slice = []
        self.projection_map = {}
        self.reverse_projection_map = {}
        # we update with current slice index for easy composition:
        self.slice_index = -1
