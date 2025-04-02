# Irfansha Shaik, 14.02.2024, Aarhus
import argparse


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="given an optimized qasm file from t-par, we standardize the format for qiskit parsing"
    )
    parser.add_argument("--circuit", help="input circuit in qasm format")
    args = parser.parse_args()

    with open(args.circuit, "r") as f:
        lines = f.readlines()

    for line_id in range(len(lines)):
        line = lines[line_id]
        line = line.strip("\n").strip(" ")
        if line_id <= 1:
            print(line)
        elif line_id == 2:
            qubits_str = line.strip("{").strip(" ").split(" ")[-1]
            qubits = {}
            count = 0
            for qubit in qubits_str.split(","):
                qubits[qubit] = count
                count += 1
            # we extract all the qubits used and map to integers:
            print(f"qreg q[{count}];")
        elif line == "}":
            continue
        else:
            gate_name, parameters = line.strip(";").split(" ")
            split_parameters = parameters.split(",")
            new_parameter_list = []
            for parameter in split_parameters:
                new_parameter_list.append(f"q[{qubits[parameter]}]")

            print(f"{gate_name} {','.join(new_parameter_list)};")
