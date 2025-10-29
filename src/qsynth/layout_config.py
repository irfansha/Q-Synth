# SOLVERS
DEPTH_OPTIMAL_SOLVERS = {
    "fd-ms",
    "fd-bjolp",
    "cd15",
    "cd19",
    "g42",
    "mcm",
    "mcb",
    "m22",
}

SWAP_OPTIMAL_SOLVERS = {
    "fd-bjolp",
    "fd-ms",
    "fd-lmcut",
    "fdss-sat",
    "fdss-opt",
    "fdss-opt-2",
    "madagascar",
    "cd",
    "cd15",
    "cd19",
    "gc3",
    "gc4",
    "g3",
    "g4",
    "g42",
    "lgl",
    "mcb",
    "mcm",
    "mpl",
    "mg3",
    "mc",
    "m22",
    "mgh",
}

PLANNING_SOLVERS = {
    "fd-bjolp",
    "fd-ms",
    "fd-lmcut",
    "fdss-sat",
    "fdss-opt",
    "fdss-opt-2",
    "madagascar",
}

SAT_SOLVERS = {
    "cd",
    "cd15",
    "cd19",
    "gc3",
    "gc4",
    "g3",
    "g4",
    "g42",
    "lgl",
    "mcb",
    "mcm",
    "mpl",
    "mg3",
    "mc",
    "m22",
    "mgh",
}

SOLVERS = PLANNING_SOLVERS.union(SAT_SOLVERS)

# METRICS
DEPTH_OPTIMAL_METRICS = {"depth", "cx-depth", "depth_cx-count", "cx-depth_cx-count"}

SWAP_OPTIMAL_METRICS = {"cx-count"}

METRICS = DEPTH_OPTIMAL_METRICS.union(SWAP_OPTIMAL_METRICS)

# MODELS
DEPTH_OPTIMAL_PLANNERS = {"cost_opt", "cond_cost_opt", "lc_incr"}

SWAP_OPTIMAL_PLANNERS = {"local", "global", "lifted"}

SAT_MODELS = {"sat"}

DEPTH_OPTIMAL_MODELS = DEPTH_OPTIMAL_PLANNERS.union(SAT_MODELS)

SWAP_OPTIMAL_MODELS = SWAP_OPTIMAL_PLANNERS.union(SAT_MODELS)

PLANNING_MODELS = DEPTH_OPTIMAL_PLANNERS.union(SWAP_OPTIMAL_PLANNERS)

# planning will be expanded later to a default planner, depending on the metric
MODELS = PLANNING_MODELS.union(SAT_MODELS).add("planning")

CONDITIONAL_PLANNERS = {"fd-ms"}

CONDITIONAL_MODELS = {"cond_cost_opt"}
