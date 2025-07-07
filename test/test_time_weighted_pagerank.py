import pytest
import numpy as np
import sys
import os
from datetime import datetime, time, date
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))
from core.time_weighted_pagerank import TimeWeightedPageRank, TimeConfig, create_sample_time_scenarios
from core.network_graph import NetworkGraph


def create_time_profile_graph():
    g = NetworkGraph()
    g.add_edge('A', 'B', weight=1.0, time_profile={'rush_hour': 2.0, 'off_peak': 0.5})
    g.add_edge('A', 'C', weight=1.0, time_profile={'rush_hour': 2.0, 'off_peak': 0.5})
    g.add_edge('A', 'D', weight=1.0)
    g.add_edge('A', 'E', weight=1.0)
    g.add_edge('B', 'A', weight=1.0)
    g.add_edge('C', 'A', weight=1.0)
    g.add_edge('D', 'A', weight=1.0)
    g.add_edge('E', 'A', weight=1.0)
    return g


def create_complex_transportation_network():
    g = NetworkGraph()
    
    g.add_node('Central', type='hub', capacity=1000)
    g.add_node('Business', type='business', capacity=500)
    g.add_node('Residential', type='residential', capacity=300)
    g.add_node('Airport', type='airport', capacity=800)
    g.add_node('Suburb', type='suburban', capacity=200)
    
    g.add_edge('Central', 'Business', weight=10.0, 
               time_profile={'rush_hour': 3.0, 'off_peak': 0.3, 'weekend': 0.5},
               line='red', capacity=200)
    
    g.add_edge('Central', 'Residential', weight=8.0,
               time_profile={'rush_hour': 2.5, 'off_peak': 0.4, 'weekend': 0.8},
               line='blue', capacity=150)
    
    g.add_edge('Central', 'Airport', weight=15.0,
               time_profile={'rush_hour': 1.5, 'off_peak': 1.2, 'weekend': 1.8},
               line='green', capacity=100)
    
    g.add_edge('Central', 'Suburb', weight=5.0,
               time_profile={'rush_hour': 0.8, 'off_peak': 0.6, 'weekend': 2.0},
               line='yellow', capacity=80)
    
    g.add_edge('Business', 'Central', weight=6.0,
               time_profile={'rush_hour': 2.0, 'off_peak': 0.5, 'weekend': 0.3})
    g.add_edge('Residential', 'Central', weight=7.0,
               time_profile={'rush_hour': 2.2, 'off_peak': 0.6, 'weekend': 0.4})
    g.add_edge('Airport', 'Central', weight=12.0,
               time_profile={'rush_hour': 1.3, 'off_peak': 1.1, 'weekend': 1.5})
    g.add_edge('Suburb', 'Central', weight=4.0,
               time_profile={'rush_hour': 0.7, 'off_peak': 0.5, 'weekend': 1.8})
    
    return g


class TestTimeConfig:
    def test_default_config(self):
        config = TimeConfig()
        assert config.rush_hour_multiplier == 2.0
        assert config.off_peak_multiplier == 0.5
        assert config.weekend_multiplier == 0.7
        assert config.holiday_multiplier == 0.5
    def test_custom_config(self):
        config = TimeConfig(
            rush_hour_multiplier=3.0,
            off_peak_multiplier=0.3,
            weekend_multiplier=0.5
        )
        assert config.rush_hour_multiplier == 3.0
        assert config.off_peak_multiplier == 0.3
        assert config.weekend_multiplier == 0.5

