import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, time
from .pagerank_engine import PageRankEngine, PageRankConfig
from .network_graph import NetworkGraph


@dataclass
class TimeConfig:
    rush_hour_multiplier: float = 2.0
    off_peak_multiplier: float = 0.5
    morning_rush_start: time = time(7, 0)
    morning_rush_end: time = time(9, 0)
    evening_rush_start: time = time(17, 0)
    evening_rush_end: time = time(19, 0)
    weekend_multiplier: float = 0.7
    holiday_multiplier: float = 0.5


class TimeWeightedPageRank:
    def __init__(self, base_config: Optional[PageRankConfig] = None, 
                 time_config: Optional[TimeConfig] = None):
        self.base_engine = PageRankEngine(base_config)
        self.time_config = time_config or TimeConfig()
        
        self.seasonal_factors = {
            'spring': 1.0,
            'summer': 0.9,
            'fall': 1.1,
            'winter': 0.8
        }
        
        self.weather_factors = {
            'clear': 1.0,
            'rain': 0.8,
            'snow': 0.5,
            'storm': 0.3
        }
    
    def get_time_context(self, current_time: datetime) -> str:
        current_time_only = current_time.time()
        is_weekend = current_time.weekday() >= 5
        if is_weekend:
            return 'weekend'
        if (self.time_config.morning_rush_start <= current_time_only <= self.time_config.morning_rush_end or
            self.time_config.evening_rush_start <= current_time_only <= self.time_config.evening_rush_end):
            return 'rush_hour'
        if (time(10, 0) <= current_time_only <= time(16, 0) or
            current_time_only >= time(20, 0) or current_time_only <= time(6, 0)):
            return 'off_peak'
        return 'normal'
    
    def get_seasonal_factor(self, current_time: datetime) -> float:
        month = current_time.month
        
        if month in [3, 4, 5]:
            return self.seasonal_factors['spring']
        elif month in [6, 7, 8]:
            return self.seasonal_factors['summer']
        elif month in [9, 10, 11]:
            return self.seasonal_factors['fall']
        else:
            return self.seasonal_factors['winter']
    
    def get_weather_factor(self, weather_condition: str) -> float:
        return self.weather_factors.get(weather_condition.lower(), 1.0)
    
    def calculate_time_weighted_pagerank(self, 
                                         graph: NetworkGraph,
                                         current_time: datetime,
                                         weather_condition: str = 'clear',
                                         custom_time_context: Optional[str] = None) -> np.ndarray:
        if custom_time_context is not None:
            time_context = custom_time_context
        else:
            time_context = self.get_time_context(current_time)
        seasonal_factor = self.get_seasonal_factor(current_time)
        weather_factor = self.get_weather_factor(weather_condition)
        node_list, weighted_matrix = graph.to_adjacency_matrix(time_context)
        weighted_matrix = np.array(weighted_matrix) * seasonal_factor * weather_factor
        adjacency_matrix = np.array(graph.to_adjacency_binary_matrix()[1])
        pagerank_scores = self.base_engine.calculate_pagerank_with_weights(
            adjacency_matrix, weighted_matrix
        )
        return pagerank_scores
    
    def calculate_hourly_pagerank(self, 
                                adjacency_matrix: np.ndarray,
                                base_date: datetime,
                                weather_condition: str = 'clear') -> Dict[int, np.ndarray]:
        hourly_scores = {}
        
        for hour in range(24):
            current_time = base_date.replace(hour=hour, minute=0, second=0, microsecond=0)
            scores = self.calculate_time_weighted_pagerank(
                adjacency_matrix, current_time, weather_condition
            )
            hourly_scores[hour] = scores
        
        return hourly_scores
    
    def calculate_daily_pagerank(self, 
                               adjacency_matrix: np.ndarray,
                               base_date: datetime,
                               weather_condition: str = 'clear') -> Dict[str, np.ndarray]:
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        daily_scores = {}
        
        for day_idx in range(7):
            current_time = base_date.replace(hour=8, minute=0, second=0, microsecond=0)
            days_diff = day_idx - current_time.weekday()
            current_time = current_time.replace(day=current_time.day + days_diff)
            
            scores = self.calculate_time_weighted_pagerank(
                adjacency_matrix, current_time, weather_condition
            )
            daily_scores[day_names[day_idx]] = scores
        
        return daily_scores
    
    def get_peak_hours_analysis(self, 
                               adjacency_matrix: np.ndarray,
                               base_date: datetime,
                               weather_condition: str = 'clear') -> Dict[str, Any]:
        hourly_scores = self.calculate_hourly_pagerank(adjacency_matrix, base_date, weather_condition)
        
        hourly_averages = {}
        for hour, scores in hourly_scores.items():
            hourly_averages[hour] = np.mean(scores)
        
        sorted_hours = sorted(hourly_averages.items(), key=lambda x: x[1], reverse=True)
        
        peak_hours = sorted_hours[:3]
        
        off_peak_hours = sorted_hours[-3:]
        
        return {
            'peak_hours': peak_hours,
            'off_peak_hours': off_peak_hours,
            'hourly_averages': hourly_averages,
            'hourly_scores': hourly_scores
        }
    
    def compare_time_periods(self, 
                           adjacency_matrix: np.ndarray,
                           time1: datetime,
                           time2: datetime,
                           weather_condition: str = 'clear') -> Dict[str, Any]:
        scores1 = self.calculate_time_weighted_pagerank(adjacency_matrix, time1, weather_condition)
        scores2 = self.calculate_time_weighted_pagerank(adjacency_matrix, time2, weather_condition)
        
        score_diff = scores2 - scores1
        score_ratio = scores2 / (scores1 + 1e-10)
        
        node_changes = [(i, diff) for i, diff in enumerate(score_diff)]
        node_changes.sort(key=lambda x: abs(x[1]), reverse=True)
        
        return {
            'scores_time1': scores1,
            'scores_time2': scores2,
            'score_differences': score_diff,
            'score_ratios': score_ratio,
            'biggest_changes': node_changes[:10],
            'time1': time1,
            'time2': time2
        }


def create_sample_time_scenarios() -> Dict[str, datetime]:
    from datetime import datetime, date
    
    base_date = date(2024, 1, 15)
    
    scenarios = {
        'monday_morning_rush': datetime.combine(base_date, time(8, 0)),
        'monday_evening_rush': datetime.combine(base_date, time(18, 0)),
        'monday_off_peak': datetime.combine(base_date, time(14, 0)),
        'saturday_morning': datetime.combine(base_date.replace(day=20), time(10, 0)),
        'sunday_evening': datetime.combine(base_date.replace(day=21), time(20, 0)),
        'winter_morning': datetime.combine(date(2024, 1, 15), time(8, 0)),
        'summer_morning': datetime.combine(date(2024, 7, 15), time(8, 0)),
    }
    
    return scenarios 