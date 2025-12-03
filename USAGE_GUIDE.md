# Portfolio Deep Agent - Usage Guide

## Quick Start: Choose Your Mode

The Portfolio Deep Agent supports two modes of operation:

### 🔧 Rule-Based Mode (Fast, Free)
- ✅ No API key required
- ✅ 50-100ms per analysis
- ✅ Zero cost
- ✅ Threshold-based logic
- ✅ Perfect for real-time monitoring

### 🧠 LLM-Powered Mode (Intelligent, Context-Aware)
- 🔑 Requires OpenAI API key
- ⏱️ 2-5 seconds per analysis
- 💰 ~$0.03-0.06 per analysis
- 🎯 GPT-4 reasoning
- 📊 Root cause analysis + narrative

## Usage Examples

### Option 1: Rule-Based Analysis (Default)

**Command Line:**
```bash
# No API key needed - uses rule-based automatically
python demo_llm_agent.py
```

**Python Code:**
```python
from langgraph_agent import PortfolioAgent

# Explicitly use rule-based mode
agent = PortfolioAgent(use_llm=False)
result = agent.analyze("PROJ-042")

print(f"Risk: {result['risk_analysis']['risk_score']}")
print(f"Recommendations: {len(result['recommendations'])}")
```

**Output Example:**
```
Risk Score: 55/100 (MEDIUM)
Risk Factors:
   • Timeline pressure
Recommendations:
   1. [MEDIUM] 🤖 AUTO schedule_review
      Schedule bi-weekly review with stakeholders
```

---

### Option 2: LLM-Powered Analysis

**Command Line:**
```bash
# Set API key
export OPENAI_API_KEY="sk-your-key-here"

# Run with LLM
python demo_llm_agent.py --use-llm
```

**Python Code:**
```python
from langgraph_agent import PortfolioAgent
import os

# Use LLM mode with API key
api_key = os.getenv("OPENAI_API_KEY")
agent = PortfolioAgent(api_key=api_key, use_llm=True)
result = agent.analyze("PROJ-042")

print(f"Risk: {result['risk_analysis']['risk_score']}")
print(f"LLM Assessment: {result['risk_analysis']['llm_assessment']}")
print(f"Recommendations: {len(result['recommendations'])}")
```

**Output Example:**
```
Risk Score: 73/100 (HIGH)
LLM Assessment: Critical trajectory requiring immediate intervention...
Risk Factors:
   • Sprint velocity declining 35% over last 3 months 
     (Cause: Team burnout from overtime + 2 departures, Likelihood: HIGH)
Recommendations:
   1. [HIGH] 👤 MANUAL immediate_staffing_review
      Conduct urgent staffing assessment within 48hrs. Focus on 
      critical-path roles (backend lead, DevOps).
```

---

### Option 3: Compare Both Modes Side-by-Side

**Command Line:**
```bash
# Compare rule-based vs LLM (if API key set)
python demo_llm_agent.py --compare
```

**Output:**
- Shows rule-based analysis first
- Shows LLM analysis second (if API key available)
- Highlights key differences
- Tests 3 project patterns: escalating, volatile, stable

---

### Option 4: Batch Portfolio Analysis

**Rule-Based (Fast):**
```python
from langgraph_agent import PortfolioAgent

agent = PortfolioAgent(use_llm=False)
results = agent.batch_analyze_portfolio(hours=24)

for result in results:
    print(f"{result['project_id']}: {result['risk_analysis']['risk_level']}")
```

**LLM-Powered (Deep Insights):**
```python
from langgraph_agent import PortfolioAgent
import os

api_key = os.getenv("OPENAI_API_KEY")
agent = PortfolioAgent(api_key=api_key, use_llm=True)
results = agent.batch_analyze_portfolio(hours=24)

for result in results:
    if result['risk_analysis']['risk_score'] > 60:
        print(f"{result['project_id']}: {result['risk_analysis']['llm_assessment']}")
```

---

### Option 5: Hybrid Approach (Recommended)

