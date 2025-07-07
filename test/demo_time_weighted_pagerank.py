#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

from datetime import datetime, time, date
from core.time_weighted_pagerank import TimeWeightedPageRank, create_sample_time_scenarios
from core.network_graph import NetworkGraph


def create_demo_network():
    g = NetworkGraph()
    
    g.add_node('Grand Central', type='hub', capacity=2000, lines=['red', 'blue', 'green'])
    g.add_node('Times Square', type='hub', capacity=1500, lines=['red', 'blue', 'yellow'])
    g.add_node('Financial District', type='business', capacity=800, lines=['red', 'green'])
    g.add_node('Upper East Side', type='residential', capacity=600, lines=['blue', 'yellow'])
    g.add_node('Brooklyn Bridge', type='residential', capacity=400, lines=['green'])
    g.add_node('JFK Airport', type='airport', capacity=1200, lines=['yellow'])
    g.add_node('Coney Island', type='leisure', capacity=300, lines=['green'])
    
    g.add_edge('Grand Central', 'Times Square', weight=20.0,
               time_profile={'rush_hour': 3.0, 'off_peak': 0.4, 'weekend': 0.8},
               line='red', capacity=500)
    
    g.add_edge('Grand Central', 'Financial District', weight=15.0,
               time_profile={'rush_hour': 2.5, 'off_peak': 0.3, 'weekend': 0.4},
               line='red', capacity=300)
    
    g.add_edge('Grand Central', 'Upper East Side', weight=12.0,
               time_profile={'rush_hour': 2.0, 'off_peak': 0.5, 'weekend': 0.6},
               line='blue', capacity=250)
    
    g.add_edge('Grand Central', 'JFK Airport', weight=25.0,
               time_profile={'rush_hour': 1.8, 'off_peak': 1.2, 'weekend': 2.0},
               line='yellow', capacity=200)
    
    g.add_edge('Times Square', 'Grand Central', weight=18.0,
               time_profile={'rush_hour': 2.8, 'off_peak': 0.5, 'weekend': 0.7})
    
    g.add_edge('Times Square', 'Upper East Side', weight=10.0,
               time_profile={'rush_hour': 1.5, 'off_peak': 0.6, 'weekend': 0.8})
    
    g.add_edge('Times Square', 'Coney Island', weight=8.0,
               time_profile={'rush_hour': 0.8, 'off_peak': 0.7, 'weekend': 2.5})
    
    g.add_edge('Financial District', 'Grand Central', weight=14.0,
               time_profile={'rush_hour': 2.2, 'off_peak': 0.4, 'weekend': 0.3})
    
    g.add_edge('Financial District', 'Brooklyn Bridge', weight=6.0,
               time_profile={'rush_hour': 1.2, 'off_peak': 0.8, 'weekend': 0.9})
    
    g.add_edge('Upper East Side', 'Grand Central', weight=11.0,
               time_profile={'rush_hour': 1.8, 'off_peak': 0.6, 'weekend': 0.5})
    
    g.add_edge('Upper East Side', 'Times Square', weight=9.0,
               time_profile={'rush_hour': 1.4, 'off_peak': 0.7, 'weekend': 0.6})
    
    g.add_edge('Brooklyn Bridge', 'Financial District', weight=5.0,
               time_profile={'rush_hour': 1.0, 'off_peak': 0.9, 'weekend': 1.1})
    
    g.add_edge('Brooklyn Bridge', 'Coney Island', weight=4.0,
               time_profile={'rush_hour': 0.6, 'off_peak': 0.8, 'weekend': 1.8})
    
    g.add_edge('JFK Airport', 'Grand Central', weight=22.0,
               time_profile={'rush_hour': 1.6, 'off_peak': 1.1, 'weekend': 1.8})
    
    g.add_edge('Coney Island', 'Times Square', weight=7.0,
               time_profile={'rush_hour': 0.7, 'off_peak': 0.8, 'weekend': 2.2})
    
    g.add_edge('Coney Island', 'Brooklyn Bridge', weight=3.0,
               time_profile={'rush_hour': 0.5, 'off_peak': 0.7, 'weekend': 1.6})
    
    return g


