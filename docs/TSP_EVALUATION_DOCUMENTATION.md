# Collaborative Traveling Salesman Problem (TSP) Evaluation

## Overview

This document describes the implementation of a Collaborative Traveling Salesman Problem (TSP) evaluation system that compares three different Multi-Agent System (MAS) architectures: Hierarchical, Flat, and Auction-based.

## Problem Definition

**Objective**: Divide and solve a TSP instance where N cities must be visited by M agents (salesmen) with the goal of minimizing total travel distance.

**Key Challenges**:
- City partitioning among agents
- Route optimization for each agent
- Coordination and communication between agents
- Load balancing across agents

## MAS Architecture Implementations

### 1. Hierarchical MAS

**Approach**: A central leader partitions cities into clusters and assigns them to follower agents.

**Algorithm**:
1. Leader uses k-means clustering to partition cities into M clusters
2. Each cluster is assigned to a follower agent
3. Each agent solves TSP for their assigned cities using nearest neighbor + 2-opt
4. Agents report results back to leader

**Pros**:
- Optimal clustering reduces overlap
- Minimal communication overhead
- Clear coordination structure

**Cons**:
- Leader becomes a bottleneck
- Inflexible to agent-specific constraints
- Single point of failure

**Implementation**: `evaluations/tsp/hierarchical_tsp.py`

### 2. Flat MAS

**Approach**: Agents negotiate peer-to-peer to claim cities through proximity-based strategies.

**Algorithm**:
1. Agents start with empty city assignments
2. In each negotiation round:
   - Each agent claims cities based on proximity to their current collection
   - Conflicts are resolved through load balancing
   - Assigned cities are removed from the unassigned pool
3. Each agent solves TSP for their final assignment

**Pros**:
- Resilient to failures
- Adaptable to dynamic agent capabilities
- Distributed decision making

**Cons**:
- High communication cost
- Risk of suboptimal splits
- Complex negotiation protocols

**Implementation**: `evaluations/tsp/flat_tsp.py`

### 3. Auction-Based MAS

**Approach**: Cities are auctioned in rounds with agents bidding based on proximity and insertion cost.

**Algorithm**:
1. Auctioneer manages sequential city auctions
2. For each city, agents calculate bids based on:
   - Distance from starting position (if no cities assigned)
   - Minimum insertion cost into current route
3. Highest bidder wins the city and pays the bid
4. Each agent optimizes their final route

**Pros**:
- Fair distribution through market mechanisms
- Dynamic adjustments based on agent preferences
- Economic efficiency

**Cons**:
- Bidding overhead
- Possible inefficiency if bids don't reflect true costs
- Requires monetary constraints

**Implementation**: `evaluations/tsp/auction_tsp.py`

## Success Metrics

### Primary Metrics
- **Total Travel Distance**: Sum of all agents' route distances
- **Computation Time**: Time to partition cities and finalize routes
- **Communication Overhead**: Number of messages exchanged
- **Load Balance**: Variance in the number of cities per agent

### Architecture-Specific Metrics

**Hierarchical**:
- Clustering efficiency (intra-cluster distance)
- Leader coordination overhead

**Flat**:
- Number of negotiation rounds
- Load fairness coefficient
- Unresolved cities

**Auction**:
- Total auction revenue
- Average bid per city
- Money fairness distribution
- Bidders per auction

## Implementation Details

### Core Components

1. **TSPUtils** (`evaluations/tsp/utils.py`):
   - City generation
   - Distance calculations
   - Route optimization (nearest neighbor + 2-opt)
   - K-means clustering

2. **TSPMetrics** (`evaluations/tsp/metrics.py`):
   - Performance metrics collection
   - Statistical analysis
   - Architecture comparison

3. **TSPEvaluator** (`evaluations/tsp/metrics.py`):
   - Evaluation orchestration
   - Timing and measurement
   - Results aggregation

### Evaluation Framework

The evaluation system supports:
- Multiple test scenarios (small, medium, large)
- Configurable parameters (cities, agents, grid size, seed)
- Comprehensive performance comparison
- Results export to JSON

## Usage

### Quick Test
```bash
python test_tsp.py
```

### Full Evaluation
```bash
python -m evaluations.tsp.main
```

### Individual MAS Testing
```bash
RUN_EVALUATION=tsp python mas_hierarchical/main.py
RUN_EVALUATION=tsp python mas_flat/main.py
RUN_EVALUATION=tsp python mas_auction/main.py
```

## Results Analysis

### Typical Performance Patterns

**Distance Optimization**:
- Hierarchical MAS typically achieves best total distance due to optimal clustering
- Flat MAS shows moderate performance with good adaptability
- Auction MAS may have higher distances due to bidding constraints

**Communication Efficiency**:
- Hierarchical MAS has lowest communication overhead
- Flat MAS has high communication due to peer-to-peer negotiation
- Auction MAS has moderate communication focused on bidding

**Load Balancing**:
- Hierarchical MAS achieves good balance through clustering
- Flat MAS may have uneven distribution due to negotiation dynamics
- Auction MAS balance depends on bidding strategies and budget constraints

**Computation Speed**:
- Flat MAS often fastest due to parallel processing
- Auction MAS moderate speed with bidding calculations
- Hierarchical MAS may be slower due to clustering computation

## Extensions and Future Work

1. **Dynamic Scenarios**: Cities appearing/disappearing during execution
2. **Agent Failures**: Robustness testing with agent failures
3. **Heterogeneous Agents**: Different capabilities and constraints
4. **Real-world Constraints**: Vehicle capacity, time windows, fuel costs
5. **Advanced Algorithms**: Genetic algorithms, simulated annealing
6. **Visualization**: Route plotting and animation

## Dependencies

- `numpy`: Numerical computations
- `scikit-learn`: K-means clustering
- `python-dotenv`: Environment configuration
- `matplotlib`: Visualization (optional)

## File Structure

```
evaluations/tsp/
├── __init__.py              # Module initialization
├── main.py                  # Main evaluation runner
├── utils.py                 # TSP utilities and algorithms
├── metrics.py               # Performance metrics
├── hierarchical_tsp.py      # Hierarchical MAS evaluation
├── flat_tsp.py             # Flat MAS evaluation
└── auction_tsp.py          # Auction MAS evaluation
```

## Configuration

The evaluation system supports various configuration options:

- `n_cities`: Number of cities (default: 20)
- `n_agents`: Number of agents (default: 4)
- `grid_size`: City generation grid size (default: 100)
- `seed`: Random seed for reproducibility (default: 42)
- `max_negotiation_rounds`: Max rounds for flat MAS (default: 10)
- `auction_strategy`: Sequential or batch auctions (default: "sequential")

## Conclusion

This TSP evaluation provides a comprehensive framework for comparing different MAS architectures on a well-defined optimization problem. The implementation demonstrates the trade-offs between centralized coordination, distributed negotiation, and market-based allocation mechanisms. 