import rustworkx as rx

from typing import TypeVar, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

import qsynth.Subarchitectures.graph_hashing as gh


T = TypeVar("T")


# Wrapper for performing memoization
def init_memoization(body: Callable) -> Callable:

    # Memoization dictionary
    mem = {}

    # Memoization wrapper
    def wrapper(*args):
        if args in mem.keys():
            return mem[args]
        else:
            res = body(*args)
            mem[args] = res
            return res

    # Return wrapper
    return wrapper


# Helper definition for simple tree purposes
@dataclass
class TreeNode:
    ident: int
    children: list["TreeNode"] = field(default_factory=list)


# Helper definitions for advanced tree processing
class Mark(Enum):
    NONE = 0
    NEW = 1
    VISITED = 2
    SEEN = 3


@dataclass
class ExtTreeNode:
    ident: int
    idx: int
    children: list[int] = field(default_factory=list)
    mark: Mark = Mark.NONE


def tree_paths(root: TreeNode, path: list[TreeNode]) -> list[list[TreeNode]]:
    """
    Extract all paths of a tree given by root node.
    """

    # Base-case
    if len(root.children) == 0:
        return [path]

    # Compute all continuing paths
    paths: list[list[TreeNode]] = []
    for child in root.children:
        cpath = path.copy()
        cpath.append(child)
        paths += tree_paths(child, cpath)

    # Return found paths
    return paths


def k_combinations(k: int, S: list[T]) -> list[list[T]]:
    """
    Extract all combinations of k elements from set S.
    """
    from itertools import combinations

    return combinations(S, k)


def k_compositions(k: int, S: int) -> list[list[int]]:
    """
    Construct all compositions of k numbers which sum to S.
    """

    def k_sum_rec(k: int, S: int) -> list[TreeNode]:

        # Base-cases
        if k == 1:
            return [TreeNode(S)]

        # Compositions that include number x
        nodes: list[TreeNode] = []
        for x in range(1, S - k + 2):
            node = TreeNode(x)
            node.children = k_sum_rec(k - 1, S - x)
            nodes.append(node)

        return nodes

    # Base-case
    if k == 0:
        raise Exception(f"Invalid argument: {k}")

    # Construct a tree of compositions
    root = TreeNode(None)
    root.children = k_sum_rec(k, S)

    # Extract all compositions from tree
    compositions: list[list[int]] = []
    for path in tree_paths(root, []):
        compositions.append(list(map(lambda n: n.ident, path)))
    return compositions


def make_memoized_refined_union_product(nodemap: dict[int, ExtTreeNode]) -> Callable:
    """
    Constructs a memoized version of the refined union product
    as suggested by Karakashian et. al.
    Requires supplying a nodemap for an existing combination tree.
    """

    # Defining oracles for constraints
    def oracle_vertex_disjoint(s1: tuple[int], s2: tuple[int]) -> bool:
        v1 = map(lambda i: nodemap[i].idx, s1)
        v2 = map(lambda i: nodemap[i].idx, s2)
        return set(v1).isdisjoint(set(v2))

    def oracle_hasmark_new(s1: tuple[int]) -> bool:
        return any(m == Mark.NEW for m in map(lambda i: nodemap[i].mark, s1))

    def oracle_nochildren_of(s1: tuple[int], s2: tuple[int]) -> bool:
        c1 = sum(list(map(lambda i: nodemap[i].children, s1)), [])
        v1 = map(lambda i: nodemap[i.ident].idx, c1)
        v2 = map(lambda i: nodemap[i].idx, s2)
        return set(v1).isdisjoint(set(v2))

    def oracle_hasmark_new_or_nochildren_of(s1: tuple[int], s2: tuple[int]) -> bool:
        return oracle_hasmark_new(s2) or oracle_nochildren_of(s1, s2)

    # Inner implementation of refined union product
    def ref_union_prod(sets: tuple[tuple[tuple[int]]]):
        import constraint as cst

        problem = cst.Problem()

        # Each variable corresponds to choosing an element from each set
        max_idx = None
        for idx, values in enumerate(sets):

            # Only add if set is non-empty
            if len(values) == 0:
                break

            problem.addVariable(idx, values)
            max_idx = idx

        # When all sets are empty
        if max_idx is None:
            return []
        # When only first set is non-empty
        if max_idx == 0:
            return sets[0]

        # Model all constraints between every pair of subsequent sets
        for idx in range(max_idx + 1):
            for jdx in range(idx + 1, min(max_idx + 1, len(sets))):

                problem.addConstraint(oracle_vertex_disjoint, (idx, jdx))
                problem.addConstraint(oracle_hasmark_new_or_nochildren_of, (idx, jdx))

        # Merge solutions into result
        solutions = []
        for solution in problem.getSolutionIter():
            solutions.append(sum(map(list, solution.values()), []))

        # Return tuple[tuple[int]]
        return tuple(map(tuple, solutions))

    # Memoization dictionary
    memo = dict()

    # Memoized wrapper around inner implementation
    def memoized(sets: tuple[tuple[tuple[int]]]):

        if sets in memo.keys():
            return memo[sets]
        else:
            res = ref_union_prod(sets)
            memo[sets] = res
            return res

    return memoized


