class Platform:
    def __init__(
        self,
        name: str,
        qubits: int,
        connectivity_graph: set[tuple[int, int]],
        description: str = "No description.",
        connectivity_graph_drawing: str | None = None,
    ):
        self.name = name
        self.qubits = qubits
        self.description = description
        self.connectivity_graph_drawing = connectivity_graph_drawing

        # Connectivity graph is an undirected graph.
        self.connectivity_graph = connectivity_graph.union(
            {(j, i) for i, j in connectivity_graph}
        )