class TestTimeWeightedPageRank:
    def setup_method(self):
        self.time_pagerank = TimeWeightedPageRank()
        self.graph = create_time_profile_graph()
        self.complex_graph = create_complex_transportation_network()
        self.scenarios = create_sample_time_scenarios()
    
    def test_initialization(self):
        assert self.time_pagerank.time_config.rush_hour_multiplier == 2.0
        assert self.time_pagerank.base_engine is not None
        assert 'spring' in self.time_pagerank.seasonal_factors
        assert 'clear' in self.time_pagerank.weather_factors
    
    def test_get_time_context(self):
        monday_rush = datetime.combine(date(2024, 1, 15), time(8, 0))
        assert self.time_pagerank.get_time_context(monday_rush) == 'rush_hour'
        monday_off_peak = datetime.combine(date(2024, 1, 15), time(14, 0))
        assert self.time_pagerank.get_time_context(monday_off_peak) == 'off_peak'
        saturday = datetime.combine(date(2024, 1, 20), time(10, 0))
        assert self.time_pagerank.get_time_context(saturday) == 'weekend'
    
    def test_time_weighted_pagerank_changes(self):
        rush_time = datetime.combine(date(2024, 1, 15), time(8, 0))
        rush_scores = self.time_pagerank.calculate_time_weighted_pagerank(self.graph, rush_time)
        off_peak_time = datetime.combine(date(2024, 1, 15), time(14, 0))
        off_peak_scores = self.time_pagerank.calculate_time_weighted_pagerank(self.graph, off_peak_time)
        assert not np.allclose(rush_scores, off_peak_scores)
        assert np.all(rush_scores > 0)
        assert np.abs(np.sum(rush_scores) - 1.0) < 1e-10
        assert np.all(off_peak_scores > 0)
        assert np.abs(np.sum(off_peak_scores) - 1.0) < 1e-10
    
    def test_time_weighted_pagerank_weekend(self):
        weekend_time = datetime.combine(date(2024, 1, 20), time(10, 0))
        weekend_scores = self.time_pagerank.calculate_time_weighted_pagerank(self.graph, weekend_time)
        assert np.all(weekend_scores > 0)
        assert np.abs(np.sum(weekend_scores) - 1.0) < 1e-10
    
    def test_time_weighted_pagerank_custom_context(self):
        rush_scores = self.time_pagerank.calculate_time_weighted_pagerank(self.graph, datetime.now(), custom_time_context='rush_hour')
        off_peak_scores = self.time_pagerank.calculate_time_weighted_pagerank(self.graph, datetime.now(), custom_time_context='off_peak')
        assert not np.allclose(rush_scores, off_peak_scores)
    
    def test_time_weighted_pagerank_weather_and_season(self):
        rush_time = datetime.combine(date(2024, 1, 15), time(8, 0))
        clear_scores = self.time_pagerank.calculate_time_weighted_pagerank(self.graph, rush_time, weather_condition='clear')
        rain_scores = self.time_pagerank.calculate_time_weighted_pagerank(self.graph, rush_time, weather_condition='rain')
        assert np.allclose(clear_scores, rain_scores) or np.mean(rain_scores) < np.mean(clear_scores)
    
    def test_complex_transportation_network_rush_hour(self):
        rush_time = datetime.combine(date(2024, 1, 15), time(8, 0))
        scores = self.time_pagerank.calculate_time_weighted_pagerank(self.complex_graph, rush_time)
        
        assert np.all(scores > 0)
        assert np.abs(np.sum(scores) - 1.0) < 1e-10
        
        business_idx = list(self.complex_graph.nodes_list()).index('Business')
        residential_idx = list(self.complex_graph.nodes_list()).index('Residential')
        
        assert scores[business_idx] > scores[list(self.complex_graph.nodes_list()).index('Suburb')]
        assert scores[residential_idx] > scores[list(self.complex_graph.nodes_list()).index('Suburb')]
    
    def test_complex_transportation_network_weekend(self):
        weekend_time = datetime.combine(date(2024, 1, 20), time(14, 0))
        scores = self.time_pagerank.calculate_time_weighted_pagerank(self.complex_graph, weekend_time)
        
        assert np.all(scores > 0)
        assert np.abs(np.sum(scores) - 1.0) < 1e-10
        
        nodes = self.complex_graph.nodes_list()
        suburb_idx = nodes.index('Suburb')
        airport_idx = nodes.index('Airport')
        central_idx = nodes.index('Central')
        
        assert scores[central_idx] > scores[suburb_idx]
        assert scores[central_idx] > scores[airport_idx]
        
        rush_time = datetime.combine(date(2024, 1, 15), time(8, 0))
        rush_scores = self.time_pagerank.calculate_time_weighted_pagerank(self.complex_graph, rush_time)
        
        suburb_weekend_rank = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
        suburb_weekend_rank = next(i for i, (idx, _) in enumerate(suburb_weekend_rank) if idx == suburb_idx)
        
        suburb_rush_rank = sorted(enumerate(rush_scores), key=lambda x: x[1], reverse=True)
        suburb_rush_rank = next(i for i, (idx, _) in enumerate(suburb_rush_rank) if idx == suburb_idx)
        
        assert suburb_weekend_rank <= suburb_rush_rank
    
    def test_complex_transportation_network_weather_impact(self):
        rush_time = datetime.combine(date(2024, 1, 15), time(8, 0))
        
        clear_scores = self.time_pagerank.calculate_time_weighted_pagerank(
            self.complex_graph, rush_time, weather_condition='clear'
        )
        
        storm_scores = self.time_pagerank.calculate_time_weighted_pagerank(
            self.complex_graph, rush_time, weather_condition='storm'
        )
        
        assert np.mean(storm_scores) <= np.mean(clear_scores)
    
    def test_complex_transportation_network_seasonal_impact(self):
        winter_rush = datetime.combine(date(2024, 1, 15), time(8, 0))
        winter_scores = self.time_pagerank.calculate_time_weighted_pagerank(
            self.complex_graph, winter_rush, weather_condition='clear'
        )
        
        summer_rush = datetime.combine(date(2024, 7, 15), time(8, 0))
        summer_scores = self.time_pagerank.calculate_time_weighted_pagerank(
            self.complex_graph, summer_rush, weather_condition='clear'
        )
        
        winter_top = np.argmax(winter_scores)
        summer_top = np.argmax(summer_scores)
        assert winter_top == summer_top
        
        winter_sum = np.sum(winter_scores)
        summer_sum = np.sum(summer_scores)
        assert np.abs(winter_sum - 1.0) < 1e-10
        assert np.abs(summer_sum - 1.0) < 1e-10
    
    def test_node_importance_ranking_changes(self):
        nodes = self.complex_graph.nodes_list()
        
        rush_time = datetime.combine(date(2024, 1, 15), time(8, 0))
        rush_scores = self.time_pagerank.calculate_time_weighted_pagerank(self.complex_graph, rush_time)
        rush_ranking = [(nodes[i], score) for i, score in enumerate(rush_scores)]
        rush_ranking.sort(key=lambda x: x[1], reverse=True)
        
        weekend_time = datetime.combine(date(2024, 1, 20), time(14, 0))
        weekend_scores = self.time_pagerank.calculate_time_weighted_pagerank(self.complex_graph, weekend_time)
        weekend_ranking = [(nodes[i], score) for i, score in enumerate(weekend_scores)]
        weekend_ranking.sort(key=lambda x: x[1], reverse=True)
        
        assert rush_ranking != weekend_ranking
        
        print(f"\nRush Hour Ranking: {rush_ranking}")
        print(f"Weekend Ranking: {weekend_ranking}")
        
        central_rush_rank = next(i for i, (node, _) in enumerate(rush_ranking) if node == 'Central')
        central_weekend_rank = next(i for i, (node, _) in enumerate(weekend_ranking) if node == 'Central')
        
        assert central_rush_rank < 3
        assert central_weekend_rank < 3

class TestSampleTimeScenarios:
    def test_create_sample_time_scenarios(self):
        scenarios = create_sample_time_scenarios()
        expected_scenarios = [
            'monday_morning_rush', 'monday_evening_rush', 'monday_off_peak',
            'saturday_morning', 'sunday_evening', 'winter_morning', 'summer_morning'
        ]
        assert all(scenario in scenarios for scenario in expected_scenarios)
        assert len(scenarios) == len(expected_scenarios)
        assert scenarios['monday_morning_rush'].weekday() == 0
        assert scenarios['saturday_morning'].weekday() == 5
        assert scenarios['winter_morning'].month == 1
        assert scenarios['summer_morning'].month == 7

if __name__ == "__main__":
    pytest.main([__file__]) 