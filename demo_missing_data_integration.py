#!/usr/bin/env python3
"""
Demo: Missing Data Handler Integration with Portfolio Agent

Shows real-world usage of missing data handling in portfolio analysis pipeline.
"""

import numpy as np
from database import PortfolioDB
from missing_data_handler import MissingDataHandler
from langgraph_agent import PortfolioAgent

def generate_projects_with_varying_quality():
    """Generate test projects with different data quality levels"""
    
    db = PortfolioDB("portfolio_predictions.db")
    
    # Project 1: HIGH quality (all fields present)
    for i in range(3):
        db.store_prediction(
            project_id="PROJ-HIGH-QUALITY",
            risk_score=int(65 + i*2),
            cost_variance=float(12.0 + i*0.5),
            success_probability=float(0.85 - i*0.02)
        )
    
    # Project 2: MEDIUM quality (some fields missing but has history)
    for i in range(3):
        db.store_prediction(
            project_id="PROJ-MEDIUM-QUALITY",
            risk_score=int(75 + i*3),
            cost_variance=float(18.0 + i*1.0),
            success_probability=None  # Missing!
        )
    
    # Project 3: NEW project (minimal history, no optional fields)
    db.store_prediction(
        project_id="PROJ-NEW",
        risk_score=55,
        cost_variance=8.0,
        success_probability=None
    )
    
    print("✓ Generated test projects with varying data quality\n")

def analyze_with_quality_awareness():
    """Demonstrate quality-aware portfolio analysis"""
    
    db = PortfolioDB("portfolio_predictions.db")
    handler = MissingDataHandler(db)
    agent = PortfolioAgent(use_llm=False, db_path="portfolio_predictions.db")
    
    print("=" * 80)
    print("📊 PORTFOLIO ANALYSIS WITH MISSING DATA HANDLING")
    print("=" * 80)
    
    projects = ["PROJ-HIGH-QUALITY", "PROJ-MEDIUM-QUALITY", "PROJ-NEW"]
    
    for project_id in projects:
        print(f"\n{'─' * 80}")
        print(f"🔍 Analyzing: {project_id}")
        print('─' * 80)
        
        # Fetch latest data
        predictions = db.get_predictions(project_id=project_id, hours=1)
        if not predictions:
            print(f"⚠️  No data found for {project_id}")
            continue
        
        latest = predictions[0]
        project_data = {
            'project_id': latest.get('project_id'),
            'risk_score': latest.get('risk_score'),
            'cost_variance': latest.get('cost_variance'),
            'success_probability': latest.get('success_probability'),
            'budget': None,  # Simulate missing metadata
            'team_size': None,
            'duration_months': None
        }
        
        # Step 1: Assess data quality
        quality = handler.assess_data_quality(project_data)
        
        print(f"\n📋 Data Quality:")
        print(f"   Completeness: {quality['completeness']:.1%}")
        print(f"   Quality Level: {quality['quality_level']}")
        print(f"   Missing Fields: {len(quality['missing_fields'])}")
        
        # Step 2: Handle missing data
        result = handler.analyze_with_missing_data(project_data)
        
        if result['status'] != 'SUCCESS':
            print(f"\n❌ Cannot analyze: {result['message']}")
            continue
        
        # Step 3: Show imputation details
        if result['imputation_log']:
            print(f"\n🔧 Imputed Fields:")
            for field, method in result['imputation_log'].items():
                print(f"   • {field}: {method}")
        
        # Step 4: Run agent analysis with imputed data
        print(f"\n🤖 Agent Analysis:")
        imputed_data = result['imputed_data']
        
        # Display risk with quality indicator
        risk_score = imputed_data['risk_score']
        risk_level = "CRITICAL" if risk_score > 80 else "HIGH" if risk_score > 60 else "MEDIUM" if risk_score > 40 else "LOW"
        
        print(f"   Risk Score: {risk_score} ({risk_level})")
        print(f"   Cost Variance: {imputed_data['cost_variance']:.1f}%")
        print(f"   Success Probability: {imputed_data['success_probability']:.1%}")
        
        # Adjust confidence based on quality
        base_confidence = 0.85
        adjusted_confidence = base_confidence * (1 - quality['confidence_penalty'])
        
        print(f"\n📊 Confidence:")
        print(f"   Base: {base_confidence:.1%}")
        print(f"   Adjusted: {adjusted_confidence:.1%}")
        if quality['confidence_penalty'] > 0:
            print(f"   Penalty: -{quality['confidence_penalty']:.1%} (due to {quality['quality_level']} data quality)")
        
        # Step 5: Display warnings
        if result['warnings']:
            print(f"\n⚠️  Warnings:")
            for warning in result['warnings']:
                print(f"   {warning}")
        
        # Step 6: Recommendations based on quality
        print(f"\n💡 Recommendations:")
        if quality['quality_level'] == 'HIGH':
            print(f"   ✅ High confidence - proceed with analysis")
        elif quality['quality_level'] == 'MEDIUM':
            print(f"   ⚠️  Medium confidence - verify imputed values")
            print(f"   ⚠️  Consider improving data collection for: {', '.join(result['imputation_log'].keys())}")
        else:
            print(f"   ❌ Low confidence - require data improvement before critical decisions")

