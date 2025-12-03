#!/usr/bin/env python3
"""
Demo: LLM-Powered Deep Agent Analysis

This script demonstrates how the Portfolio Agent uses GPT-4 for:
1. Deep risk factor analysis with root cause identification
2. Intelligent recommendation generation
3. Context-aware decision making

To run with LLM (requires OpenAI API key):
    export OPENAI_API_KEY="your-key-here"
    python demo_llm_agent.py --use-llm

To run without LLM (rule-based fallback):
    python demo_llm_agent.py
"""

import os
import argparse
from langgraph_agent import PortfolioAgent
from database import PortfolioDB
import numpy as np
from datetime import datetime, timedelta

def generate_test_data(db: PortfolioDB, project_id: str, risk_pattern: str):
    """Generate test data with specific risk patterns"""
    
    print(f"\n📊 Generating test data for {project_id} ({risk_pattern} pattern)...")
    
    if risk_pattern == "escalating":
        # Increasing risk over time
        for i in range(10):
            db.store_prediction(
                project_id=project_id,
                risk_score=int(40 + i * 5),  # 40 -> 85
                cost_variance=float(5 + i * 2.5),  # 5% -> 27.5%
                success_probability=float(0.9 - i * 0.05)  # 90% -> 40%
            )
    elif risk_pattern == "volatile":
        # High volatility
        for i in range(10):
            db.store_prediction(
                project_id=project_id,
                risk_score=int(np.random.choice([30, 75, 45, 80, 35, 85])),
                cost_variance=float(np.random.choice([-5, 20, 5, 25, -2, 30])),
                success_probability=float(np.random.uniform(0.4, 0.9))
            )
    elif risk_pattern == "stable":
        # Low risk, stable
        for i in range(10):
            db.store_prediction(
                project_id=project_id,
                risk_score=int(25 + np.random.randint(-5, 5)),
                cost_variance=float(np.random.uniform(-2, 3)),
                success_probability=float(0.95)
            )
    
    print(f"✓ Generated 10 data points")

def run_comparison_demo():
    """Run side-by-side comparison of rule-based vs LLM-powered analysis"""
    
    print("=" * 80)
    print("🤖 Portfolio Deep Agent Comparison Demo")
    print("=" * 80)
    
    # Setup
    db = PortfolioDB("demo_agent.db")
    api_key = os.getenv("OPENAI_API_KEY")
    
    # Test projects with different patterns
    test_cases = [
        ("PROJ-HIGH-RISK", "escalating"),
        ("PROJ-VOLATILE", "volatile"),
        ("PROJ-STABLE", "stable")
    ]
    
    for project_id, pattern in test_cases:
        generate_test_data(db, project_id, pattern)
    
    print("\n" + "=" * 80)
    print("COMPARISON: Rule-Based vs LLM-Powered Analysis")
    print("=" * 80)
    
    for project_id, pattern in test_cases:
        print(f"\n{'=' * 80}")
        print(f"📦 PROJECT: {project_id} ({pattern.upper()})")
        print('=' * 80)
        
        # Run RULE-BASED analysis
        print("\n🔧 RULE-BASED ANALYSIS (No LLM)")
        print("-" * 80)
        
        agent_rule_based = PortfolioAgent(db_path="demo_agent.db", use_llm=False)
        result_rule = agent_rule_based.analyze(project_id)
        
        print(f"Risk: {result_rule['risk_analysis']['risk_score']} ({result_rule['risk_analysis']['risk_level']})")
        print(f"Risk Factors:")
        for factor in result_rule['risk_analysis']['risk_factors']:
            print(f"  • {factor}")
        print(f"\nRecommendations ({len(result_rule['recommendations'])}):")
        for i, rec in enumerate(result_rule['recommendations'][:3], 1):
            print(f"  {i}. [{rec['priority']}] {rec['action']}")
            print(f"     {rec['description']}")
        
        # Run LLM-POWERED analysis
        if api_key:
            print(f"\n🧠 LLM-POWERED ANALYSIS (GPT-4)")
            print("-" * 80)
            
            agent_llm = PortfolioAgent(api_key=api_key, db_path="demo_agent.db", use_llm=True)
            result_llm = agent_llm.analyze(project_id)
            
            print(f"Risk: {result_llm['risk_analysis']['risk_score']} ({result_llm['risk_analysis']['risk_level']})")
            print(f"LLM Assessment: {result_llm['risk_analysis'].get('llm_assessment', 'N/A')}")
            print(f"Risk Factors:")
            for factor in result_llm['risk_analysis']['risk_factors']:
                print(f"  • {factor}")
            print(f"\nRecommendations ({len(result_llm['recommendations'])}):")
            for i, rec in enumerate(result_llm['recommendations'][:3], 1):
                print(f"  {i}. [{rec['priority']}] {rec['action']}")
                print(f"     {rec['description']}")
            
            print(f"\n💡 KEY DIFFERENCE:")
            print(f"   Rule-based: Generic recommendations based on thresholds")
            print(f"   LLM-powered: Context-aware, specific recommendations with reasoning")
        else:
            print(f"\n⚠️  Skipping LLM analysis - OPENAI_API_KEY not set")
    
    print("\n" + "=" * 80)
    print("✅ Demo Complete")
    print("=" * 80)
    
    if not api_key:
        print("\n💡 To see LLM-powered analysis:")
        print("   export OPENAI_API_KEY='your-key-here'")
        print("   python demo_llm_agent.py")

