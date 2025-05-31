import numpy as np
import random
import math
from typing import List, Tuple, Dict
from sklearn.cluster import KMeans

class TSPUtils:
    @staticmethod
    def generate_cities(n_cities: int, grid_size: int = 100, seed: int = None) -> List[Tuple[int, int]]:
        """Generate random city coordinates"""
        if seed:
            random.seed(seed)
        cities = []
        for i in range(n_cities):
            x = random.randint(0, grid_size)
            y = random.randint(0, grid_size)
            cities.append((x, y))
        return cities
    
    @staticmethod
    def calculate_distance(city1: Tuple[int, int], city2: Tuple[int, int]) -> float:
        """Calculate Euclidean distance between two cities"""
        return math.sqrt((city1[0] - city2[0])**2 + (city1[1] - city2[1])**2)
    
    @staticmethod
    def calculate_route_distance(cities: List[Tuple[int, int]], route: List[int]) -> float:
        """Calculate total distance for a given route"""
        total_distance = 0
        for i in range(len(route)):
            current_city = cities[route[i]]
            next_city = cities[route[(i + 1) % len(route)]]
            total_distance += TSPUtils.calculate_distance(current_city, next_city)
        return total_distance
    
    @staticmethod
    def nearest_neighbor_tsp(cities: List[Tuple[int, int]], start_city: int = 0) -> Tuple[List[int], float]:
        """Solve TSP using nearest neighbor heuristic"""
        n = len(cities)
        unvisited = set(range(n))
        current = start_city
        route = [current]
        unvisited.remove(current)
        
        while unvisited:
            nearest = min(unvisited, 
                         key=lambda city: TSPUtils.calculate_distance(cities[current], cities[city]))
            route.append(nearest)
            current = nearest
            unvisited.remove(nearest)
        
        distance = TSPUtils.calculate_route_distance(cities, route)
        return route, distance
    
    @staticmethod
    def cluster_cities(cities: List[Tuple[int, int]], n_clusters: int, seed: int = None) -> Dict[int, List[int]]:
        """Cluster cities using K-means"""
        if seed:
            np.random.seed(seed)
        
        if len(cities) < n_clusters:
            # If fewer cities than clusters, assign each city to its own cluster
            clusters = {}
            for i, _ in enumerate(cities):
                clusters[i] = [i]
            return clusters
        
        city_coords = np.array(cities)
        kmeans = KMeans(n_clusters=n_clusters, random_state=seed, n_init=10)
        cluster_labels = kmeans.fit_predict(city_coords)
        
        clusters = {}
        for i in range(n_clusters):
            clusters[i] = [idx for idx, label in enumerate(cluster_labels) if label == i]
        
        return clusters
    
    @staticmethod
    def optimize_route_2opt(cities: List[Tuple[int, int]], route: List[int], max_iterations: int = 1000) -> Tuple[List[int], float]:
        """Improve route using 2-opt optimization"""
        best_route = route.copy()
        best_distance = TSPUtils.calculate_route_distance(cities, best_route)
        
        for _ in range(max_iterations):
            improved = False
            for i in range(len(route) - 1):
                for j in range(i + 2, len(route)):
                    if j == len(route) - 1 and i == 0:
                        continue  # Skip if it would disconnect the route
                    
                    # Create new route by reversing the segment between i and j
                    new_route = route[:i+1] + route[i+1:j+1][::-1] + route[j+1:]
                    new_distance = TSPUtils.calculate_route_distance(cities, new_route)
                    
                    if new_distance < best_distance:
                        best_route = new_route
                        best_distance = new_distance
                        improved = True
            
            if not improved:
                break
            
            route = best_route.copy()
        
        return best_route, best_distance 