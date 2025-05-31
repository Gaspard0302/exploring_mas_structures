# LLM-Powered Multi-Agent System Evaluation

A comprehensive research framework for studying how **LLM agents collaborate** in different organizational structures. This project evaluates Hierarchical, Flat, and Auction-based multi-agent systems using **actual LLM reasoning** to understand AI collaboration patterns and their parallels to human organizational behavior.

## 🎯 Research Focus

**Core Question**: Which organizational structure (Hierarchical, Flat, or Auction-based) produces the most effective LLM agent collaboration?

### Primary Research Objectives
- **Solution Quality**: Which architecture finds the best solutions?
- **Communication Efficiency**: How do message patterns differ between structures?
- **Cost Analysis**: What are the computational costs (LLM calls, tokens, money) of each approach?
- **Collaboration Patterns**: How do LLM agents naturally coordinate and negotiate?
- **Human Parallels**: How do AI collaboration patterns compare to human organizational behavior?

## 🏗️ Architecture Implementations

### 1. **Hierarchical MAS**
- **Leader agent** analyzes problems and creates strategic plans using LLM reasoning
- **Follower agents** receive assignments and optimize solutions with LLM planning
- **Top-down coordination** with clear command structure
- *Similar to*: Corporate hierarchies, military command structures

### 2. **Flat MAS (Peer-to-Peer)**
- **Equal agents** negotiate directly using natural language arguments
- **Multi-round negotiation** with strategic reasoning and conflict resolution
- **Distributed decision-making** through LLM mediation
- *Similar to*: Academic collaborations, democratic decision-making

### 3. **Auction-Based MAS**
- **Strategic bidders** with different personalities (Conservative, Aggressive, etc.)
- **LLM auctioneer** evaluates bids based on merit AND amount
- **Competitive resource allocation** with reasoned bidding strategies
- *Similar to*: Market-based allocation, competitive environments

## 🚀 Quick Start

### 1. Setup
```bash
# Clone repository
git clone <repository-url>
cd multi-agent-systems

# Install dependencies
pip install -r requirements.txt

# Setup API key configuration
cp config_template.py config.py
# Edit config.py and set your OpenAI API key
```

### 2. Configure API Key
Edit `config.py`:
```python
OPENAI_API_KEY = "your-openai-api-key-here"
```

**Alternative**: Set environment variable
```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

### 3. Test Installation
```bash
# Test basic functionality
python test_llm_tsp.py
```

### 4. Run Evaluation
```bash
# Quick test (single scenario)
python -m evaluations.tsp.llm_main --quick

# Full evaluation (multiple scenarios)
python -m evaluations.tsp.llm_main

# Without saving detailed logs
python -m evaluations.tsp.llm_main --no-save
```

## 📊 What Gets Evaluated

### Traveling Salesman Problem (TSP) Collaboration
**Scenario**: Multiple agents must collaboratively solve a TSP where N cities need to be visited by M agents, minimizing total travel distance.

**LLM Integration**: 
- Agents use natural language reasoning to analyze city patterns
- Strategic thinking for route optimization and resource allocation
- Natural language negotiation and conflict resolution
- Reflection on collaboration effectiveness

### Comprehensive Logging
Every aspect of agent collaboration is tracked:
- **All LLM calls** with prompts, responses, timing, and costs
- **Agent communications** with message types and strategic reasoning
- **Performance metrics** for each architecture
- **Meta-analysis** by LLM of collaboration effectiveness

## 📈 Output and Analysis

### Real-Time Progress
```
🤖 Starting LLM-Powered Multi-Agent TSP Evaluation
✅ LLM Connection Test: OK

📍 Scenario 1/3: Small_Clustered
   🏗️ Running Hierarchical MAS...
      ✅ Distance: 15.23, Comm: 8, LLM Calls: 12, Cost: $0.087, Time: 23.4s
   🏗️ Running Flat MAS...
      ✅ Distance: 16.45, Comm: 24, LLM Calls: 28, Cost: $0.203, Time: 41.2s
   🏗️ Running Auction MAS...
      ✅ Distance: 17.12, Comm: 19, LLM Calls: 22, Cost: $0.156, Time: 35.7s
