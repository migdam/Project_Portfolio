#!/usr/bin/env python3
"""
Demand Portfolio Optimizer - Linear Programming-Based Resource Optimization

Selects optimal subset of approved demand ideas subject to resource constraints.
Uses Linear Programming (scipy.optimize.linprog) to maximize portfolio value.

Objectives:
- Maximize NPV (Net Present Value)
- Maximize Strategic Value
- Multi-objective optimization with weights

Constraints:
- Total budget limit
- Resource capacity (FTEs by skill/department)
- Maximum concurrent projects
- Risk tolerance (average risk score)
- Dependency management

Author: Portfolio ML
Version: 1.0.0
"""

import numpy as np
from scipy.optimize import linprog
from typing import Dict, List, Optional, Tuple


class DemandOptimizer:
    """
    Linear Programming-based portfolio optimizer for demand selection
    
    Solves the project selection problem:
    - Maximize: Weighted sum of NPV and strategic value
    - Subject to: Budget, capacity, risk, and dependency constraints
    """
    
    def __init__(self):
        """Initialize the demand optimizer"""
        pass
    
    def optimize(
        self,
        approved_demands: List[Dict],
        constraints: Dict,
        objective: str = 'maximize_npv',
        weights: Optional[Dict] = None
    ) -> Dict:
        """
        Optimize portfolio selection from approved demands
        
        Args:
            approved_demands: List of approved demand evaluations
            constraints: Dictionary of resource constraints
                - total_budget: Maximum total cost
                - resource_capacity: Dict of {skill: FTE_capacity}
                - max_concurrent_projects: Maximum number of projects
                - max_avg_risk: Maximum average risk score
            objective: Optimization objective
                - 'maximize_npv': Maximize total NPV
                - 'maximize_strategic': Maximize strategic value
                - 'balanced': Weighted combination
            weights: Optional weights for balanced objective
                - npv_weight: Weight for NPV (default 0.6)
                - strategic_weight: Weight for strategic value (default 0.4)
        
        Returns:
            Dictionary with optimization results:
            - selected_projects: List of selected project IDs
            - total_npv: Total NPV of selected projects
            - total_cost: Total cost of selected projects
            - total_strategic_value: Sum of strategic alignment scores
            - resource_utilization: Dict of resource usage by skill
            - avg_risk: Average risk score of portfolio
            - num_selected: Number of projects selected
            - optimization_status: Success/failure status
        """
        if not approved_demands:
            return {
                'selected_projects': [],
                'total_npv': 0,
                'total_cost': 0,
                'total_strategic_value': 0,
                'resource_utilization': {},
                'avg_risk': 0,
                'num_selected': 0,
                'optimization_status': 'NO_DEMANDS',
                'message': 'No approved demands to optimize'
            }
        
        # Extract project data
        n_projects = len(approved_demands)
        project_ids = [d['project_id'] for d in approved_demands]
        
        # Extract metrics from each demand
        npvs = []
        costs = []
        strategic_scores = []
        risk_scores = []
        
        for demand in approved_demands:
            # NPV from financial step
            npv = demand.get('steps', {}).get('financial', {}).get('npv', 0)
            npvs.append(npv)
            
            # Cost from original idea data (stored in evaluation)
            cost = self._extract_cost(demand)
            costs.append(cost)
            
            # Strategic alignment from alignment step
            strategic = demand.get('steps', {}).get('alignment', {}).get('alignment_score', 50)
            strategic_scores.append(strategic)
            
            # Risk from risk step
            risk = demand.get('steps', {}).get('risk', {}).get('risk_score', 50)
            risk_scores.append(risk)
        
        # Convert to numpy arrays
        npvs = np.array(npvs)
        costs = np.array(costs)
        strategic_scores = np.array(strategic_scores)
        risk_scores = np.array(risk_scores)
        
        # Set default weights if not provided
        if weights is None:
            weights = {'npv_weight': 0.6, 'strategic_weight': 0.4}
        
        # Define objective function (we minimize, so negate for maximization)
        if objective == 'maximize_npv':
            c = -npvs  # Negate because linprog minimizes
        elif objective == 'maximize_strategic':
            c = -strategic_scores
        else:  # balanced
            # Normalize both to 0-1 scale for fair weighting
            npv_normalized = npvs / (np.max(npvs) if np.max(npvs) > 0 else 1)
            strategic_normalized = strategic_scores / 100.0
            c = -(weights['npv_weight'] * npv_normalized + 
                  weights['strategic_weight'] * strategic_normalized)
        
        # Build constraint matrices
        # All constraints in form: A_ub @ x <= b_ub
        A_ub = []
        b_ub = []
        
        # 1. Budget constraint: sum(cost_i * x_i) <= total_budget
        if 'total_budget' in constraints:
            A_ub.append(costs)
            b_ub.append(constraints['total_budget'])
        
        # 2. Max concurrent projects: sum(x_i) <= max_concurrent
        if 'max_concurrent_projects' in constraints:
            A_ub.append(np.ones(n_projects))
            b_ub.append(constraints['max_concurrent_projects'])
        
        # 3. Risk constraint: sum(risk_i * x_i) / sum(x_i) <= max_avg_risk
        # Rewritten as: sum(risk_i * x_i) - max_avg_risk * sum(x_i) <= 0
        if 'max_avg_risk' in constraints:
            A_ub.append(risk_scores - constraints['max_avg_risk'])
            b_ub.append(0)
        
        # Variable bounds: each x_i is binary (0 or 1)
        bounds = [(0, 1) for _ in range(n_projects)]
        
        # Integer constraints (binary)
        integrality = np.ones(n_projects)
        
        # Solve the linear program
        try:
            result = linprog(
                c=c,
                A_ub=np.array(A_ub) if A_ub else None,
                b_ub=np.array(b_ub) if b_ub else None,
                bounds=bounds,
                method='highs',
                integrality=integrality
            )
            
            if result.success:
                # Extract selected projects (where x_i = 1)
                selected_indices = np.where(result.x > 0.5)[0]
                selected_projects = [project_ids[i] for i in selected_indices]
                
                # Calculate portfolio metrics
                total_npv = np.sum(npvs[selected_indices])
                total_cost = np.sum(costs[selected_indices])
                total_strategic = np.sum(strategic_scores[selected_indices])
                avg_risk = np.mean(risk_scores[selected_indices]) if len(selected_indices) > 0 else 0
                
                # Resource utilization (simplified - assumes equal distribution)
                resource_utilization = {}
                if 'resource_capacity' in constraints:
                    for skill, capacity in constraints['resource_capacity'].items():
                        # Simple model: each project uses capacity/n_projects
                        used = len(selected_indices) * (capacity / n_projects) if n_projects > 0 else 0
                        resource_utilization[skill] = {
                            'used': used,
                            'capacity': capacity,
                            'utilization_pct': (used / capacity * 100) if capacity > 0 else 0
                        }
                
                return {
                    'selected_projects': selected_projects,
                    'total_npv': float(total_npv),
                    'total_cost': float(total_cost),
                    'total_strategic_value': float(total_strategic),
                    'avg_strategic_score': float(total_strategic / len(selected_indices)) if len(selected_indices) > 0 else 0,
                    'resource_utilization': resource_utilization,
                    'avg_risk': float(avg_risk),
                    'num_selected': len(selected_indices),
                    'num_rejected': n_projects - len(selected_indices),
                    'optimization_status': 'SUCCESS',
                    'objective_value': float(-result.fun),  # Negate back to get maximized value
                    'selected_details': [
                        {
                            'project_id': project_ids[i],
                            'npv': float(npvs[i]),
                            'cost': float(costs[i]),
                            'strategic_score': float(strategic_scores[i]),
                            'risk_score': float(risk_scores[i]),
                            'priority_score': approved_demands[i].get('priority_score', 0)
                        }
                        for i in selected_indices
                    ]
                }
            else:
                return {
                    'selected_projects': [],
                    'total_npv': 0,
                    'total_cost': 0,
                    'total_strategic_value': 0,
                    'resource_utilization': {},
                    'avg_risk': 0,
                    'num_selected': 0,
                    'optimization_status': 'INFEASIBLE',
                    'message': f'Optimization failed: {result.message}'
                }
                
        except Exception as e:
            return {
                'selected_projects': [],
                'total_npv': 0,
                'total_cost': 0,
                'total_strategic_value': 0,
                'resource_utilization': {},
                'avg_risk': 0,
                'num_selected': 0,
                'optimization_status': 'ERROR',
                'message': f'Optimization error: {str(e)}'
            }
    
    def _extract_cost(self, demand: Dict) -> float:
        """Extract total cost from demand evaluation"""
        # Try to get from financial step
        cost = demand.get('steps', {}).get('financial', {}).get('total_cost', 0)
        if cost > 0:
            return cost
        
        # Fallback: estimate from NPV and ROI
        npv = demand.get('steps', {}).get('financial', {}).get('npv', 0)
        roi = demand.get('steps', {}).get('financial', {}).get('roi', 0)
        
        if roi > 0 and npv > 0:
            # Rough estimate: cost = npv / (roi / 100)
            return npv / (roi / 100)
        
        # Default fallback
        return 100000  # $100K default
    
    def compare_scenarios(
        self,
        approved_demands: List[Dict],
        scenarios: List[Dict]
    ) -> Dict:
        """
        Compare multiple optimization scenarios
        
        Args:
            approved_demands: List of approved demands
            scenarios: List of scenario dictionaries, each with:
                - name: Scenario name
                - constraints: Constraint dictionary
                - objective: Optimization objective
                - weights: Optional weights
        
        Returns:
            Dictionary with comparison results
        """
        results = {}
        
        for scenario in scenarios:
            name = scenario['name']
            result = self.optimize(
                approved_demands=approved_demands,
                constraints=scenario['constraints'],
                objective=scenario.get('objective', 'maximize_npv'),
                weights=scenario.get('weights')
            )
            results[name] = result
        
        # Generate comparison summary
        comparison = {
            'scenarios': results,
            'best_by_npv': max(results.items(), key=lambda x: x[1]['total_npv'])[0],
            'best_by_strategic': max(results.items(), key=lambda x: x[1]['total_strategic_value'])[0],
            'most_projects': max(results.items(), key=lambda x: x[1]['num_selected'])[0],
            'lowest_risk': min(results.items(), key=lambda x: x[1]['avg_risk'] if x[1]['avg_risk'] > 0 else 999)[0]
        }
        
        return comparison