def combinations_from_tree(
    root: ExtTreeNode,
    size: int,
    ref_union_prod: Callable,
    k_comp: Callable = k_compositions,
) -> tuple[tuple[int]]:
    """
    Extracts all combinations from a combination tree given by root node
    using an implementation of refined union product.
    """

    # Set of combinations of tree nodes (their node id's)
    node_combinations: list[tuple[int]] = []

    # Base-case
    if size == 1:
        return ((root.ident,),)

    # Try all possible combinations of subtrees from root
    for n_nodes in range(1, min(len(root.children), size - 1) + 1):

        # Try every combination of child nodes as new root
        for comb in k_combinations(n_nodes, root.children):

            # Try every subtree-combination of depth size-1
            for comp in k_comp(n_nodes, size - 1):

                # Initialize vars
                fail = False

                # Results of the recursive calls to be combined into one
                rec_res: list[tuple[tuple[int]]] = [() for _ in range(n_nodes)]

                # Perform recursive call for each child
                for i in range(n_nodes):
                    subtree_root: ExtTreeNode = comb[i]
                    subtree_size: int = comp[i]
                    rec_res[i] = combinations_from_tree(
                        subtree_root, subtree_size, ref_union_prod, k_comp
                    )

                    # If no combinations found, then instance failed
                    if len(rec_res[i]) == 0:
                        fail = True
                        break

                # Skip failed instance
                if fail:
                    continue

                # Combine recursive results
                combined = ref_union_prod(tuple(rec_res))
                for combination in combined:
                    node_combinations.append((root.ident,) + combination)

    # Return found node combinations
    return tuple(node_combinations)


def root_subgraphs_idx(G: rx.PyGraph, size: int, root_idx: int) -> list[tuple[int]]:
    """
    Computes all subgraphs of a certain size,
    which include node given by root_idx.
    """

    # List for memorizing visited vertices
    vertex_list: list[list[int]] = [[] for _ in range(size + 1)]

    # Dictionary for memorizing marks of vertices
    vertex_marks = defaultdict(lambda: Mark.NONE)

    # Dictionary for mapping ids to nodes
    nodemap: dict[int, ExtTreeNode] = {}

    # Build the combination tree
    def build_tree(root: ExtTreeNode, depth: int, G: rx.PyGraph, max_depth: int):

        # Update vertex_list
        vertex_list[depth] = vertex_list[depth - 1].copy()

        # Examine each neighbor vertex
        for v in G.neighbors(root.idx):

            # Skip all ancestors, siblings or siblings of ancestors
            if v in vertex_list[depth]:
                continue

            # Add child
            node_id: int = len(nodemap)
            node = ExtTreeNode(node_id, v)
            nodemap[node_id] = node
            root.children.append(node)
            vertex_list[depth].append(v)

            # Manage marks
            if vertex_marks[v] != Mark.VISITED:
                node.mark = Mark.NEW
                vertex_marks[v] = Mark.VISITED
            else:
                node.mark = Mark.SEEN

            # If maximum depth not reached, call recursively
            if depth + 1 <= max_depth:
                build_tree(node, depth + 1, G, max_depth)

        return

    # Build the tree using root_idx node as root
    vertex_list[0].append(root_idx)
    root = ExtTreeNode(0, root_idx)
    nodemap[0] = root
    build_tree(root, 1, G, size)

    # Construct memoized refined union product
    ref_union_prod = make_memoized_refined_union_product(nodemap)

    # Construct memoized k-compositions
    k_comp = init_memoization(k_compositions)

    # Extract combinations from tree
    combinations: tuple[tuple[int]] = combinations_from_tree(
        root, size, ref_union_prod, k_comp
    )

    # Convert into vertex ids
    vertex_idx = []
    for combination in combinations:
        vertex_idx.append(tuple(map(lambda i: nodemap[i].idx, combination)))
    return vertex_idx