Combine both modes for optimal speed + intelligence:

```python
from langgraph_agent import PortfolioAgent
import os

# Create both agents
agent_fast = PortfolioAgent(use_llm=False)
agent_smart = PortfolioAgent(api_key=os.getenv("OPENAI_API_KEY"), use_llm=True)

# Fast scan entire portfolio
all_results = agent_fast.batch_analyze_portfolio(hours=24)

# Deep dive only high-risk projects
high_risk_projects = [r for r in all_results if r['risk_analysis']['risk_score'] > 60]

print(f"Found {len(high_risk_projects)} high-risk projects")

for project in high_risk_projects:
    # Get detailed LLM analysis for high-risk only
    deep_analysis = agent_smart.analyze(project['project_id'])
    
    print(f"\n🚨 {project['project_id']}")
    print(f"LLM Assessment: {deep_analysis['risk_analysis']['llm_assessment']}")
    print("Recommendations:")
    for rec in deep_analysis['recommendations'][:3]:
        print(f"  • [{rec['priority']}] {rec['action']}")
```

**Benefits:**
- ⚡ Fast: Rule-based for full portfolio scan
- 🧠 Intelligent: LLM for critical decisions
- 💰 Cost-effective: Only pay for high-risk analysis
- 📊 Best of both worlds

---

## Command Reference

### Demo Scripts

```bash
# Rule-based analysis (no API key)
python demo_llm_agent.py

# LLM-powered analysis (requires API key)
export OPENAI_API_KEY="sk-..."
python demo_llm_agent.py --use-llm

# Compare both modes
python demo_llm_agent.py --compare

# Single project via CLI
python langgraph_agent.py PROJ-042
```

### Environment Variables

```bash
# Set OpenAI API key for LLM mode
export OPENAI_API_KEY="sk-your-key-here"

# Verify it's set
echo $OPENAI_API_KEY
```

### Python API

```python
# Import
from langgraph_agent import PortfolioAgent

# Rule-based (no API key)
agent = PortfolioAgent(use_llm=False)

# LLM-powered (with API key)
agent = PortfolioAgent(api_key="sk-...", use_llm=True)

# LLM with auto-detection (uses LLM if API key available)
agent = PortfolioAgent(api_key=os.getenv("OPENAI_API_KEY"))

# Analyze single project
result = agent.analyze("PROJ-042")

# Batch analyze recent projects
results = agent.batch_analyze_portfolio(hours=24)
```

---

## Decision Matrix: Which Mode to Use?

| Scenario | Recommended Mode | Why |
|----------|------------------|-----|
| Real-time dashboard | Rule-Based | Speed + no cost |
| Low-risk monitoring (score < 40) | Rule-Based | Threshold detection sufficient |
| High-frequency polling | Rule-Based | Can't afford 2-5s latency |
| Offline/air-gapped systems | Rule-Based | No API access |
| Cost-sensitive environment | Rule-Based | Zero cost |
| **High-risk projects (score > 60)** | **LLM-Powered** | **Need root cause analysis** |
| **Executive reports** | **LLM-Powered** | **Need narrative explanation** |
| **Strategic decisions** | **LLM-Powered** | **Context-aware insights** |
| **Complex multi-factor risks** | **LLM-Powered** | **Pattern recognition** |
| **Root cause investigation** | **LLM-Powered** | **Deep reasoning required** |
| **Large portfolio (100+ projects)** | **Hybrid** | **Fast scan + deep dive** |

---

## Performance Comparison

### Speed
```
Rule-Based:  50-100ms per project  →  1,000 projects = 50-100 seconds
LLM-Powered: 2-5s per project      →  1,000 projects = 33-83 minutes
Hybrid:      100ms + 2s (20% high) →  1,000 projects = 6-7 minutes
```

### Cost (100 Projects/Day)
```
Rule-Based:  $0/month
LLM (100%):  $90-180/month
Hybrid (20%): $18-36/month  ✅ RECOMMENDED
```

### Output Quality

