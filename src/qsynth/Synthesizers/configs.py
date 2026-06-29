from dataclasses import dataclass
from typing import Optional

from qsynth.ReachabilitySolver.solvers.solver_extraction import ReachabilitySolverNames
from qsynth.layout_synthesis_wrapper import check_options


@dataclass
class LayoutSynthesisConfig:
    """Configuration object for layout synthesis parameters."""
    # Optimization
    metric: str = "cx-count"
    secondary_metric: Optional[str] = None
    parallel_swaps: bool = False
    initial_mapping: Optional[dict[int, int]] = None

    # Ancillaries and subarchitectures
    subarchitecture: Optional[bool] = None
    num_ancillary_qubits: Optional[int] = None

    # Solver options
    search_strategy: str = "forward"
    swap_upper_bound: Optional[int] = None
    model: str = "sat"
    solver: Optional[str] = None

    # Circuit options
    relaxed_dependencies: bool = False
    cancel_cnots: bool = False
    allow_bridges: bool = False

    # Execution
    intermediate_files_path: str = "./intermediate_files"
    timeout: int | float = 1800
    verbose: int = -1

    def __post_init__(self):
        self._set_defaults()
        self._validate()

    def _set_defaults(self):
        # Set subarchitecture to False by default - unless num_ancillary_qubits is set to positive number
        if self.subarchitecture is None:
            self.subarchitecture = (
                    self.num_ancillary_qubits is not None and self.num_ancillary_qubits > 0
            )

        # Set planning model from metric
        if self.model == "planning":
            if self.metric == "cx-count" and self.secondary_metric is None:
                self.model = "local"
            else:
                self.model = "cond_cost_opt"

        # Set solver default from model
        if self.solver is None:
            match self.model:
                case "sat":
                    self.solver = "cd19"
                case "global" | "local" | "lifted" | "cost_opt" | "lc_incr":
                    self.solver = "fd-bjolp"
                case "cond_cost_opt":
                    self.solver = "fd-ms"
                case _:
                    raise ValueError(f"Invalid model: {self.model}.")

        # Set num_ancillary_qubits default
        if self.num_ancillary_qubits is None:
            if self.subarchitecture:
                self.num_ancillary_qubits = 0
                if self.verbose >= 0:
                    print("Warning: With subarchitectures, num_ancillary_qubits is set to 0 by default.")
            else:
                self.num_ancillary_qubits = -1

    def _validate(self):
        if self.metric not in ["cx-count", "cx-depth", "depth"]:# "cx-depth_cx-count", "depth_cx-count", "cx-count_cx-depth"]:
            raise ValueError(f"{self.metric} is not a valid primary metric.")

        if self.secondary_metric not in [None, "cx-count", "cx-depth"]:
            raise ValueError(f"{self.secondary_metric} is not a valid primary metric.")

        if self.secondary_metric is not None:
            if self.secondary_metric == self.metric:
                raise ValueError("Secondary metric should be different from primary metric.")
            elif self.secondary_metric == "cx-depth" and self.metric != "cx-count":
                raise ValueError("Having cx-depth as secondary metric is only supported for cx-count as primary metric.")

        if self.parallel_swaps:
            if self.metric != "cx-count":
                raise ValueError("Parallel swaps is only compatible with optimizing for cx-count.")

        if self.subarchitecture and self.initial_mapping is not None:
            raise ValueError("Subarchitecture mapping must be disabled to enforce an initial mapping.")

        if self.num_ancillary_qubits > 0 and not self.subarchitecture:
            raise ValueError("Subarchitecture must be enabled to enforce a positive number of ancillary qubits.")

        if self.search_strategy not in ["forward", "backward"]:
            if not ReachabilitySolverNames.is_valid(self.search_strategy):
                raise ValueError(f"{self.search_strategy} is not a valid search strategy.")
            if self.relaxed_dependencies:
                raise ValueError(f"Relaxed dependencies are not supported for search strategy {self.search_strategy}.")
            if self.cancel_cnots:
                raise ValueError(f"CNOT cancellations are not supported for search strategy {self.search_strategy}.")
            if self.allow_bridges:
                raise ValueError(f"Bridges are not supported for search strategy {self.search_strategy}.")
            if self.initial_mapping:
                raise ValueError(f"Enforcing an initial mapping is not supported for search strategy {self.search_strategy}.")
            if self.solver not in ('cd19', 'cd195', 'cdl19', 'cdl195', 'cadical195'):
                raise ValueError(f"Search strategy {self.search_strategy} is only compatible with CaDiCal 1.9.5 (solver='cd19').")

        if self.search_strategy != "forward":
            if self.metric != "cx-count" or self.secondary_metric is not None:
                raise ValueError(
                    f"Search strategy {self.search_strategy} can only be used for optimizing cx-count. Use 'forward' instead.")

        if self.search_strategy == "backward" and self.swap_upper_bound is None:
            raise ValueError("A swap_upper_bound must be provided when the search_strategy is 'backward'.")

        if self.initial_mapping is not None:
            if self.metric != "cx-count" or self.secondary_metric is not None:
                raise ValueError("Enforcing an initial mapping is only compatible with optimizing for cx-count.")

        combined_metric = self.metric if self.secondary_metric is None else f"{self.metric}_{self.secondary_metric}"
        check_options(self.model, self.solver, combined_metric)


