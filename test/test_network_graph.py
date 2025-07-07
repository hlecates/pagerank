"""
Unit tests for the NetworkGraph data structure.
"""
import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))
from core.network_graph import NetworkGraph

def test_add_and_remove_nodes():
    g = NetworkGraph()
    g.add_node('A', type='station')
    g.add_node('B')
    assert set(g.nodes_list()) == {'A', 'B'}
    assert g.get_node_attrs('A')['type'] == 'station'
    g.remove_node('A')
    assert 'A' not in g.nodes_list()

def test_add_and_remove_edges():
    g = NetworkGraph()
    g.add_edge('A', 'B', weight=2.5, line='red')
    g.add_edge('B', 'C')
    assert g.get_neighbors('A') == ['B']
    assert g.get_edge_weight('A', 'B') == 2.5
    assert g.get_edge_attrs('A', 'B')['line'] == 'red'
    g.remove_edge('A', 'B')
    assert g.get_neighbors('A') == []

def test_adjacency_matrix():
    g = NetworkGraph()
    g.add_edge('A', 'B', weight=3.0)
    g.add_edge('B', 'C', weight=1.5)
    nodes, matrix = g.to_adjacency_matrix()
    idx = {node: i for i, node in enumerate(nodes)}
    assert matrix[idx['A']][idx['B']] == 3.0
    assert matrix[idx['B']][idx['C']] == 1.5
    assert matrix[idx['A']][idx['C']] == 0.0

def test_adjacency_binary_matrix():
    g = NetworkGraph()
    g.add_edge('A', 'B')
    g.add_edge('B', 'C')
    nodes, matrix = g.to_adjacency_binary_matrix()
    idx = {node: i for i, node in enumerate(nodes)}
    assert matrix[idx['A']][idx['B']] == 1
    assert matrix[idx['B']][idx['C']] == 1
    assert matrix[idx['A']][idx['C']] == 0

def test_edge_and_node_attributes():
    g = NetworkGraph()
    g.add_node('X', zone='north')
    g.add_edge('X', 'Y', weight=4.2, capacity=100)
    assert g.get_node_attrs('X')['zone'] == 'north'
    assert g.get_edge_attrs('X', 'Y')['capacity'] == 100
    assert g.get_edge_weight('X', 'Y') == 4.2 