**Rule-Based:**
- ✅ Fast threshold detection
- ✅ Consistent responses
- ❌ Generic recommendations
- ❌ No root cause analysis

**LLM-Powered:**
- ✅ Specific risk factors
- ✅ Root cause identification
- ✅ Context-aware recommendations
- ✅ Narrative assessment
- ❌ Slower (2-5s)
- ❌ Costs money

---

## Troubleshooting

### "OPENAI_API_KEY not set" Error

```bash
# Check if set
echo $OPENAI_API_KEY

# If empty, set it
export OPENAI_API_KEY="sk-your-key-here"

# Or use rule-based mode instead
python demo_llm_agent.py  # No --use-llm flag
```

### LLM Not Working (Falling Back to Rule-Based)

The agent automatically falls back to rule-based if:
- API key not set or invalid
- Network connectivity issues
- API rate limiting
- LLM response timeout (>30s)

**Check logs:**
```python
result = agent.analyze("PROJ-042")
assessment = result['risk_analysis'].get('llm_assessment', '')

if assessment == "LLM analysis unavailable":
    print("⚠️  LLM failed, used rule-based fallback")
```

### Slow Performance with LLM

**Solutions:**
1. Use hybrid approach (rule-based scan + LLM for high-risk)
2. Cache results (1-hour TTL)
3. Batch process overnight
4. Reserve LLM for manual deep-dives only

---

## Best Practices

### ✅ DO:
- Use rule-based for real-time monitoring
- Use LLM for high-risk projects (score > 60)
- Implement hybrid approach for large portfolios
- Cache LLM results for 1 hour
- Log LLM usage and costs
- Set budget alerts for API usage

### ❌ DON'T:
- Use LLM for every project in real-time dashboard
- Use rule-based for executive reports
- Ignore cost optimization strategies
- Retry LLM calls on failure (use fallback)
- Use LLM in latency-critical paths

---

## Examples by Use Case

### Use Case 1: Daily Portfolio Health Check
```python
# Fast scan all projects
agent = PortfolioAgent(use_llm=False)
results = agent.batch_analyze_portfolio(hours=24)

alerts = [r for r in results if r['risk_analysis']['risk_score'] > 70]
print(f"🚨 {len(alerts)} projects need attention")
```

### Use Case 2: Weekly Executive Report
```python
# Deep analysis for executive summary
import os
agent = PortfolioAgent(api_key=os.getenv("OPENAI_API_KEY"), use_llm=True)

high_risk = ["PROJ-042", "PROJ-103", "PROJ-207"]
for pid in high_risk:
    result = agent.analyze(pid)
    print(f"\n{pid}: {result['risk_analysis']['llm_assessment']}")
```

### Use Case 3: Continuous Monitoring Dashboard
```python
# Real-time updates every 5 seconds
agent = PortfolioAgent(use_llm=False)

while True:
    results = agent.batch_analyze_portfolio(hours=1)
    update_dashboard(results)
    time.sleep(5)
```

### Use Case 4: Project Gate Review
```python
# Deep dive for gate approval
import os
agent_llm = PortfolioAgent(api_key=os.getenv("OPENAI_API_KEY"), use_llm=True)

result = agent_llm.analyze("PROJ-GATE-REVIEW-042")
print(f"Risk Assessment: {result['risk_analysis']['llm_assessment']}")
print("\nRecommendations for gate approval:")
for rec in result['recommendations']:
    print(f"  • {rec['description']}")
```

---

## Summary

**Rule-Based Mode:**
```bash
python demo_llm_agent.py          # Fast, free, threshold-based
```

**LLM-Powered Mode:**
```bash
export OPENAI_API_KEY="sk-..."
python demo_llm_agent.py --use-llm  # Intelligent, context-aware
```

**Hybrid Mode (Recommended):**
```python
# Fast scan + smart deep-dive
agent_fast = PortfolioAgent(use_llm=False)
agent_smart = PortfolioAgent(api_key=api_key, use_llm=True)
```

Choose the right tool for the job! 🚀