def run_single_analysis(use_llm: bool):
    """Run a single project analysis"""
    
    project_id = "DEMO-PROJECT-001"
    api_key = os.getenv("OPENAI_API_KEY")
    
    if use_llm and not api_key:
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("Set it with: export OPENAI_API_KEY='your-key-here'")
        return
    
    print("=" * 80)
    print(f"🤖 Portfolio Deep Agent - {'LLM-Powered' if use_llm else 'Rule-Based'}")
    print("=" * 80)
    
    # Generate test data
    db = PortfolioDB("demo_agent.db")
    generate_test_data(db, project_id, "escalating")
    
    # Create agent
    agent = PortfolioAgent(
        api_key=api_key if use_llm else None,
        db_path="demo_agent.db",
        use_llm=use_llm
    )
    
    print(f"\n🔍 Analyzing {project_id}...")
    print("-" * 80)
    
    result = agent.analyze(project_id)
    
    # Display results
    print(f"\n📊 ANALYSIS RESULTS")
    print("=" * 80)
    print(f"Project: {result['project_id']}")
    print(f"Risk Score: {result['risk_analysis']['risk_score']}/100 ({result['risk_analysis']['risk_level']})")
    print(f"Cost Overrun: {result['cost_analysis']['predicted_overrun']:.1f}% ({result['cost_analysis']['overrun_level']})")
    print(f"Confidence: {result['confidence']:.1%}")
    print(f"Escalate to Human: {'YES' if result['needs_human_review'] else 'NO'}")
    
    if use_llm and 'llm_assessment' in result['risk_analysis']:
        print(f"\n🧠 LLM Assessment:")
        print(f"   {result['risk_analysis']['llm_assessment']}")
    
    print(f"\n⚠️  Risk Factors:")
    for factor in result['risk_analysis']['risk_factors']:
        print(f"   • {factor}")
    
    print(f"\n💡 Recommendations:")
    for i, rec in enumerate(result['recommendations'], 1):
        auto_badge = "🤖 AUTO" if rec.get('automated') else "👤 MANUAL"
        print(f"   {i}. [{rec['priority']}] {auto_badge} {rec['action']}")
        print(f"      {rec['description']}")
    
    if result['actions_taken']:
        print(f"\n✅ Automated Actions Taken:")
        for action in result['actions_taken']:
            print(f"   • {action['action']}: {action['result']}")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Portfolio Deep Agent Demo")
    parser.add_argument(
        "--use-llm",
        action="store_true",
        help="Use LLM for deep reasoning (requires OPENAI_API_KEY)"
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Run side-by-side comparison of rule-based vs LLM"
    )
    
    args = parser.parse_args()
    
    if args.compare:
        run_comparison_demo()
    else:
        run_single_analysis(args.use_llm)
