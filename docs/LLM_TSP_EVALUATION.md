# LLM-Powered Multi-Agent TSP Evaluation

This evaluation tests **actual LLM agents** collaborating in different organizational structures to solve the Traveling Salesman Problem (TSP). Unlike algorithmic approaches, this uses natural language reasoning, strategic thinking, and inter-agent communication to study how AI agents collaborate similarly to human teams.

## 🎯 Research Objectives

### Primary Questions
1. **Which MAS architecture produces the best collaborative problem-solving?**
   - Hierarchical (leader-follower), Flat (peer-to-peer), or Auction-based (competitive bidding)
   
2. **How do communication patterns differ between architectures?**
   - Message frequency, types, and effectiveness
   
3. **What are the computational costs of LLM-based collaboration?**
   - API calls, tokens used, monetary costs
   
4. **How does AI collaboration compare to human organizational behavior?**
   - Decision quality, coordination overhead, emergent patterns

### Secondary Insights
- Optimal conditions for each architecture
- Trade-offs between solution quality and coordination costs
- Scalability implications for larger teams
- Bias and reasoning patterns in LLM collaboration

## 🏗️ Architecture Implementations

### 1. Hierarchical MAS
**Structure**: Leader agent coordinates multiple follower agents

**Process**:
1. **Leader Analysis**: Uses LLM to analyze city layout and create partitioning strategy
2. **Task Assignment**: Leader assigns city clusters to followers with strategic reasoning
3. **Individual Planning**: Each follower uses LLM to optimize route through assigned cities
4. **Coordination**: Leader synthesizes results and provides final assessment

**Key LLM Interactions**:
- Strategic planning and city clustering
- Task delegation with reasoning
- Route optimization by specialists
- Final synthesis and evaluation

### 2. Flat MAS (Peer-to-Peer)
**Structure**: Equal agents negotiate directly with each other

**Process**:
1. **Initial Assessment**: Each agent analyzes problem from their specialty perspective
2. **Negotiation Rounds**: Agents claim cities with arguments and justifications
3. **Conflict Resolution**: LLM mediator resolves disputes based on efficiency arguments
4. **Route Optimization**: Each agent optimizes their final city collection

**Key LLM Interactions**:
- Specialized analysis and initial preferences
- Strategic negotiation with argumentation
- Conflict resolution through reasoning
- Collaborative optimization

### 3. Auction-Based MAS
**Structure**: Competitive bidding with auctioneer mediation

**Process**:
1. **Strategy Formation**: Each bidder develops strategy based on personality (Conservative, Aggressive, etc.)
2. **Sequential Auctions**: Bidders use LLM reasoning to calculate strategic bids for each city
3. **Auctioneer Evaluation**: LLM auctioneer considers bid amount AND strategic merit
4. **Route Optimization**: Winners optimize routes through purchased cities

**Key LLM Interactions**:
- Strategic planning and budget allocation
- Contextual bidding with reasoning
- Fair evaluation considering multiple factors
- Reflection on auction performance

## 📊 Comprehensive Logging System

### LLM Call Tracking
Every LLM interaction is logged with:
- **Agent identity and type** (leader, follower, peer, bidder, auctioneer)
- **Call purpose** (strategic_planning, negotiation_claim, bidding_decision, etc.)
- **Full prompt and response**
- **Context and reasoning**
- **Timing and token usage**
- **Estimated costs**

### Agent Communication Logging
All inter-agent messages tracked:
- **Sender/receiver pairs**
- **Message types** (task_assignment, negotiation, conflict_resolution, etc.)
- **Content and context**
- **Timestamps**
- **Communication patterns**

### Example Log Entry
```json
{
  "timestamp": "2024-01-15T10:30:45",
  "agent_name": "Follower_0",
  "agent_type": "follower",
  "call_type": "route_planning",
  "prompt": "You are AGENT Follower_0 with expertise in route optimization...",
  "response": "{\n  \"reasoning\": \"I'll start from city 2 as it's central...\",\n  \"route\": [2, 0, 3, 1],\n  \"estimated_distance\": 8.45\n}",
  "context": {"assigned_cities": [0, 1, 2, 3], "coordinates": [(0,0), (1,1), (2,0), (1,-1)]},
  "duration": 2.3,
  "tokens_used": 287,
  "cost": 0.013
}
```

## 🚀 Usage Instructions

### Prerequisites
```bash
# Install dependencies
pip install -r requirements.txt

# Set OpenAI API key
export OPENAI_API_KEY='your-api-key-here'
```

### Quick Test
```bash
# Test LLM integration and basic functionality
python test_llm_tsp.py
```

