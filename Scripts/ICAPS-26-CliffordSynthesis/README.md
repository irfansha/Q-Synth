# ICAPS-26: Optimal Clifford Synthesis as Planning

## Prerequisites

1. **Q-Synth** must be installed:
   ```bash
   pip install -e .
   ```

2. **Planners** must be built and exposed on your `PATH` under the exact
   executable names below — these are the names the experiment scripts invoke:

   | Planner (name in scripts) | Executable on `PATH` | Install from (git folder) |
   |---|---|---|
   | `madagascar` | `M`                | https://research.ics.aalto.fi/software/sat/madagascar/ |
   | `lama`       | `fast-downward.py` | https://github.com/aibasel/downward |
   | `scorpion`   | `scorpion.py`      | https://github.com/Martin1887/scp_merge_and_shrink |
   | `symk`       | `symk.py`          | https://github.com/speckdavid/symk |


   Clone and build (the Fast Downward-based planners build with `./build.py`):

   ```bash
   git clone https://github.com/aibasel/downward.git                 && (cd downward && ./build.py)
   git clone https://github.com/Martin1887/scp_merge_and_shrink.git  && (cd scp_merge_and_shrink && ./build.py)
   git clone https://github.com/speckdavid/symk.git                  && (cd symk && ./build.py)
   ```

   Expose them on `PATH` under the names the scripts expect (each Scorpion/SymK
   launcher is just its own repo's `fast-downward.py`):

   ```bash
   mkdir -p ~/planners-bin
   ln -s "$PWD/downward/fast-downward.py"             ~/planners-bin/fast-downward.py
   ln -s "$PWD/scp_merge_and_shrink/fast-downward.py" ~/planners-bin/scorpion.py
   ln -s "$PWD/symk/fast-downward.py"                 ~/planners-bin/symk.py
   export PATH="$HOME/planners-bin:$PATH"   # also put Madagascar's `M` here
   ```

## Experiments

### Experiment 1 (`run_experiment1.py`)

Random Clifford circuits (3–5 qubits, 15 instances).
Compares SAT-based cx-count minimization with planning-based normalform cx-count minimization.

- **SAT**: model=sat, metric=cx-count
- **Planning**: model=planning, encoding=normalform (auto-derived from metric=cx-count)
- **Planners**: madagascar, lama, scorpion, symk
- **Timeout**: 1800s

```bash
python run_experiment1.py
```

### Experiment 2a (`run_experiment2a.py`)

Random Clifford circuits (3–5 qubits, 15 instances).
Planning-based costbased encoding, minimizing both cx-count and 1q-count.

- **Planning**: model=planning, encoding=costbased (auto-derived from metric=cx-count_1q-count)
- **Planners**: lama, scorpion, symk
- **Timeout**: 1800s

```bash
python run_experiment2a.py
```

### Experiment 2b (`run_experiment2b.py`)

Random Clifford circuits SAT-synthesized from Experiment 1 (3–5 qubits).
Planning-based rigidcnot encoding, minimizing total gate-count.

- **Planning**: encoding=rigidcnot, metric=gate-count
- **Planners**: lama, scorpion, symk
- **Timeout**: 1800s
- **Input**: SAT-optimized circuits from Experiment 1 placed in `Benchmarks/Random-Clifford/sat_synthesized/`

```bash
python run_experiment2b.py
```

### Experiment 3 (`run_experiment3.py`)

QEC (Quantum Error Correction) circuits.
- **Part A**: SAT-based bounded optimization (cx-count_cx-depth and cx-depth_cx-count)
- **Part B**: Planning-based rigidcnot gate-count optimization on SAT-optimized QEC circuits

- **Planners** (Part B): symk, scorpion, lama
- **Timeout**: 10800s (3 hours)
- **Input (Part B)**: SAT-optimized QEC circuits placed in `Benchmarks/QECC/sat_optimized/`

```bash
python run_experiment3.py
```

## Benchmarks

- `Benchmarks/Random-Clifford/tket_optimized_without_swaps_no_u3_gates/` — Random Clifford circuits (Experiments 1, 2a)
- `Benchmarks/Random-Clifford/sat_synthesized/` — SAT-optimized outputs from Experiment 1 (Experiment 2b)
- `Benchmarks/QECC/` — QEC circuits (Experiment 3, Part A)
- `Benchmarks/QECC/sat_optimized/` — SAT-optimized QEC circuits (Experiment 3, Part B)

## Reference

Archived at: [Zenodo: 10.5281/zenodo.18678724](https://doi.org/10.5281/zenodo.18678724)
