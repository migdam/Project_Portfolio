"""Portfolio Optimizer - Recommends optimal project portfolio."""

from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from scipy.optimize import linprog

from .base import BaseModel
from utils.logger import setup_logger

logger = setup_logger(__name__)


class PortfolioOptimizer(BaseModel):
    """Optimizes project portfolio selection given constraints."""
    
    def __init__(self, config: Dict):
        """
        Initialize Portfolio Optimizer.
        
        Args:
            config: Configuration dictionary
        """
        super().__init__("po", config)
        self.is_trained = True  # Optimizer doesn't require traditional training
    
    def optimize(
        self,
        projects_df: pd.DataFrame,
        budget_constraint: float,
        resource_constraint: float,
        value_column: str = "strategic_value_score",
        cost_column: str = "project_npv",
        resource_column: str = "resource_requirements",
        risk_column: str = "risk_score"
    ) -> Dict[str, Any]:
        """
        Optimize portfolio selection.
        
        Args:
            projects_df: DataFrame with project data
            budget_constraint: Maximum budget available
            resource_constraint: Maximum resources available
            value_column: Column name for value/benefit
            cost_column: Column name for cost
            resource_column: Column name for resource requirements
            risk_column: Column name for risk scores
            
        Returns:
            Dictionary with optimization results
        """
        logger.info("Running portfolio optimization...")
        
        n_projects = len(projects_df)
        
        # Extract values
        values = projects_df[value_column].values
        costs = projects_df[cost_column].abs().values  # Ensure positive
        resources = projects_df[resource_column].values
        risks = projects_df[risk_column].values if risk_column in projects_df.columns else np.zeros(n_projects)
        
        # Risk-adjusted value (penalize high-risk projects)
        risk_penalty = 1 - (risks / 100)  # Scale risk 0-1
        adjusted_values = values * risk_penalty
        
        # Objective: Maximize value (minimize negative value)
        c = -adjusted_values
        
        # Constraints
        # Budget constraint: sum(costs * x) <= budget
        # Resource constraint: sum(resources * x) <= resources
        A_ub = np.vstack([costs, resources])
        b_ub = np.array([budget_constraint, resource_constraint])
        
        # Bounds: each project is either selected (1) or not (0)
        bounds = [(0, 1) for _ in range(n_projects)]
        
        # Solve linear program
        result = linprog(
            c, A_ub=A_ub, b_ub=b_ub, bounds=bounds,
            method='highs'
        )
        
        if result.success:
            # Select projects with x > 0.5 (handle fractional solutions)
            selected = result.x > 0.5
            selected_projects = projects_df[selected].copy()
            
            total_value = selected_projects[value_column].sum()
            total_cost = selected_projects[cost_column].abs().sum()
            total_resources = selected_projects[resource_column].sum()
            avg_risk = risks[selected].mean() if risks.sum() > 0 else 0
            
            optimization_results = {
                "success": True,
                "selected_projects": selected_projects["project_id"].tolist() if "project_id" in selected_projects else list(range(len(selected_projects))),
                "n_selected": int(selected.sum()),
                "total_value": float(total_value),
                "total_cost": float(total_cost),
                "total_resources": float(total_resources),
                "avg_risk": float(avg_risk),
                "value_cost_ratio": float(total_value / total_cost) if total_cost > 0 else 0,
                "budget_utilization": float(total_cost / budget_constraint),
                "resource_utilization": float(total_resources / resource_constraint)
            }
            
            logger.info(f"Optimization successful: {selected.sum()} projects selected")
            logger.info(f"Total value: {total_value:.2f}, Total cost: {total_cost:.2f}")
            logger.info(f"Value/Cost ratio: {optimization_results['value_cost_ratio']:.2f}")
            
        else:
            optimization_results = {
                "success": False,
                "message": "Optimization failed - infeasible constraints or numerical issues"
            }
            logger.error("Portfolio optimization failed")
        
        return optimization_results
    
    def simulate_scenarios(
        self,
        projects_df: pd.DataFrame,
        budget_scenarios: List[float],
        resource_scenarios: List[float],
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Run optimization across multiple budget/resource scenarios.
        
        Args:
            projects_df: DataFrame with project data
            budget_scenarios: List of budget constraints to test
            resource_scenarios: List of resource constraints to test
            **kwargs: Additional parameters for optimize()
            
        Returns:
            List of optimization results for each scenario
        """
        logger.info(f"Running {len(budget_scenarios)} x {len(resource_scenarios)} scenarios...")
        
        results = []
        
        for budget in budget_scenarios:
            for resources in resource_scenarios:
                scenario_result = self.optimize(
                    projects_df,
                    budget_constraint=budget,
                    resource_constraint=resources,
                    **kwargs
                )
                scenario_result["budget_scenario"] = budget
                scenario_result["resource_scenario"] = resources
                results.append(scenario_result)
        
        logger.info(f"Completed {len(results)} scenario simulations")
        return results
    
    def get_pareto_frontier(
        self,
        projects_df: pd.DataFrame,
        budget_range: Tuple[float, float],
        n_points: int = 10,
        **kwargs
    ) -> pd.DataFrame:
        """
        Calculate Pareto frontier of value vs. cost trade-offs.
        
        Args:
            projects_df: DataFrame with project data
            budget_range: Tuple of (min_budget, max_budget)
            n_points: Number of points to calculate
            **kwargs: Additional parameters for optimize()
            
        Returns:
            DataFrame with Pareto frontier results
        """
        logger.info("Calculating Pareto frontier...")
        
        budgets = np.linspace(budget_range[0], budget_range[1], n_points)
        
        # Use maximum resources (no resource constraint for Pareto)
        max_resources = projects_df[kwargs.get("resource_column", "resource_requirements")].sum() * 2
        
        frontier_results = []
        
        for budget in budgets:
            result = self.optimize(
                projects_df,
                budget_constraint=budget,
                resource_constraint=max_resources,
                **kwargs
            )
            
            if result["success"]:
                frontier_results.append({
                    "budget": budget,
                    "value": result["total_value"],
                    "cost": result["total_cost"],
                    "n_projects": result["n_selected"],
                    "value_cost_ratio": result["value_cost_ratio"]
                })
        
        pareto_df = pd.DataFrame(frontier_results)
        logger.info(f"Pareto frontier calculated with {len(pareto_df)} points")
        
        return pareto_df
    
    # Implement required base class methods (not used for optimizer)
    def train(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """Not applicable for optimizer."""
        logger.info("Portfolio Optimizer does not require training")
        return {"message": "No training required"}
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Not applicable for optimizer."""
        raise NotImplementedError("Use optimize() method instead")
    
    def predict_with_confidence(self, X: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Not applicable for optimizer."""
        raise NotImplementedError("Use optimize() method instead")