### Full Evaluation
```bash
# Run complete evaluation across multiple scenarios
python -m evaluations.tsp.llm_main

# Quick test with single scenario
python -m evaluations.tsp.llm_main --quick

# Run without saving detailed logs
python -m evaluations.tsp.llm_main --no-save
```

### Individual Architecture Testing
```bash
# Test specific architectures directly
python -c "
from evaluations.tsp.llm_hierarchical_tsp import evaluate_llm_hierarchical_tsp
result = evaluate_llm_hierarchical_tsp([(0,0), (1,1), (2,0)], 2, 'your-api-key')
print(f'Distance: {result[\"total_distance\"]:.2f}')
"
```

## 📈 Evaluation Scenarios

### Small Clustered (8 cities, 3 agents)
- **Purpose**: Test basic coordination with clear geographical patterns
- **Expected**: Hierarchical should excel due to obvious clustering

### Medium Mixed (12 cities, 4 agents)  
- **Purpose**: Test adaptability with mixed clustering patterns
- **Expected**: Flat negotiation might find creative solutions

### Medium Random (15 cities, 4 agents)
- **Purpose**: Test scalability and robustness
- **Expected**: Auction might handle complexity well through competition

## 📊 Metrics and Analysis

### Performance Metrics
- **Total Travel Distance**: Primary optimization objective
- **Communication Overhead**: Number of messages exchanged
- **Computation Time**: End-to-end evaluation duration
- **Load Balance**: Fairness of city distribution

### LLM-Specific Metrics
- **Total LLM Calls**: API requests made
- **Token Usage**: Input/output tokens consumed
- **Cost Analysis**: Estimated monetary cost
- **Reasoning Quality**: Coherence and strategic thinking

### Architecture-Specific Metrics
- **Hierarchical**: Clustering efficiency, coordination overhead
- **Flat**: Negotiation rounds, conflict resolution success
- **Auction**: Bidding competition, revenue generation, strategy effectiveness

### Meta-Analysis
The system generates LLM-powered analysis of results, comparing:
- Solution quality vs. coordination costs
- Communication patterns and effectiveness
- Reasoning quality and strategic coherence
- Parallels to human organizational behavior

## 🧠 Research Insights

### Expected Findings
- **Hierarchical**: Best for clear problem structure, lowest communication overhead
- **Flat**: Most adaptive and creative, but highest communication costs
- **Auction**: Balanced approach with fair distribution, moderate efficiency

### Human Organizational Parallels
- **Hierarchical**: Corporate top-down structures, military command
- **Flat**: Academic collaborations, democratic decision-making
- **Auction**: Market-based resource allocation, competitive environments

### AI Collaboration Insights
- How LLM agents develop and maintain strategies
- Communication patterns that emerge naturally
- Bias and reasoning limitations in collaborative contexts
- Scalability implications for larger AI teams

## 📁 Output Files

### Results Structure
```
results/llm_tsp/
├── llm_evaluation_YYYYMMDD_HHMMSS.json    # Complete results
├── logs/
│   └── session_YYYYMMDD_HHMMSS/
│       ├── llm_calls.json                  # All LLM interactions
│       ├── communications.json             # Agent messages
│       └── session_summary.json           # Aggregated statistics
```

### Analysis Reports
- **Performance comparison** across architectures
- **Communication pattern analysis**
- **Cost-benefit analysis** of LLM usage
- **Reasoning quality assessment**
- **LLM-generated insights** and recommendations

## 🔬 Research Applications

### Academic Research
- Multi-agent system design principles
- AI collaboration effectiveness studies
- Computational cost analysis of LLM-based systems
- Comparative organizational behavior research

### Practical Applications
- Optimal team structures for AI agent deployment
- Cost-effective LLM usage in collaborative systems
- Communication protocol design for AI teams
- Scalability planning for enterprise AI systems

## ⚠️ Limitations and Considerations

### Cost Implications
- LLM API calls can be expensive for large evaluations
- Recommend starting with `--quick` flag for testing
- Monitor token usage and costs during development

### LLM Variability
- Results may vary between runs due to LLM non-determinism
- Temperature setting affects creativity vs. consistency
- JSON parsing failures handled with algorithmic fallbacks

### Scalability
- Current implementation designed for small-medium problems
- Larger scenarios may require prompt optimization
- Communication complexity grows with agent count

### Evaluation Validity
- Simulated collaboration may not fully represent human dynamics
- LLM reasoning limitations affect strategic thinking
- Cultural and linguistic biases in LLM responses

This evaluation provides unprecedented insight into how AI agents collaborate using natural language reasoning, offering valuable insights for both AI system design and understanding of collaborative intelligence. 