```

### Generated Files
```
results/llm_tsp/
├── llm_evaluation_YYYYMMDD_HHMMSS.json    # Complete results
└── logs/
    └── session_YYYYMMDD_HHMMSS/
        ├── llm_calls.json                  # All LLM interactions
        ├── communications.json             # Agent messages
        └── session_summary.json           # Session statistics
```

### Performance Analysis
```
🏆 Performance Rankings (Average Distance):
   1. Hierarchical: 15.67 (±1.23)
   2. Flat: 16.89 (±2.45)  
   3. Auction: 17.34 (±1.87)

💰 Cost Analysis:
   Hierarchical: $0.092 per scenario, 11.3 messages
   Flat: $0.198 per scenario, 23.7 messages
   Auction: $0.154 per scenario, 18.2 messages
```

### LLM-Generated Insights
The system uses an LLM analyst to generate comprehensive insights:
- Comparative analysis of collaboration effectiveness
- Communication pattern analysis
- Cost-benefit trade-offs
- Recommendations for optimal conditions
- Parallels to human organizational behavior

## 🔬 Research Applications

### Academic Research
- **Multi-agent system design principles**
- **AI collaboration effectiveness studies**
- **Computational cost analysis of LLM-based systems**
- **Comparative organizational behavior research**

### Practical Applications
- **Optimal team structures** for AI agent deployment
- **Cost-effective LLM usage** in collaborative systems
- **Communication protocol design** for AI teams
- **Scalability planning** for enterprise AI systems

## 📊 Project Structure

```
multi-agent-systems/
├── README.md                            # This file
├── requirements.txt                     # Python dependencies
├── config_template.py                   # Configuration template
├── config.py                           # Your configuration (gitignored)
├── test_llm_tsp.py                     # Quick test script
│
├── evaluations/tsp/                     # TSP evaluation module
│   ├── llm_main.py                     # Main evaluation runner
│   ├── llm_integration.py              # LLM integration & logging
│   ├── llm_hierarchical_tsp.py         # Hierarchical LLM agents
│   ├── llm_flat_tsp.py                 # Flat/P2P LLM agents
│   ├── llm_auction_tsp.py              # Auction LLM agents
│   ├── utils.py                        # TSP utilities
│   └── metrics.py                      # Performance metrics
│
├── mas_hierarchical/                    # Original agent implementations
├── mas_flat/                           # (for reference/comparison)
├── mas_auction/                        
│
├── results/                            # Generated results (gitignored)
├── logs/                              # Generated logs (gitignored)
└── docs/                              # Documentation
    └── LLM_TSP_EVALUATION.md          # Detailed evaluation docs
```

## 🔧 Configuration Options

Edit `config.py` to customize:

```python
# Model selection (impacts cost and quality)
DEFAULT_LLM_MODEL = "gpt-4"          # Best quality
# DEFAULT_LLM_MODEL = "gpt-3.5-turbo" # Cost savings

# Response creativity (0.0 = deterministic, 1.0 = creative)
LLM_TEMPERATURE = 0.7

# Cost tracking (update with current OpenAI pricing)
COST_PER_1K_TOKENS = 0.045
```

## ⚠️ Important Considerations

### Cost Management
- **LLM API calls can be expensive** - start with `--quick` flag
- Monitor token usage and costs during development
- Consider using `gpt-3.5-turbo` for cost savings during testing

### API Requirements
- **OpenAI API key required** - get one at [platform.openai.com](https://platform.openai.com)
- Ensure sufficient API credits for evaluation runs
- Rate limits may affect larger evaluations

### Result Variability
- LLM responses may vary between runs (controlled by temperature)
- JSON parsing failures are handled with algorithmic fallbacks
- Multiple runs recommended for statistical significance

## 🤝 Contributing

This research framework is designed for:
- **AI researchers** studying collaboration patterns
- **Organizational behavior scientists** comparing AI to human teams  
- **Multi-agent system developers** optimizing team structures
- **LLM application developers** understanding coordination costs

## 📄 License

[Add your license here]

## 🙏 Acknowledgments

Built for research into AI collaboration patterns and their relationship to human organizational behavior.

---

**Ready to explore how AI agents collaborate?** Start with the quick test and dive into the fascinating world of LLM-powered multi-agent collaboration! 🤖🤝
