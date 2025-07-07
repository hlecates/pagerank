"""
Unit tests for the core PageRank engine.

Tests the basic PageRank algorithm implementation with standard parameters.
"""

import pytest
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))
from core.pagerank_engine import PageRankEngine, PageRankConfig, create_sample_network


class TestPageRankConfig:
    """Test PageRank configuration class."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = PageRankConfig()
        assert config.damping_factor == 0.85
        assert config.convergence_threshold == 1e-10
        assert config.max_iterations == 100
        assert config.teleport_probability == 0.15
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = PageRankConfig(
            damping_factor=0.9,
            convergence_threshold=1e-8,
            max_iterations=50,
            teleport_probability=0.1
        )
        assert config.damping_factor == 0.9
        assert config.convergence_threshold == 1e-8
        assert config.max_iterations == 50
        assert config.teleport_probability == 0.1


class TestPageRankEngine:
    """Test the core PageRank engine."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.engine = PageRankEngine()
        self.sample_adjacency, self.sample_weights = create_sample_network()
    
    def test_engine_initialization(self):
        """Test engine initialization with default config."""
        engine = PageRankEngine()
        assert engine.config.damping_factor == 0.85
        assert engine.config.convergence_threshold == 1e-10
    
    def test_engine_initialization_with_config(self):
        """Test engine initialization with custom config."""
        config = PageRankConfig(damping_factor=0.9, max_iterations=50)
        engine = PageRankEngine(config)
        assert engine.config.damping_factor == 0.9
        assert engine.config.max_iterations == 50
    
    def test_create_transition_matrix(self):
        """Test transition matrix creation."""
        # Simple 3-node network: 0 -> 1 -> 2
        adjacency = np.array([
            [0, 1, 0],
            [0, 0, 1],
            [0, 0, 0]
        ])
        
        transition_matrix = self.engine.create_transition_matrix(adjacency)
        
        # Expected: node 0 has out-degree 1, node 1 has out-degree 1, node 2 has out-degree 0
        expected = np.array([
            [0, 1, 0],
            [0, 0, 1],
            [1/3, 1/3, 1/3]  # Dangling node gets uniform distribution
        ])
        
        np.testing.assert_array_almost_equal(transition_matrix, expected)
    
    def test_calculate_pagerank_simple_network(self):
        """Test PageRank calculation on a simple network."""
        # Simple 3-node network: 0 -> 1 -> 2
        adjacency = np.array([
            [0, 1, 0],
            [0, 0, 1],
            [0, 0, 0]
        ])
        
        pagerank_scores = self.engine.calculate_pagerank(adjacency)
        
        # All scores should be positive and sum to 1
        assert np.all(pagerank_scores > 0)
        assert np.abs(np.sum(pagerank_scores) - 1.0) < 1e-10
        
        # Node 1 should have higher score than node 0 (due to incoming edge)
        assert pagerank_scores[1] > pagerank_scores[0]
    
    def test_calculate_pagerank_sample_network(self):
        """Test PageRank calculation on the sample transportation network."""
        pagerank_scores = self.engine.calculate_pagerank(self.sample_adjacency)
        
        # All scores should be positive and sum to 1
        assert np.all(pagerank_scores > 0)
        assert np.abs(np.sum(pagerank_scores) - 1.0) < 1e-10
        
        # Central station (node 0) should have highest score (hub)
        assert pagerank_scores[0] == max(pagerank_scores)
    
    def test_calculate_pagerank_with_weights(self):
        """Test PageRank calculation with weighted edges."""
        pagerank_scores = self.engine.calculate_pagerank_with_weights(
            self.sample_adjacency, self.sample_weights
        )
        
        # All scores should be positive and sum to 1
        assert np.all(pagerank_scores > 0)
        assert np.abs(np.sum(pagerank_scores) - 1.0) < 1e-10
        
        # Central station should still have highest score
        assert pagerank_scores[0] == max(pagerank_scores)
    
    def test_get_top_nodes(self):
        """Test getting top-k nodes by PageRank score."""
        pagerank_scores = np.array([0.1, 0.5, 0.3, 0.05, 0.05])
        
        top_nodes = self.engine.get_top_nodes(pagerank_scores, top_k=3)
        
        assert len(top_nodes) == 3
        assert top_nodes[0][0] == 1  # Node 1 has highest score (0.5)
        assert top_nodes[0][1] == 0.5
        assert top_nodes[1][0] == 2  # Node 2 has second highest score (0.3)
        assert top_nodes[1][1] == 0.3
        assert top_nodes[2][0] == 0  # Node 0 has third highest score (0.1)
        assert top_nodes[2][1] == 0.1
    
    def test_normalize_scores(self):
        """Test score normalization."""
        scores = np.array([1.0, 2.0, 3.0, 4.0])
        normalized = self.engine.normalize_scores(scores)
        
        # Should sum to 1
        assert np.abs(np.sum(normalized) - 1.0) < 1e-10
        
        # Should maintain relative proportions
        assert normalized[3] == max(normalized)  # 4.0 becomes highest
        assert normalized[0] == min(normalized)  # 1.0 becomes lowest
    
    def test_normalize_scores_zero_sum(self):
        """Test normalization when scores sum to zero."""
        scores = np.array([0.0, 0.0, 0.0])
        normalized = self.engine.normalize_scores(scores)
        
        # Should return original scores unchanged
        np.testing.assert_array_equal(normalized, scores)
    
    def test_validate_adjacency_matrix_valid(self):
        """Test adjacency matrix validation with valid matrix."""
        valid_matrix = np.array([
            [0, 1, 0],
            [1, 0, 1],
            [0, 1, 0]
        ])
        
        assert self.engine.validate_adjacency_matrix(valid_matrix) is True
    
    def test_validate_adjacency_matrix_invalid_dimensions(self):
        """Test adjacency matrix validation with invalid dimensions."""
        invalid_matrix = np.array([
            [0, 1],
            [1, 0],
            [0, 1]
        ])
        
        assert self.engine.validate_adjacency_matrix(invalid_matrix) is False
    
    def test_validate_adjacency_matrix_invalid_values(self):
        """Test adjacency matrix validation with invalid values."""
        invalid_matrix = np.array([
            [0, 1, 0.5],
            [1, 0, 1],
            [0, 1, 0]
        ])
        
        assert self.engine.validate_adjacency_matrix(invalid_matrix) is False
    
    def test_convergence_behavior(self):
        """Test that PageRank converges within reasonable iterations."""
        # Create a larger network to test convergence
        n = 10
        adjacency = np.random.randint(0, 2, (n, n))
        np.fill_diagonal(adjacency, 0)  # No self-loops
        
        pagerank_scores = self.engine.calculate_pagerank(adjacency)
        
        # Should converge and produce valid scores
        assert np.all(pagerank_scores > 0)
        assert np.abs(np.sum(pagerank_scores) - 1.0) < 1e-10
    
    def test_damping_factor_effect(self):
        """Test that different damping factors produce different results."""
        config_low = PageRankConfig(damping_factor=0.5)
        config_high = PageRankConfig(damping_factor=0.95)
        
        engine_low = PageRankEngine(config_low)
        engine_high = PageRankEngine(config_high)
        
        pagerank_low = engine_low.calculate_pagerank(self.sample_adjacency)
        pagerank_high = engine_high.calculate_pagerank(self.sample_adjacency)
        
        # Results should be different
        assert not np.allclose(pagerank_low, pagerank_high)
        
        # Both should still be valid probability distributions
        assert np.abs(np.sum(pagerank_low) - 1.0) < 1e-10
        assert np.abs(np.sum(pagerank_high) - 1.0) < 1e-10


class TestSampleNetwork:
    """Test the sample network creation function."""
    
    def test_create_sample_network(self):
        """Test sample network creation."""
        adjacency, weights = create_sample_network()
        
        # Check dimensions
        assert adjacency.shape == (5, 5)
        assert weights.shape == (5, 5)
        
        # Check that adjacency matrix is binary
        assert np.all((adjacency == 0) | (adjacency == 1))
        
        # Check that central node (0) connects to all others
        assert np.sum(adjacency[0, :]) == 4  # Central connects to 4 others
        assert np.sum(adjacency[:, 0]) == 4  # 4 others connect to central
        
        # Check that other nodes only connect to central
        for i in range(1, 5):
            assert adjacency[i, 0] == 1  # Connect to central
            assert np.sum(adjacency[i, 1:]) == 0  # Don't connect to others
        
        # Check that weights are positive where edges exist
        for i in range(5):
            for j in range(5):
                if adjacency[i, j] == 1:
                    assert weights[i, j] > 0
                else:
                    assert weights[i, j] == 0


if __name__ == "__main__":
    pytest.main([__file__]) 