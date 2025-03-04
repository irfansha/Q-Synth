# (C) CC-BY Irfansha Shaik, Jaco van de Pol, Aarhus University, 2023

# from qiskit.providers.fake_provider import FakeTokyo
# from qiskit.providers.fake_provider import FakeTenerife
# from qiskit.providers.fake_provider import FakeMelbourne

from qiskit_ibm_runtime.fake_provider import (
    FakeMelbourneV2,
)
import rustworkx as rx


def platform(platform, bidirectional, coupling_graph, verbose=0):

    # Platforms known in qiskit
    if platform in ("melbournev2",):
        if platform == "melbournev2":
            arch = FakeMelbourneV2()
        num_physical_qubits = arch.configuration().n_qubits
        coupling_map = arch.configuration().coupling_map
        if verbose > 0:
            print("provider from qiskit: ", arch.configuration().backend_name)

    # Some other well-known quantum architectures
    else:
        if platform == "rigetti-8":
            # square with legs
            num_physical_qubits = 8
            coupling_map = [
                [0, 4],
                [1, 5],
                [2, 6],
                [3, 7],
                [4, 5],
                [4, 6],
                [5, 7],
                [6, 7],
            ]
        elif platform == "rigetti-12":
            # octagon and an adjacent square with legs:
            num_physical_qubits = 12
            coupling_map = [
                [0, 1],
                [1, 2],
                [2, 3],
                [3, 4],
                [4, 5],
                [5, 6],
                [6, 7],
                [7, 0],
                [7, 8],
                [8, 9],
                [9, 0],
                [8, 10],
                [9, 11],
            ]
        elif platform == "rigetti-14":
            # 2 squares with legs connected diagonally with one edge:
            num_physical_qubits = 14
            coupling_map = [
                [0, 1],
                [1, 2],
                [2, 6],
                [3, 6],
                [1, 3],
                [0, 4],
                [0, 5],
                [4, 7],
                [5, 7],
                [2, 8],
                [6, 9],
                [3, 10],
                [4, 11],
                [7, 12],
                [5, 13],
            ]
        elif platform == "rigetti-16":
            # TODO: (not) 2 octagons connected by a square
            num_physical_qubits = 16
            coupling_map = [
                [0, 1],
                [1, 2],
                [2, 3],
                [3, 4],
                [4, 5],
                [5, 6],
                [6, 7],
                [0, 8],
                [3, 11],
                [4, 12],
                [7, 15],
                [8, 9],
                [9, 10],
                [10, 11],
                [11, 12],
                [12, 13],
                [13, 14],
                [14, 15],
            ]
        elif platform == "rigetti-80":
            num_physical_qubits = 80
            coupling_map = [
                [0, 1],
                [1, 2],
                [2, 3],
                [3, 4],
                [4, 5],
                [5, 6],
                [6, 7],
                [7, 0],
                [0, 13],
                [1, 12],
                [2, 47],
                [3, 46],
                [8, 9],
                [9, 10],
                [10, 11],
                [11, 12],
                [12, 13],
                [13, 14],
                [14, 15],
                [15, 8],
                [8, 21],
                [9, 20],
                [10, 55],
                [11, 54],
                [16, 17],
                [17, 18],
                [18, 19],
                [19, 20],
                [20, 21],
                [21, 22],
                [22, 23],
                [23, 16],
                [16, 29],
                [17, 28],
                [18, 63],
                [19, 62],
                [24, 25],
                [25, 26],
                [26, 27],
                [27, 28],
                [28, 29],
                [29, 30],
                [30, 31],
                [31, 24],
                [24, 37],
                [25, 36],
                [26, 71],
                [27, 70],
                [32, 33],
                [33, 34],
                [34, 35],
                [35, 36],
                [36, 37],
                [37, 38],
                [38, 39],
                [39, 32],
                [34, 79],
                [35, 78],
                [40, 41],
                [41, 42],
                [42, 43],
                [43, 44],
                [44, 45],
                [45, 46],
                [46, 47],
                [47, 40],
                [40, 53],
                [41, 52],
                [48, 49],
                [49, 50],
                [50, 51],
                [51, 52],
                [52, 53],
                [53, 54],
                [54, 55],
                [55, 48],
                [48, 61],
                [49, 60],
                [56, 57],
                [57, 58],
                [58, 59],
                [59, 60],
                [60, 61],
                [61, 62],
                [62, 63],
                [63, 56],
                [56, 69],
                [57, 68],
                [64, 65],
                [65, 66],
                [66, 67],
                [67, 68],
                [68, 69],
                [69, 70],
                [70, 71],
                [71, 64],
                [64, 77],
                [65, 76],
                [72, 73],
                [73, 74],
                [74, 75],
                [75, 76],
                [76, 77],
                [77, 78],
                [78, 79],
                [79, 72],
            ]
        elif platform == "sycamore":
            num_physical_qubits = 54
            coupling_map = [
                [0, 6],
                [1, 6],
                [1, 7],
                [2, 7],
                [2, 8],
                [3, 8],
                [3, 9],
                [4, 9],
                [4, 10],
                [5, 10],
                [5, 11],
                [6, 12],
                [6, 13],
                [7, 13],
                [7, 14],
                [8, 14],
                [8, 15],
                [9, 15],
                [9, 16],
                [10, 16],
                [10, 17],
                [11, 17],
                [12, 18],
                [13, 18],
                [13, 19],
                [14, 19],
                [14, 20],
                [15, 20],
                [15, 21],
                [16, 21],
                [16, 22],
                [17, 22],
                [17, 23],
                [18, 24],
                [18, 25],
                [19, 25],
                [19, 26],
                [20, 26],
                [20, 27],
                [21, 27],
                [21, 28],
                [22, 28],
                [22, 29],
                [23, 29],
                [24, 30],
                [25, 30],
                [25, 31],
                [26, 31],
                [26, 32],
                [27, 32],
                [27, 33],
                [28, 33],
                [28, 34],
                [29, 34],
                [29, 35],
                [30, 36],
                [30, 37],
                [31, 37],
                [31, 38],
                [32, 38],
                [32, 39],
                [33, 39],
                [33, 40],
                [34, 40],
                [34, 41],
                [35, 41],
                [36, 42],
                [37, 42],
                [37, 43],
                [38, 43],
                [38, 44],
                [39, 44],
                [39, 45],
                [40, 45],
                [40, 46],
                [41, 46],
                [41, 47],
                [42, 48],
                [42, 49],
                [43, 49],
                [43, 50],
                [44, 50],
                [44, 51],
                [45, 51],
                [45, 52],
                [46, 52],
                [46, 53],
                [47, 53],
            ]
        elif platform == "eagle":
            num_physical_qubits = 127
            coupling_map = [
                [0, 1],
                [1, 2],
                [2, 3],
                [3, 4],
                [4, 5],
                [5, 6],
                [6, 7],
                [7, 8],
                [8, 9],
                [9, 10],
                [10, 11],
                [11, 12],
                [12, 13],
                [0, 14],
                [14, 18],
                [4, 15],
                [15, 22],
                [8, 16],
                [16, 26],
                [12, 17],
                [17, 30],
                [18, 19],
                [19, 20],
                [20, 21],
                [21, 22],
                [22, 23],
                [23, 24],
                [24, 25],
                [25, 26],
                [26, 27],
                [27, 28],
                [28, 29],
                [29, 30],
                [30, 31],
                [31, 32],
                [20, 33],
                [33, 39],
                [24, 34],
                [34, 43],
                [28, 35],
                [35, 47],
                [32, 36],
                [36, 51],
                [37, 38],
                [38, 39],
                [39, 40],
                [40, 41],
                [41, 42],
                [42, 43],
                [43, 44],
                [44, 45],
                [45, 46],
                [46, 47],
                [47, 48],
                [48, 49],
                [49, 50],
                [50, 51],
                [37, 52],
                [52, 56],
                [41, 53],
                [53, 60],
                [45, 54],
                [54, 64],
                [49, 55],
                [55, 68],
                [56, 57],
                [57, 58],
                [58, 59],
                [59, 60],
                [60, 61],
                [61, 62],
                [62, 63],
                [63, 64],
                [64, 65],
                [65, 66],
                [66, 67],
                [67, 68],
                [68, 69],
                [69, 70],
                [58, 71],
                [71, 77],
                [62, 72],
                [72, 81],
                [66, 73],
                [73, 85],
                [70, 74],
                [74, 89],
                [75, 76],
                [76, 77],
                [77, 78],
                [78, 79],
                [79, 80],
                [80, 81],
                [81, 82],
                [82, 83],
                [83, 84],
                [84, 85],
                [85, 86],
                [86, 87],
                [87, 88],
                [88, 89],
                [75, 90],
                [90, 94],
                [79, 91],
                [91, 98],
                [83, 92],
                [92, 102],
                [87, 93],
                [93, 106],
                [94, 95],
                [95, 96],
                [96, 97],
                [97, 98],
                [98, 99],
                [99, 100],
                [100, 101],
                [101, 102],
                [102, 103],
                [103, 104],
                [104, 105],
                [105, 106],
                [106, 107],
                [107, 108],
                [96, 109],
                [109, 114],
                [100, 110],
                [110, 118],
                [104, 111],
                [111, 122],
                [108, 112],
                [112, 126],
                [113, 114],
                [114, 115],
                [115, 116],
                [116, 117],
                [117, 118],
                [118, 119],
                [119, 120],
                [120, 121],
                [121, 122],
                [122, 123],
                [123, 124],
                [124, 125],
                [125, 126],
            ]
        elif platform == "guadalupe":
            num_physical_qubits = 16
            coupling_map = [
                [0, 1],
                [1, 2],
                [2, 3],
                [3, 4],
                [4, 5],
                [5, 6],
                [6, 7],
                [7, 8],
                [8, 9],
                [9, 10],
                [10, 11],
                [11, 0],
                [12, 0],
                [13, 4],
                [14, 6],
                [15, 8],
            ]
        elif platform == "OCQ-tokyo":
            (num_physical_qubits, coupling_map) = remap_architecture(
                [  # qubit numbers below correspond to OCQ qubit identifiers
                    [4, 5],
                    [6, 5],
                    [7, 6],
                    [7, 16],
                    [17, 16],
                    [17, 25],
                    [26, 25],
                    [26, 35],
                    [34, 35],
                    [27, 24],
                    [27, 34],
                    [24, 23],
                    [23, 22],
                    [22, 18],
                    [22, 21],
                    [28, 21],
                    [28, 31],
                    [34, 33],
                    [32, 33],
                    [32, 31],
                    [30, 31],
                    [18, 14],
                    [14, 15],
                    [13, 14],
                    [12, 13],
                    [12, 9],
                    [2, 9],
                    [1, 2],
                    [1, 10],
                    [10, 11],
                    [19, 11],
                    [19, 20],
                ]
            )
        elif platform == "tokyo":
            num_physical_qubits = 20
            coupling_map = [
                [0, 1],
                [0, 5],
                [1, 0],
                [1, 2],
                [1, 6],
                [1, 7],
                [2, 1],
                [2, 6],
                [3, 8],
                [4, 8],
                [4, 9],
                [5, 0],
                [5, 6],
                [5, 10],
                [5, 11],
                [6, 1],
                [6, 2],
                [6, 5],
                [6, 7],
                [6, 10],
                [6, 11],
                [7, 1],
                [7, 6],
                [7, 8],
                [7, 12],
                [8, 3],
                [8, 4],
                [8, 7],
                [8, 9],
                [8, 12],
                [8, 13],
                [9, 4],
                [9, 8],
                [10, 5],
                [10, 6],
                [10, 11],
                [10, 15],
                [11, 5],
                [11, 6],
                [11, 10],
                [11, 12],
                [11, 16],
                [11, 17],
                [12, 7],
                [12, 8],
                [12, 11],
                [12, 13],
                [12, 16],
                [13, 8],
                [13, 12],
                [13, 14],
                [13, 18],
                [13, 19],
                [14, 13],
                [14, 18],
                [14, 19],
                [15, 10],
                [15, 16],
                [16, 11],
                [16, 12],
                [16, 15],
                [16, 17],
                [17, 11],
                [17, 16],
                [17, 18],
                [18, 13],
                [18, 14],
                [18, 17],
                [19, 13],
                [19, 14],
            ]
        elif platform == "tenerife":
            num_physical_qubits = 5
            coupling_map = [[1, 0], [2, 0], [2, 1], [3, 2], [3, 4], [4, 2]]
        elif platform == "melbourne":
            num_physical_qubits = 14
            coupling_map = [
                [1, 0],
                [1, 2],
                [2, 3],
                [4, 3],
                [4, 10],
                [5, 4],
                [5, 6],
                [5, 9],
                [6, 8],
                [7, 8],
                [9, 8],
                [9, 10],
                [11, 3],
                [11, 10],
                [11, 12],
                [12, 2],
                [13, 1],
                [13, 12],
            ]

        # generated parameterized platforms

        elif platform.startswith("line-"):
            # Line of <n> qubits:
            num_physical_qubits = int(platform.split("-")[-1])
            coupling_map = [[i, i + 1] for i in range(0, num_physical_qubits - 1)]
        elif platform.startswith("cycle-"):
            # Cycle of <n> qubits:
            num_physical_qubits = int(platform.split("-")[-1])
            coupling_map = [[i, i + 1] for i in range(0, num_physical_qubits - 1)]
            coupling_map.append([num_physical_qubits - 1, 0])
            print(coupling_map)
        elif platform.startswith("star-"):
            # Star with <n> legs + center:
            num_physical_qubits = 1 + int(platform.split("-")[-1])
            coupling_map = [[0, i] for i in range(1, num_physical_qubits)]
        elif platform.startswith("grid-"):
            grid_size = int(platform.split("-")[-1])
            num_physical_qubits = grid_size * grid_size
            coupling_map = []
            # Grids same as in OLSQ2:
            for i in range(grid_size):
                for j in range(grid_size):
                    if j < grid_size - 1:
                        coupling_map.append([i * grid_size + j, i * grid_size + j + 1])
                    if i < grid_size - 1:
                        coupling_map.append(
                            [i * grid_size + j, i * grid_size + j + grid_size]
                        )
        elif platform == "test":  # change this to your own purpose...
            num_physical_qubits = 6
            coupling_map = [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0], [1, 4]]
        elif platform == "custom":
            import itertools

            # We assume the physical qubits start from 0
            num_physical_qubits = max(itertools.chain.from_iterable(coupling_graph)) + 1
            coupling_map = coupling_graph
        else:
            print(f"Platform {platform} is not recognized")
            exit(-1)
        if verbose > 0:
            print(f"platform generated: {platform}")

    if verbose > 0:
        print("number of physical qubits: ", num_physical_qubits)

    # if bidirectional flag is on, we make everything bidirectional:
    if bidirectional > 0:
        extra_connections = []

        for [x1, x2] in coupling_map:
            if [x2, x1] not in coupling_map:
                if [x2, x1] not in extra_connections:
                    extra_connections.append([x2, x1])

        # adding the extra connections:
        bi_coupling_map = coupling_map + extra_connections
    else:
        bi_coupling_map = coupling_map[:]

    # for bridges, we compute physical qubits at 2 distance:
    graph = rx.PyGraph()
    bi_coupling_tuples = []
    for [x1, x2] in bi_coupling_map:
        bi_coupling_tuples.append((x1, x2))
    graph.add_nodes_from(range(0, num_physical_qubits))
    graph.add_edges_from_no_data(bi_coupling_tuples)
    # cost of an edge is 1:
    distance_dict = rx.distance_matrix(graph)

    # reverse distance dictionary:
    reverse_swap_distance_dict = {}
    for i in range(num_physical_qubits):
        for j in range(i + 1, num_physical_qubits):
            distance = int(distance_dict[i][j])
            swap_distance = distance - 1
            if swap_distance not in reverse_swap_distance_dict:
                reverse_swap_distance_dict[swap_distance] = [(i, j)]
            else:
                reverse_swap_distance_dict[swap_distance].append((i, j))

    bridge_coupling_map = []
    bridge_bicoupling_map = []
    # if distance is 2 then they are bridge pairs:
    for i in range(num_physical_qubits):
        for j in range(i + 1, num_physical_qubits):
            if distance_dict[i][j] == 2:
                bridge_coupling_map.append([i, j])
                # we use append both combinations:
                bridge_bicoupling_map.append([i, j])
                bridge_bicoupling_map.append([j, i])

    bridge_middle_pqubit_dict = {}
    # generating intermediate physical qubits for bridge qubit pairs:
    for [i, j] in bridge_coupling_map:
        cur_middle_pqubits = []
        for k in range(num_physical_qubits):
            if distance_dict[i, k] == 1 and distance_dict[j, k] == 1:
                cur_middle_pqubits.append(k)
        bridge_middle_pqubit_dict[(i, j)] = cur_middle_pqubits

    if verbose > 1:
        print("coupling map: ", coupling_map)
        print("bicoupling map: ", bi_coupling_map)
        print("bridge bicoupling map: ", bridge_bicoupling_map)
        print("bridge middle pqubit dict: ", bridge_middle_pqubit_dict)
        print("distance matrix:", distance_dict)
        print("reverse swap distance dict:", reverse_swap_distance_dict)

    # TODO: should only compute and return the maps that are actually needed
    # (maybe provide auxiliary functions to obtain derived maps)
    return (
        coupling_map,
        bi_coupling_map,
        bridge_bicoupling_map,
        bridge_middle_pqubit_dict,
        reverse_swap_distance_dict,
        num_physical_qubits,
    )


# This function can be used to renumber qubits consecutively from 0..n-1, see OCQ-tokyo for an example.
# TODO: later, we could store/reuse the qubits-dictionary to print the proper qubit names


def remap_architecture(coupling):
    qubits = dict()
    next = 0
    result = []
    for [i, j] in coupling:
        if i not in qubits:
            qubits[i] = next
            next += 1
        if j not in qubits:
            qubits[j] = next
            next += 1
        result.append([qubits[i], qubits[j]])
    return (next, result)
