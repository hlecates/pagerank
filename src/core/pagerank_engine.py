import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class PageRankConfig:
    damping_factor: float = 0.85
    convergence_threshold: float = 1e-10
    max_iterations: int = 100
    teleport_probability: float = 0.15


class PageRankEngine:
    def __init__(self, config: Optional[PageRankConfig] = None):
        self.config = config or PageRankConfig()
        
    def create_transition_matrix(self, adjacency_matrix: np.ndarray) -> np.ndarray:
        n = adjacency_matrix.shape[0]
        transition_matrix = np.zeros((n, n))
        
        for i in range(n):
            out_degree = np.sum(adjacency_matrix[i, :])
            if out_degree > 0:
                transition_matrix[i, :] = adjacency_matrix[i, :] / out_degree
            else:
                transition_matrix[i, :] = 1.0 / n
                
        return transition_matrix
    
    def calculate_pagerank(self, adjacency_matrix: np.ndarray) -> np.ndarray:
        n = adjacency_matrix.shape[0]
        
        transition_matrix = self.create_transition_matrix(adjacency_matrix)
        
        pagerank_scores = np.ones(n) / n
        
        for iteration in range(self.config.max_iterations):
            previous_scores = pagerank_scores.copy()
            
            pagerank_scores = (
                (1 - self.config.damping_factor) * np.ones(n) / n +
                self.config.damping_factor * transition_matrix.T @ pagerank_scores
            )
            
            if np.linalg.norm(pagerank_scores - previous_scores) < self.config.convergence_threshold:
                break
                
        return pagerank_scores
    
    def calculate_pagerank_with_weights(self, adjacency_matrix: np.ndarray, 
                                      weights: np.ndarray) -> np.ndarray:
        n = adjacency_matrix.shape[0]
        
        transition_matrix = np.zeros((n, n))
        
        for i in range(n):
            total_weight = np.sum(weights[i, :] * adjacency_matrix[i, :])
            if total_weight > 0:
                transition_matrix[i, :] = (weights[i, :] * adjacency_matrix[i, :]) / total_weight
            else:
                transition_matrix[i, :] = 1.0 / n
                
        pagerank_scores = np.ones(n) / n
        
        for iteration in range(self.config.max_iterations):
            previous_scores = pagerank_scores.copy()
            
            pagerank_scores = (
                (1 - self.config.damping_factor) * np.ones(n) / n +
                self.config.damping_factor * transition_matrix.T @ pagerank_scores
            )
            
            if np.linalg.norm(pagerank_scores - previous_scores) < self.config.convergence_threshold:
                break
                
        return pagerank_scores
    
    def get_top_nodes(self, pagerank_scores: np.ndarray, top_k: int = 10) -> List[Tuple[int, float]]:
        node_scores = [(i, score) for i, score in enumerate(pagerank_scores)]
        node_scores.sort(key=lambda x: x[1], reverse=True)
        return node_scores[:top_k]
    
    def normalize_scores(self, pagerank_scores: np.ndarray) -> np.ndarray:
        total_score = np.sum(pagerank_scores)
        if total_score > 0:
            return pagerank_scores / total_score
        return pagerank_scores
    
    def validate_adjacency_matrix(self, adjacency_matrix: np.ndarray) -> bool:
        if adjacency_matrix.ndim != 2:
            return False
        if adjacency_matrix.shape[0] != adjacency_matrix.shape[1]:
            return False
        if not np.all((adjacency_matrix == 0) | (adjacency_matrix == 1)):
            return False
        return True


def create_sample_network() -> Tuple[np.ndarray, np.ndarray]:
    adjacency_matrix = np.array([
        [0, 1, 1, 1, 1],
        [1, 0, 0, 0, 0],
        [1, 0, 0, 0, 0],
        [1, 0, 0, 0, 0],
        [1, 0, 0, 0, 0]
    ])
    
    weights_matrix = np.array([
        [0, 10, 15, 12, 8],
        [10, 0, 0, 0, 0],
        [15, 0, 0, 0, 0],
        [12, 0, 0, 0, 0],
        [8, 0, 0, 0, 0]
    ])
    
    return adjacency_matrix, weights_matrix 