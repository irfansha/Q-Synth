# (C) CC-BY Irfansha Shaik, Jaco van de Pol, Aarhus University, 2023

from qiskit.providers.fake_provider import FakeTokyo
from qiskit.providers.fake_provider import FakeTenerife
from qiskit.providers.fake_provider import FakeMelbourne

def platform(platform, bidirectional, debug=0):
    if platform in ("tenerife","melbourne","tokyo"):
      if platform == "tokyo":
        arch = FakeTokyo()
      elif platform == "tenerife":
        arch = FakeTenerife()
      elif platform == "melbourne":
        arch = FakeMelbourne()
      num_physical_qubits = arch.configuration().n_qubits
      coupling_map = arch.configuration().coupling_map
      if debug > 0:
        print("provider from qiskit: ",arch.configuration().backend_name)
    else:
      if platform == "rigetti-12":
        # octagon and an adjacent square with legs:
        num_physical_qubits = 12
        coupling_map = [[0,1],[1,2],[2,3],[3,4],[4,5],[5,6],[6,7],[7,0],[7,8],[8,9],[9,0],[8,10],[9,11]]
      elif platform == "rigetti-14":
        # 2 squares with legs connected diagonally with one edge:
        num_physical_qubits = 14
        coupling_map = [[0, 1], [1, 2], [2, 6], [3, 6], [1,3], [0, 4], [0, 5], [4, 7], [5, 7],[2,8],[6,9],[3,10],[4,11],[7,12],[5,13]]
      elif platform == "star-3":
        # Star with 3 legs + center:
        num_physical_qubits = 4
        coupling_map = [[0,1],[0,2],[0,3]]
      elif platform == "star-7":
        # Star with 7 legs + center:
        num_physical_qubits = 8
        coupling_map = [[0,1],[0,2],[0,3],[0,4],[0,5],[0,6],[0,7]]
      elif platform == "cycle-5":
        # Cycle of 5 qubits:
        num_physical_qubits = 5
        coupling_map = [(0,1),(1,2),(2,3),(3,4),(4,0)]
      elif platform == "test": # change this to your own purpose...
        num_physical_qubits = 5
        coupling_map = [(0,1),(1,2),(2,3),(3,4),(4,0)]
      else:
        print(f"Platform {platform} is not recognized")
        exit(-1)
      if debug > 0:
        print(f"platform generated: {platform}")

    if debug > 0:
      print("number of physical qubits: ", num_physical_qubits)

    # if bidirectional flag is on, we make everything bidirectional:
    if bidirectional == 1:
      extra_connections = []
    
      for [x1,x2] in coupling_map:
        if [x2,x1] not in coupling_map:
          if [x2,x1] not in extra_connections:
            extra_connections.append([x2,x1])

      # adding the extra connections:
      coupling_map.extend(extra_connections)

    if debug > 1:
      print("coupling map: ", coupling_map)


    return (coupling_map, num_physical_qubits)