@dataclass
class CnotSynthesisConfig:
    """Configuration object for CNOT synthesis parameters."""
    metric: str = "cx-depth"
    bound_metric: Optional[str] = None
    output_qubit_permute: bool = False

    search_strategy: str = "forward"
    model: str = "sat"
    solver: Optional[str] = None

    intermediate_files_path: str = "./intermediate_files"
    verbose: int = -1

    def __post_init__(self):
        self._set_defaults()
        self._validate()

    def _set_defaults(self):
        # Set default solver
        if self.solver is None:
            if self.model == "planning":
                self.solver = "fd-ms"
            elif self.model == "qbf":
                self.solver = "caqe"
            elif self.model == "sat":
                self.solver = "pysat-cd19"

    def _validate(self):
        validate_optimization_and_bound_metric(self.metric, self.bound_metric)

        if (self.metric == "cx-count"
                and self.bound_metric == "cx-depth"
                and self.search_strategy not in ["forward", "backward", "goingdown", "maxsat"]):
            raise ValueError(f"Search strategy {self.search_strategy} is not compatible with optimizing for cx-count while bounding cx-depth.")

        if self.model not in ["sat", "qbf", "planning"]:
            raise ValueError(f"Invalid model: {self.model}")

        if self.model == "planning":
            if self.output_qubit_permute:
                raise ValueError("Qubit permutation is only available with SAT model.")
            if self.metric != "cx-count":
                raise ValueError(f"Use cx-count metric for model=planning.")

        if self.model == "qbf" and self.output_qubit_permute:
            raise ValueError("Qubit permutation is only available with SAT model.")

        if self.search_strategy not in ["forward", "backward", "unbounded-forward"]:
            if not ReachabilitySolverNames.is_valid(self.search_strategy):
                raise ValueError(f"{self.search_strategy} is not a valid search strategy.")
            # Strip 'pysat-' from solver-name
            if self.solver[6:] not in ('cd19', 'cd195', 'cdl19', 'cdl195', 'cadical195'):
                raise ValueError(f"Search strategy {self.search_strategy} is only compatible with CaDiCal 1.9.5 (solver='pysat-cd19').")


@dataclass
class CnotRzSynthesisConfig:
    """Configuration object for CNOT+Rz synthesis parameters."""
    metric: str = "cx-depth"
    bound_metric: Optional[str] = None
    output_qubit_permute: bool = False

    search_strategy: str = "forward"

    intermediate_files_path: str = "./intermediate_files"
    verbose: int = -1

    def __post_init__(self):
        self._set_defaults()
        self._validate()

    def _set_defaults(self):
        # Do nothing
        pass

    def _validate(self):
        validate_optimization_and_bound_metric(self.metric, self.bound_metric)

        if (self.metric == "cx-count"
                and self.bound_metric == "cx-depth"
                and self.search_strategy not in ["forward", "backward", "maxsat"]):
            raise ValueError(f"Search strategy {self.search_strategy} is not compatible with optimizing for cx-count while bounding cx-depth.")


@dataclass
class CliffordSynthesisConfig:
    """Configuration object for Clifford synthesis parameters."""
    metric: str = "cx-depth"
    bound_metric: Optional[str] = None
    output_qubit_permute: bool = False
    postprocess_1q_gates: Optional[str] = "greedy"

    gate_ordering: bool = True
    simple_path_restrictions: bool = False
    cycle_bound: int = 3

    search_strategy: str = "forward"
    model: Optional[str] = "sat"
    solver: Optional[str] = None

    intermediate_files_path: str = "./intermediate_files"
    verbose: int = -1

    def __post_init__(self):
        self._set_defaults()
        self._validate()

    def _set_defaults(self):
        if self.model == "planning":
            # Auto-derive encoding from metric
            if self.metric == "cx-count":
                self.encoding = "normalform"
            elif self.metric == "cx-count_1q-count":
                self.encoding = "costbased"
            else:
                raise ValueError(f"Invalid optimization metric for planning model: {self.metric}")

            if self.solver is None:
                self.solver = "fd-ms"

        elif self.model == "sat":
            self.encoding = None
            if self.solver is None:
                self.solver = "pysat-cd19"

    def _validate(self):
        if self.model == "planning":
            if self.metric not in ["cx-count", "cx-count_1q-count"]:
                raise ValueError(f"For planning based Clifford synthesis, metric should be either 'cx-count' or 'cx-count_1q-count'.")
            if self.bound_metric is not None:
                raise ValueError(f"Specifying a bound metric requires using model='sat'.")
        elif self.model == "sat":
            validate_optimization_and_bound_metric(self.metric, self.bound_metric)

        else:
            raise ValueError(f"Invalid model: {self.model}")



def validate_optimization_and_bound_metric(optimization_metric, bound_metric):
    if optimization_metric not in ["cx-count", "cx-depth"]:
        raise ValueError(f"Invalid optimization metric: {optimization_metric}")

    if bound_metric == optimization_metric:
        raise ValueError("Bound metric must be different from optimization metric.")

    if bound_metric not in [None, "cx-count", "cx-depth"]:
        raise ValueError(f"Invalid bound metric: {bound_metric}")