def show_portfolio_health():
    """Generate and display portfolio data quality report"""
    
    db = PortfolioDB("portfolio_predictions.db")
    handler = MissingDataHandler(db)
    
    print("\n\n" + "=" * 80)
    print("📊 PORTFOLIO DATA QUALITY HEALTH CHECK")
    print("=" * 80)
    
    report = handler.get_portfolio_data_quality_report(hours=720)
    
    print(f"\nTotal Projects Analyzed: {report['total_projects']}")
    print(f"Overall Portfolio Health: {report['overall_portfolio_health']}")
    
    print(f"\n📈 Quality Distribution:")
    for level in ['HIGH', 'MEDIUM', 'LOW', 'INSUFFICIENT']:
        count = report['quality_distribution'][level]
        pct = report['quality_percentage'][level]
        
        # Visual bar
        bar_length = int(pct / 2)  # Scale to 50 chars max
        bar = '█' * bar_length
        
        print(f"   {level:12s}: {count:3d} ({pct:5.1f}%) {bar}")
    
    if report['top_missing_fields']:
        print(f"\n🔍 Most Commonly Missing Fields:")
        for field, count in report['top_missing_fields']:
            pct = (count / report['total_projects'] * 100) if report['total_projects'] > 0 else 0
            print(f"   • {field:20s}: {count:3d} projects ({pct:.1f}%)")
    
    if report['projects_needing_improvement']:
        print(f"\n⚠️  Projects Requiring Data Improvement (Top 5):")
        seen = set()
        count = 0
        for proj in report['projects_needing_improvement']:
            if proj['project_id'] not in seen:
                seen.add(proj['project_id'])
                print(f"   {count+1}. {proj['project_id']:20s} - {proj['quality_level']:12s} ({proj['completeness']:.0%} complete)")
                count += 1
                if count >= 5:
                    break
    
    # Recommendations based on portfolio health
    print(f"\n💡 Portfolio-Level Recommendations:")
    
    health = report['overall_portfolio_health']
    insufficient_pct = report['quality_percentage']['INSUFFICIENT']
    medium_low_pct = report['quality_percentage']['MEDIUM'] + report['quality_percentage']['LOW']
    
    if health == 'EXCELLENT':
        print(f"   ✅ Excellent data quality - continue current practices")
    elif health == 'GOOD':
        print(f"   ✅ Good data quality - minor improvements recommended")
    elif health == 'FAIR':
        print(f"   ⚠️  Fair data quality - focus on improving data collection")
        if medium_low_pct > 50:
            print(f"   ⚠️  {medium_low_pct:.0f}% of projects have MEDIUM/LOW quality - prioritize data completeness")
    else:  # POOR
        print(f"   ❌ Poor data quality - immediate action required")
        if insufficient_pct > 20:
            print(f"   ❌ {insufficient_pct:.0f}% of projects cannot be analyzed - critical data gaps")
    
    # Specific action items
    print(f"\n🎯 Action Items:")
    for field, count in report['top_missing_fields'][:3]:
        pct = (count / report['total_projects'] * 100) if report['total_projects'] > 0 else 0
        if pct > 50:
            print(f"   • Implement mandatory collection of '{field}' field")
        elif pct > 25:
            print(f"   • Improve '{field}' data collection processes")

def main():
    print("=" * 80)
    print("🚀 Portfolio ML - Missing Data Integration Demo")
    print("=" * 80)
    print()
    
    # Step 1: Generate test data
    print("📦 Step 1: Generating test projects...")
    generate_projects_with_varying_quality()
    
    # Step 2: Analyze with quality awareness
    print("🔍 Step 2: Quality-aware analysis...")
    analyze_with_quality_awareness()
    
    # Step 3: Portfolio health report
    print("\n📊 Step 3: Portfolio health check...")
    show_portfolio_health()
    
    print("\n\n" + "=" * 80)
    print("✅ Demo Complete!")
    print("=" * 80)
    print("\n💡 Key Takeaways:")
    print("   • Always assess data quality before analysis")
    print("   • Adjust confidence scores based on completeness")
    print("   • Display warnings to users about imputed data")
    print("   • Monitor portfolio-level data quality trends")
    print("   • Target improvements for frequently missing fields")
    print()

if __name__ == "__main__":
    main()
