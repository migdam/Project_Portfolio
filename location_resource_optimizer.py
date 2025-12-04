#!/usr/bin/env python3
"""
Location-Based Resource Optimizer

Optimizes portfolio selection with location-specific resource constraints.
Handles distributed teams across multiple geographic sites.

Features:
- Multi-site resource pools (US, EU, APAC, etc.)
- Location-project assignment constraints
- Time zone considerations
- Site-specific capacity management
- Distributed team optimization

Author: Portfolio ML
Version: 1.0.0
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass
import numpy as np
from scipy.optimize import linprog


@dataclass
class LocationResource:
    """Resource pool at a specific location"""
    location: str
    resource_type: str
    capacity: float  # FTE capacity
    cost_multiplier: float = 1.0  # Relative cost (e.g., 1.2 for higher cost locations)
    time_zone: Optional[str] = None


@dataclass
class ProjectLocationRequirement:
    """Project with location-specific requirements"""
    project_id: str
    allowed_locations: List[str]  # Locations where project can be executed
    resource_requirements: Dict[str, float]  # {resource_type: FTE}
    priority_score: float
    strategic_value: float
    npv: float
    preferred_location: Optional[str] = None  # Preferred but not required


class LocationResourceOptimizer:
    """
    Optimizes portfolio with location-aware resource allocation
    
    Solves multi-site resource optimization:
    - Each location has its own resource pools
    - Projects can be assigned to specific locations
    - Resources cannot be shared across locations
    - Optimizes for maximum value under location constraints
    """
    
    def __init__(self):
        """Initialize location-based optimizer"""
        self.locations: Dict[str, Dict[str, LocationResource]] = {}  # {location: {resource_type: resource}}
        self.projects: Dict[str, ProjectLocationRequirement] = {}
    
    def add_location_resource(
        self,
        location: str,
        resource_type: str,
        capacity: float,
        cost_multiplier: float = 1.0,
        time_zone: Optional[str] = None
    ) -> None:
        """
        Add resource pool at a specific location
        
        Args:
            location: Geographic location (e.g., 'US', 'EU', 'APAC')
            resource_type: Type of resource (e.g., 'Engineering', 'Design')
            capacity: FTE capacity at this location
            cost_multiplier: Relative cost multiplier (1.0 = baseline)
            time_zone: Time zone for coordination considerations
        """
        if location not in self.locations:
            self.locations[location] = {}
        
        self.locations[location][resource_type] = LocationResource(
            location=location,
            resource_type=resource_type,
            capacity=capacity,
            cost_multiplier=cost_multiplier,
            time_zone=time_zone
        )
    
    def add_project(
        self,
        project_id: str,
        allowed_locations: List[str],
        resource_requirements: Dict[str, float],
        priority_score: float,
        strategic_value: float = 0.0,
        npv: float = 0.0,
        preferred_location: Optional[str] = None
    ) -> None:
        """
        Add project with location constraints
        
        Args:
            project_id: Unique project identifier
            allowed_locations: List of locations where project can execute
            resource_requirements: Dict of {resource_type: FTE_needed}
            priority_score: Priority score (0-100)
            strategic_value: Strategic alignment score
            npv: Net Present Value
            preferred_location: Preferred (but not required) location
        """
        self.projects[project_id] = ProjectLocationRequirement(
            project_id=project_id,
            allowed_locations=allowed_locations,
            resource_requirements=resource_requirements,
            priority_score=priority_score,
            strategic_value=strategic_value,
            npv=npv,
            preferred_location=preferred_location
        )
    
    def optimize(
        self,
        objective: str = 'maximize_value',
        prefer_local_resources: bool = True,
        max_projects: Optional[int] = None
    ) -> Dict:
        """
        Optimize portfolio with location constraints
        
        Args:
            objective: Optimization objective
                - 'maximize_value': Maximize NPV + strategic value
                - 'maximize_npv': Maximize NPV only
                - 'minimize_cost': Minimize total cost (prefer low-cost locations)
            prefer_local_resources: Bonus for using preferred locations
            max_projects: Maximum number of projects to select
        
        Returns:
            Optimization results with location assignments
        """
        if not self.projects:
            return {
                'status': 'ERROR',
                'message': 'No projects to optimize'
            }
        
        # Build optimization problem
        # Decision variables: x[project_id][location] = 1 if project assigned to location, 0 otherwise
        
        n_projects = len(self.projects)
        project_list = list(self.projects.keys())
        
        # Create flattened decision variables: one per (project, location) pair
        decision_vars = []
        var_map = {}  # {(project_id, location): var_index}
        
        for i, project_id in enumerate(project_list):
            project = self.projects[project_id]
            for location in project.allowed_locations:
                var_index = len(decision_vars)
                decision_vars.append((project_id, location))
                var_map[(project_id, location)] = var_index
        
        n_vars = len(decision_vars)
        
        # Objective function coefficients
        c = np.zeros(n_vars)
        
        for idx, (project_id, location) in enumerate(decision_vars):
            project = self.projects[project_id]
            
            if objective == 'maximize_value':
                # Combine NPV and strategic value
                value = project.npv + project.strategic_value
            elif objective == 'maximize_npv':
                value = project.npv
            else:  # minimize_cost
                # Use cost multiplier (higher multiplier = higher cost)
                total_cost = sum(
                    self.locations[location][res_type].cost_multiplier * fte
                    for res_type, fte in project.resource_requirements.items()
                    if location in self.locations and res_type in self.locations[location]
                )
                value = -total_cost
            
            # Bonus for preferred location
            if prefer_local_resources and project.preferred_location == location:
                value *= 1.1
            
            # Negate for maximization (linprog minimizes)
            c[idx] = -value
        
        # Build constraint matrices
        A_ub = []
        b_ub = []
        A_eq = []
        b_eq = []
        
        # Constraint 1: Each project assigned to at most one location
        for project_id in project_list:
            constraint = np.zeros(n_vars)
            for location in self.projects[project_id].allowed_locations:
                if (project_id, location) in var_map:
                    constraint[var_map[(project_id, location)]] = 1
            A_ub.append(constraint)
            b_ub.append(1)  # Sum <= 1 (can choose not to select project)
        
        # Constraint 2: Location resource capacity
        for location in self.locations:
            for resource_type in self.locations[location]:
                constraint = np.zeros(n_vars)
                
                for idx, (proj_id, proj_loc) in enumerate(decision_vars):
                    if proj_loc == location:
                        project = self.projects[proj_id]
                        if resource_type in project.resource_requirements:
                            constraint[idx] = project.resource_requirements[resource_type]
                
                capacity = self.locations[location][resource_type].capacity
                A_ub.append(constraint)
                b_ub.append(capacity)
        
        # Constraint 3: Maximum projects (if specified)
        if max_projects is not None:
            # Sum of all decision variables <= max_projects
            # But each project can only be in one location, so we need to be careful
            # Create a constraint that ensures total unique projects <= max_projects
            
            # This is tricky with multiple locations per project
            # For now, use approximate: sum of all vars <= max_projects
            constraint = np.ones(n_vars)
            A_ub.append(constraint)
            b_ub.append(max_projects)
        
        # Variable bounds: binary
        bounds = [(0, 1) for _ in range(n_vars)]
        
        # Integer constraints
        integrality = np.ones(n_vars)
        
        # Solve
        try:
            result = linprog(
                c=c,
                A_ub=np.array(A_ub) if A_ub else None,
                b_ub=np.array(b_ub) if b_ub else None,
                A_eq=np.array(A_eq) if A_eq else None,
                b_eq=np.array(b_eq) if b_eq else None,
                bounds=bounds,
                method='highs',
                integrality=integrality
            )
            
            if not result.success:
                return {
                    'status': 'ERROR',
                    'message': f'Optimization failed: {result.message}'
                }
            
            # Extract results
            selected_projects = {}
            location_assignments = {}
            
            for idx, (project_id, location) in enumerate(decision_vars):
                if result.x[idx] > 0.5:  # Selected
                    selected_projects[project_id] = location
                    location_assignments[project_id] = location
            
            # Calculate metrics
            total_npv = sum(
                self.projects[pid].npv 
                for pid in selected_projects
            )
            
            total_strategic_value = sum(
                self.projects[pid].strategic_value 
                for pid in selected_projects
            )
            
            # Calculate resource utilization by location
            location_utilization = {}
            
            for location in self.locations:
                location_utilization[location] = {}
                
                for resource_type in self.locations[location]:
                    capacity = self.locations[location][resource_type].capacity
                    used = 0.0
                    
                    for project_id, assigned_location in location_assignments.items():
                        if assigned_location == location:
                            project = self.projects[project_id]
                            if resource_type in project.resource_requirements:
                                used += project.resource_requirements[resource_type]
                    
                    location_utilization[location][resource_type] = {
                        'capacity': capacity,
                        'used': used,
                        'utilization_pct': (used / capacity * 100) if capacity > 0 else 0,
                        'available': capacity - used
                    }
            
            # Calculate projects by location
            projects_by_location = {}
            for project_id, location in location_assignments.items():
                if location not in projects_by_location:
                    projects_by_location[location] = []
                projects_by_location[location].append(project_id)
            
            return {
                'status': 'SUCCESS',
                'selected_projects': list(selected_projects.keys()),
                'location_assignments': location_assignments,
                'num_selected': len(selected_projects),
                'total_npv': total_npv,
                'total_strategic_value': total_strategic_value,
                'location_utilization': location_utilization,
                'projects_by_location': projects_by_location,
                'objective_value': -result.fun  # Negate back
            }
            
        except Exception as e:
            return {
                'status': 'ERROR',
                'message': f'Optimization error: {str(e)}'
            }
    
    def get_location_summary(self) -> Dict:
        """Get summary of location resources and constraints"""
        summary = {
            'num_locations': len(self.locations),
            'locations': {}
        }
        
        for location, resources in self.locations.items():
            summary['locations'][location] = {
                'resource_types': list(resources.keys()),
                'total_capacity': sum(r.capacity for r in resources.values()),
                'resources': {
                    res_type: {
                        'capacity': res.capacity,
                        'cost_multiplier': res.cost_multiplier,
                        'time_zone': res.time_zone
                    }
                    for res_type, res in resources.items()
                }
            }
        
        # Project distribution
        projects_by_allowed_locations = {}
        for project_id, project in self.projects.items():
            key = tuple(sorted(project.allowed_locations))
            if key not in projects_by_allowed_locations:
                projects_by_allowed_locations[key] = []
            projects_by_allowed_locations[key].append(project_id)
        
        summary['project_distribution'] = {
            str(locs): len(projs)
            for locs, projs in projects_by_allowed_locations.items()
        }
        
        return summary
    
    def validate_feasibility(self) -> Dict:
        """
        Validate that portfolio is feasible with location constraints
        
        Returns:
            Validation results with potential issues
        """
        issues = []
        
        # Check if each project has at least one valid location
        for project_id, project in self.projects.items():
            valid_locations = []
            
            for location in project.allowed_locations:
                if location not in self.locations:
                    issues.append({
                        'type': 'INVALID_LOCATION',
                        'project_id': project_id,
                        'location': location,
                        'message': f'Location {location} not defined in resource pools'
                    })
                    continue
                
                # Check if location has required resource types
                has_all_resources = all(
                    res_type in self.locations[location]
                    for res_type in project.resource_requirements
                )
                
                if not has_all_resources:
                    missing = [
                        res_type for res_type in project.resource_requirements
                        if res_type not in self.locations[location]
                    ]
                    issues.append({
                        'type': 'MISSING_RESOURCES',
                        'project_id': project_id,
                        'location': location,
                        'missing_resources': missing,
                        'message': f'Location {location} missing resources: {missing}'
                    })
                else:
                    valid_locations.append(location)
            
            if not valid_locations:
                issues.append({
                    'type': 'NO_VALID_LOCATION',
                    'project_id': project_id,
                    'message': f'Project {project_id} has no valid location assignments'
                })
        
        return {
            'is_feasible': len(issues) == 0,
            'num_issues': len(issues),
            'issues': issues
        }