def connected_subarchitectures(G: rx.PyGraph, size: int) -> list[rx.PyGraph]:
    """
    Efficient algorithm based on Karakashian et. al.
    """
    subarchitectures = []
    G = G.copy()
    while len(G.nodes()) >= size:

        # Choosing node 0 as root node
        # compute all subgraphs starting with root
        root_idx = G.node_indices()[0]
        rsgraphs = root_subgraphs_idx(G, size, root_idx)
        for sg in rsgraphs:
            subgraph = G.subgraph(sg).copy()
            subarchitectures.append(subgraph)

        # Remove root node from graph
        G.remove_node(root_idx)

    # Return the final set of subarchitectures
    return subarchitectures


# def eliminate_isomorphism_hash(candidates: list[rx.PyGraph]) -> list[rx.PyGraph]:
#     """
#     Use graph-hashing to efficiently eliminate isomorphic copies.
#     """
#     fcand = dict()
#     for cand in enumerate(candidates):
#         h = gh.weisfeiler_lehman_graph_hash(cand, iterations=8)
#         if h not in fcand.keys():
#             fcand[h] = cand
#     return fcand.values()


def eliminate_isomorphism_hybrid(candidates: list[rx.PyGraph]) -> list[rx.PyGraph]:
    """
    Hybrid approach which guarantees correctness by supplementing
    hashing-based approach with VF2 isomorphism checks.
    """
    fcand: dict[str, list] = dict()
    for cand in candidates:

        # Check using graph-hashing
        h = gh.weisfeiler_lehman_graph_hash(cand, iterations=3)
        if h not in fcand.keys():
            fcand[h] = [cand]
        else:

            # Use VF2 algorithm against every graph with same hash
            is_cand = True
            for other in fcand[h]:
                if rx.is_isomorphic(cand, other, id_order=False):
                    is_cand = False
                    break

            # If no isomorphisms found, add to list
            if is_cand:
                fcand[h].append(cand)

    # Compile final list of candidates
    return sum(fcand.values(), [])


# def eliminate_isomorphism(candidates: list[rx.PyGraph]) -> list[rx.PyGraph]:
#     """
#     No graph-hashing implementation currently exists in rustworkx.
#     Therefore we use naive N^2 isomorphism checking.
#     """
#     fcand = []
#     for i, cand in enumerate(candidates):
#         is_cand = True
#         for other in candidates[i + 1 :]:
#             if rx.is_isomorphic(cand, other, id_order=False):
#                 is_cand = False
#                 break
#         if is_cand:
#             fcand.append(cand)
#     return fcand


def maximal_subarchitectures(candidates: list[rx.PyGraph]) -> list[rx.PyGraph]:
    """
    Use subgraph-isomorphism checking.
    """
    fcand = []
    for cand in candidates:
        is_cand = True
        for other in candidates:
            if cand == other:
                continue
            if rx.is_subgraph_isomorphic(other, cand, induced=False):
                is_cand = False
                break
        if is_cand:
            fcand.append(cand)
    return fcand