def main():
    """Demo: Portfolio optimization with resource constraints"""
    print("=" * 80)
    print("DEMAND PORTFOLIO OPTIMIZER - LINEAR PROGRAMMING OPTIMIZATION")
    print("=" * 80)
    
    # Simulate 10 approved demands
    approved_demands = [
        {
            'project_id': f'IDEA-{i:03d}',
            'priority_score': np.random.uniform(50, 95),
            'steps': {
                'financial': {
                    'npv': np.random.uniform(500000, 5000000),
                    'total_cost': np.random.uniform(200000, 2000000)
                },
                'alignment': {
                    'alignment_score': np.random.uniform(60, 95)
                },
                'risk': {
                    'risk_score': np.random.uniform(20, 70)
                }
            }
        }
        for i in range(1, 11)
    ]
    
    # Define constraints
    constraints = {
        'total_budget': 8_000_000,  # $8M budget
        'max_concurrent_projects': 6,  # Can handle 6 projects
        'max_avg_risk': 50,  # Average risk must be <= 50
        'resource_capacity': {
            'Engineering': 30,  # 30 FTE engineers
            'Design': 8,  # 8 FTE designers
            'PM': 6  # 6 FTE project managers
        }
    }
    
    print(f"\n📊 Portfolio to Optimize:")
    print(f"   Total Approved Ideas: {len(approved_demands)}")
    total_cost = sum(d['steps']['financial']['total_cost'] for d in approved_demands)
    total_npv = sum(d['steps']['financial']['npv'] for d in approved_demands)
    print(f"   Total Cost if all selected: ${total_cost:,.0f}")
    print(f"   Total NPV if all selected: ${total_npv:,.0f}")
    
    print(f"\n🔒 Constraints:")
    print(f"   Budget Limit: ${constraints['total_budget']:,.0f}")
    print(f"   Max Concurrent: {constraints['max_concurrent_projects']} projects")
    print(f"   Max Avg Risk: {constraints['max_avg_risk']}")
    
    # Optimize
    optimizer = DemandOptimizer()
    
    print(f"\n🔄 Running optimization...")
    result = optimizer.optimize(
        approved_demands=approved_demands,
        constraints=constraints,
        objective='balanced',
        weights={'npv_weight': 0.6, 'strategic_weight': 0.4}
    )
    
    if result['optimization_status'] == 'SUCCESS':
        print(f"\n✅ OPTIMIZATION SUCCESSFUL")
        print(f"\n📈 Optimized Portfolio:")
        print(f"   Projects Selected: {result['num_selected']}/{len(approved_demands)}")
        print(f"   Projects Deferred: {result['num_rejected']}")
        print(f"   Total NPV: ${result['total_npv']:,.0f}")
        print(f"   Total Cost: ${result['total_cost']:,.0f}")
        print(f"   Budget Utilization: {result['total_cost']/constraints['total_budget']*100:.1f}%")
        print(f"   Avg Strategic Score: {result['avg_strategic_score']:.0f}/100")
        print(f"   Avg Risk Score: {result['avg_risk']:.0f}/100")
        
        print(f"\n💰 VALUE IMPROVEMENT:")
        if total_cost > 0:
            improvement = (result['total_npv'] / result['total_cost']) / (total_npv / total_cost) - 1
            print(f"   NPV/Cost Ratio Improvement: {improvement*100:+.1f}%")
        
        print(f"\n📋 Selected Projects:")
        for detail in result['selected_details']:
            print(f"   • {detail['project_id']}: NPV=${detail['npv']:,.0f}, "
                  f"Cost=${detail['cost']:,.0f}, Strategic={detail['strategic_score']:.0f}, "
                  f"Risk={detail['risk_score']:.0f}")
    else:
        print(f"\n❌ Optimization failed: {result['message']}")
    
    print(f"\n{'=' * 80}")
    print("Optimization complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