def print_ranking(title, scores, nodes):
    print(f"\n{title}")
    print("=" * 50)
    ranking = [(nodes[i], score * 100) for i, score in enumerate(scores)]
    ranking.sort(key=lambda x: x[1], reverse=True)
    
    for i, (node, score) in enumerate(ranking, 1):
        print(f"{i:2d}. {node:20s} {score:6.2f}%")


def analyze_time_scenarios():
    print("Time-Weighted PageRank Analysis for Transportation Network")
    print("=" * 60)
    
    time_pagerank = TimeWeightedPageRank()
    network = create_demo_network()
    nodes = network.nodes_list()
    
    scenarios = {
        'Monday Rush Hour (8 AM)': datetime.combine(date(2024, 1, 15), time(8, 0)),
        'Monday Off-Peak (2 PM)': datetime.combine(date(2024, 1, 15), time(14, 0)),
        'Saturday Morning (10 AM)': datetime.combine(date(2024, 1, 20), time(10, 0)),
        'Sunday Evening (6 PM)': datetime.combine(date(2024, 1, 21), time(18, 0)),
    }
    
    for scenario_name, scenario_time in scenarios.items():
        scores = time_pagerank.calculate_time_weighted_pagerank(network, scenario_time)
        print_ranking(scenario_name, scores, nodes)
    
    print("\n" + "=" * 60)
    print("Weather Impact Analysis (Monday Rush Hour)")
    print("=" * 60)
    
    rush_time = datetime.combine(date(2024, 1, 15), time(8, 0))
    weather_conditions = ['clear', 'rain', 'snow', 'storm']
    
    for weather in weather_conditions:
        scores = time_pagerank.calculate_time_weighted_pagerank(network, rush_time, weather_condition=weather)
        print_ranking(f"Rush Hour - {weather.title()} Weather", scores, nodes)
    
    print("\n" + "=" * 60)
    print("Seasonal Impact Analysis (Rush Hour)")
    print("=" * 60)
    
    seasons = {
        'Winter (January)': datetime.combine(date(2024, 1, 15), time(8, 0)),
        'Spring (April)': datetime.combine(date(2024, 4, 15), time(8, 0)),
        'Summer (July)': datetime.combine(date(2024, 7, 15), time(8, 0)),
        'Fall (October)': datetime.combine(date(2024, 10, 15), time(8, 0)),
    }
    
    for season_name, season_time in seasons.items():
        scores = time_pagerank.calculate_time_weighted_pagerank(network, season_time)
        print_ranking(f"Rush Hour - {season_name}", scores, nodes)


def analyze_node_importance_changes():
    print("\n" + "=" * 60)
    print("Node Importance Change Analysis")
    print("=" * 60)
    
    time_pagerank = TimeWeightedPageRank()
    network = create_demo_network()
    nodes = network.nodes_list()
    
    key_nodes = ['Financial District', 'Coney Island', 'JFK Airport']
    
    scenarios = {
        'Rush Hour': datetime.combine(date(2024, 1, 15), time(8, 0)),
        'Off-Peak': datetime.combine(date(2024, 1, 15), time(14, 0)),
        'Weekend': datetime.combine(date(2024, 1, 20), time(10, 0)),
    }
    
    print(f"{'Node':<20} {'Rush Hour':<12} {'Off-Peak':<12} {'Weekend':<12} {'Change':<10}")
    print("-" * 70)
    
    for node in key_nodes:
        node_idx = nodes.index(node)
        scores = []
        
        for scenario_name, scenario_time in scenarios.items():
            scenario_scores = time_pagerank.calculate_time_weighted_pagerank(network, scenario_time)
            scores.append(scenario_scores[node_idx] * 100)
        
        change = scores[2] - scores[0]
        change_str = f"{change:+.1f}%"
        
        print(f"{node:<20} {scores[0]:<12.2f} {scores[1]:<12.2f} {scores[2]:<12.2f} {change_str}")


if __name__ == "__main__":
    analyze_time_scenarios()
    analyze_node_importance_changes()
    
    print("\n" + "=" * 60)
    print("Key Insights:")
    print("=" * 60)
    print("1. Business districts (Financial District) peak during rush hour")
    print("2. Leisure destinations (Coney Island) gain importance on weekends")
    print("3. Airport usage increases during weekends (leisure travel)")
    print("4. Weather conditions affect overall network activity")
    print("5. Seasonal factors provide additional context for planning")
    print("6. Hub stations (Grand Central, Times Square) maintain high importance") 