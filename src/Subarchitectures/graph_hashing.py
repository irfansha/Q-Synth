#!/usr/bin/env python3
from collections import Counter, defaultdict
from hashlib import blake2b
import rustworkx as rx

"""
Adapted to rustworkx with simplifications from implementation of networkx library:
https://networkx.org/documentation/stable/_modules/networkx/algorithms/graph_hashing.html#weisfeiler_lehman_graph_hash
"""


def _hash_label(label, digest_size):
    return blake2b(label.encode("ascii"), digest_size=digest_size).hexdigest()


def _init_node_labels(G):
    # Removed options for node_attributes and edge_attributes
    return {i: str(G.degree(i)) for i in G.node_indices()}


def _neighborhood_aggregate(G, node, node_labels):
    """
    Compute new labels for given node by aggregating
    the labels of each node's neighbors.
    """
    # Removed options for edge_attributes
    label_list = []
    for nbr in G.neighbors(node):
        label_list.append(node_labels[nbr])
    return node_labels[node] + "".join(sorted(label_list))


def weisfeiler_lehman_graph_hash(G, iterations=3, digest_size=16):
    # Removed options for node_attributes and edge_attributes
    def weisfeiler_lehman_step(G, labels):
        """
        Apply neighborhood aggregation to each node
        in the graph.
        Computes a dictionary with labels for each node.
        """
        new_labels = {}
        for node in G.node_indices():
            label = _neighborhood_aggregate(G, node, labels)
            new_labels[node] = _hash_label(label, digest_size)
        return new_labels

    # set initial node labels
    node_labels = _init_node_labels(G)

    subgraph_hash_counts = []
    for _ in range(iterations):
        node_labels = weisfeiler_lehman_step(G, node_labels)
        counter = Counter(node_labels.values())
        # sort the counter, extend total counts
        subgraph_hash_counts.extend(sorted(counter.items(), key=lambda x: x[0]))

    # hash the final counter
    return _hash_label(str(tuple(subgraph_hash_counts)), digest_size)
