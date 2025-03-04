from src.DepthOptimal.synthesizers.planning.cond_cost_based_optimal_planning import (
    ConditionalCostBasedOptimalPlanningSynthesizer,
)
from src.DepthOptimal.synthesizers.planning.synthesizer import PlanningSynthesizer
from src.DepthOptimal.synthesizers.planning.cost_based_optimal_planning import (
    CostBasedOptimalPlanningSynthesizer,
)
from src.DepthOptimal.synthesizers.planning.local_clock_incremental_planning import (
    LocalClockIncrementalPlanningSynthesizer,
)
from src.DepthOptimal.synthesizers.sat.synthesizer import SATSynthesizer
import src.DepthOptimal.synthesizers.sat.synthesizer as sat
from src.DepthOptimal.synthesizers.sat.phys import PhysSynthesizer

from src.DepthOptimal.synthesizers.planning.solvers import (
    FAST_DOWNWARD_MERGE_AND_SHRINK,
    FAST_DOWNWARD_BJOLP,
    Solver,
)

import pysat.solvers
import atexit

synthesizers: dict[str, PlanningSynthesizer | SATSynthesizer] = {
    "cost_opt": CostBasedOptimalPlanningSynthesizer(),
    "cond_cost_opt": ConditionalCostBasedOptimalPlanningSynthesizer(),
    "lc_incr": LocalClockIncrementalPlanningSynthesizer(),
    "sat": PhysSynthesizer(),
}

OPTIMAL_PLANNING_SYNTHESIZERS = [
    name
    for name, inst in synthesizers.items()
    if isinstance(inst, PlanningSynthesizer) and inst.is_optimal
]
CONDITIONAL_PLANNING_SYNTHESIZERS = [
    name
    for name, inst in synthesizers.items()
    if isinstance(inst, PlanningSynthesizer) and inst.uses_conditional_effects
]

# Do not pre-initialize solvers
solvers: dict[str, Solver | sat.Solver] = {
    "fd-ms": FAST_DOWNWARD_MERGE_AND_SHRINK,
    "fd-bjolp": FAST_DOWNWARD_BJOLP,
    "cd15": pysat.solvers.Cadical153,
    "cd19": pysat.solvers.Cadical195,
    "g42": pysat.solvers.Glucose42,
    "mcm": pysat.solvers.MapleCM,
    "mcb": pysat.solvers.MapleChrono,
    "m22": pysat.solvers.Minisat22,
}
