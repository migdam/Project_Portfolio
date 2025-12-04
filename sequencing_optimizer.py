#!/usr/bin/env python3
"""
Project Sequencing Optimizer with Dependency Management

Optimizes project execution sequence considering:
- Project dependencies (topological ordering)
- Resource leveling over time
- Critical path analysis
- Timeline optimization for maximum impact

Uses:
- Topological sort for dependency resolution
- Critical path method (CPM) for scheduling
- Resource-constrained scheduling

Author: Portfolio ML
Version: 1.0.0
"""

from typing import Dict, List, Optional, Tuple, Set
from collections import defaultdict, deque
from dataclasses import dataclass
import numpy as np


@dataclass
class Project:
    """Project with dependencies and resource requirements"""
    project_id: str
    duration_months: int
    priority_score: float
    dependencies: List[str]  # List of project IDs that must complete first
    resource_requirements: Dict[str, float]  # {resource_type: FTE_months}
    strategic_value: float = 0.0
    npv: float = 0.0
    
    def __hash__(self):
        return hash(self.project_id)


class SequencingOptimizer:
    """
    Optimizes project execution sequence with dependency management
    
    Features:
    - Topological sort for valid execution order
    - Critical path calculation
    - Resource leveling
    - Timeline optimization
    """
    
    def __init__(self):
        """Initialize the sequencing optimizer"""
        self.projects: Dict[str, Project] = {}
        self.dependency_graph: Dict[str, List[str]] = defaultdict(list)
        self.reverse_dependencies: Dict[str, Set[str]] = defaultdict(set)
    
    def add_project(
        self,
        project_id: str,
        duration_months: int,
        priority_score: float,
        dependencies: List[str] = None,
        resource_requirements: Dict[str, float] = None,
        strategic_value: float = 0.0,
        npv: float = 0.0
    ) -> None:
        """
        Add a project to the portfolio
        
        Args:
            project_id: Unique project identifier
            duration_months: Project duration in months
            priority_score: Priority score (0-100)
            dependencies: List of project IDs that must complete first
            resource_requirements: Dict of {resource_type: FTE_months}
            strategic_value: Strategic alignment score
            npv: Net Present Value
        """
        dependencies = dependencies or []
        resource_requirements = resource_requirements or {}
        
        project = Project(
            project_id=project_id,
            duration_months=duration_months,
            priority_score=priority_score,
            dependencies=dependencies,
            resource_requirements=resource_requirements,
            strategic_value=strategic_value,
            npv=npv
        )
        
        self.projects[project_id] = project
        
        # Build dependency graph
        for dep in dependencies:
            self.dependency_graph[dep].append(project_id)
            self.reverse_dependencies[project_id].add(dep)
    
    def validate_dependencies(self) -> Tuple[bool, Optional[str]]:
        """
        Validate that dependencies form a valid DAG (no cycles)
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        visited = set()
        rec_stack = set()
        
        def has_cycle(node: str) -> bool:
            """DFS to detect cycles"""
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in self.dependency_graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        # Check all nodes
        for project_id in self.projects:
            if project_id not in visited:
                if has_cycle(project_id):
                    return False, f"Circular dependency detected involving {project_id}"
        
        # Check for missing dependencies
        for project_id, project in self.projects.items():
            for dep in project.dependencies:
                if dep not in self.projects:
                    return False, f"Project {project_id} depends on non-existent project {dep}"
        
        return True, None
    
    def topological_sort(self) -> List[str]:
        """
        Perform topological sort to get valid execution order
        
        Returns:
            List of project IDs in valid execution order
        """
        # Calculate in-degree for each node
        in_degree = {pid: len(self.reverse_dependencies.get(pid, set())) 
                     for pid in self.projects}
        
        # Queue of projects with no dependencies
        queue = deque([pid for pid, degree in in_degree.items() if degree == 0])
        sorted_order = []
        
        while queue:
            # Among projects with no remaining dependencies, pick highest priority
            current = max(queue, key=lambda p: self.projects[p].priority_score)
            queue.remove(current)
            sorted_order.append(current)
            
            # Reduce in-degree for dependent projects
            for dependent in self.dependency_graph.get(current, []):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        
        return sorted_order
    
    def calculate_critical_path(self) -> Dict[str, Dict]:
        """
        Calculate critical path using CPM (Critical Path Method)
        
        Returns:
            Dictionary with project scheduling info:
            - earliest_start: Earliest possible start month
            - earliest_finish: Earliest possible finish month
            - latest_start: Latest allowable start month
            - latest_finish: Latest allowable finish month
            - slack: Float time (months)
            - is_critical: Whether project is on critical path
        """
        schedule = {}
        
        # Forward pass: Calculate earliest start/finish
        sorted_projects = self.topological_sort()
        
        for project_id in sorted_projects:
            project = self.projects[project_id]
            
            # Earliest start is max of all dependency finish times
            if not project.dependencies:
                earliest_start = 0
            else:
                earliest_start = max(
                    schedule[dep]['earliest_finish'] 
                    for dep in project.dependencies
                )
            
            earliest_finish = earliest_start + project.duration_months
            
            schedule[project_id] = {
                'earliest_start': earliest_start,
                'earliest_finish': earliest_finish,
                'project_id': project_id,
                'duration': project.duration_months
            }
        
        # Project completion time
        if sorted_projects:
            total_duration = max(s['earliest_finish'] for s in schedule.values())
        else:
            total_duration = 0
        
        # Backward pass: Calculate latest start/finish
        for project_id in reversed(sorted_projects):
            project = self.projects[project_id]
            
            # Latest finish is min of all dependent project latest starts
            dependents = self.dependency_graph.get(project_id, [])
            if not dependents:
                latest_finish = total_duration
            else:
                latest_finish = min(
                    schedule[dep]['latest_start'] 
                    for dep in dependents
                )
            
            latest_start = latest_finish - project.duration_months
            
            schedule[project_id].update({
                'latest_start': latest_start,
                'latest_finish': latest_finish,
                'slack': latest_start - schedule[project_id]['earliest_start'],
                'is_critical': (latest_start == schedule[project_id]['earliest_start'])
            })
        
        return schedule
    
    def optimize_sequence(
        self,
        max_parallel_projects: int = 5,
        resource_constraints: Optional[Dict[str, float]] = None
    ) -> Dict:
        """
        Optimize project sequence with resource leveling
        
        Args:
            max_parallel_projects: Maximum concurrent projects
            resource_constraints: Dict of {resource_type: monthly_capacity}
        
        Returns:
            Optimized schedule with:
            - sequence: Ordered list of phases (each phase has parallel projects)
            - timeline: Project start/end dates
            - resource_utilization: Monthly resource usage
            - critical_path: Projects on critical path
            - total_duration: Total portfolio duration in months
        """
        # Validate dependencies
        is_valid, error = self.validate_dependencies()
        if not is_valid:
            return {
                'status': 'ERROR',
                'message': error
            }
        
        # Calculate critical path
        schedule = self.calculate_critical_path()
        
        # Identify critical path projects
        critical_path = [pid for pid, info in schedule.items() 
                        if info['is_critical']]
        
        # Build execution phases (projects that can run in parallel)
        phases = []
        remaining_projects = set(self.projects.keys())
        completed_projects = set()
        
        while remaining_projects:
            # Find projects whose dependencies are all completed
            ready_projects = [
                pid for pid in remaining_projects
                if all(dep in completed_projects 
                      for dep in self.projects[pid].dependencies)
            ]
            
            if not ready_projects:
                return {
                    'status': 'ERROR',
                    'message': 'Unable to schedule remaining projects (circular dependency)'
                }
            
            # Limit parallel execution
            phase_projects = sorted(
                ready_projects,
                key=lambda p: (
                    schedule[p]['is_critical'],  # Critical path first
                    -self.projects[p].priority_score  # Then by priority
                )
            )[:max_parallel_projects]
            
            phases.append(phase_projects)
            
            # Mark as completed
            for pid in phase_projects:
                remaining_projects.remove(pid)
                completed_projects.add(pid)
        
        # Calculate timeline with resource leveling
        timeline = {}
        current_month = 0
        
        for phase in phases:
            # Start all projects in phase at current month
            phase_duration = max(self.projects[pid].duration_months 
                               for pid in phase)
            
            for pid in phase:
                timeline[pid] = {
                    'start_month': current_month,
                    'end_month': current_month + self.projects[pid].duration_months,
                    'phase': len(timeline) // max_parallel_projects,
                    'parallel_projects': [p for p in phase if p != pid]
                }
            
            current_month += phase_duration
        
        # Calculate resource utilization
        resource_utilization = self._calculate_resource_utilization(
            timeline, resource_constraints
        )
        
        # Calculate value metrics
        total_value = sum(p.strategic_value + p.npv for p in self.projects.values())
        
        return {
            'status': 'SUCCESS',
            'phases': phases,
            'timeline': timeline,
            'critical_path': critical_path,
            'total_duration_months': current_month,
            'resource_utilization': resource_utilization,
            'total_strategic_value': sum(p.strategic_value for p in self.projects.values()),
            'total_npv': sum(p.npv for p in self.projects.values()),
            'num_projects': len(self.projects),
            'num_phases': len(phases),
            'schedule_details': schedule
        }
    
    def _calculate_resource_utilization(
        self,
        timeline: Dict,
        resource_constraints: Optional[Dict[str, float]]
    ) -> Dict:
        """Calculate monthly resource utilization"""
        if not timeline:
            return {}
        
        max_month = max(info['end_month'] for info in timeline.values())
        
        # Track monthly usage by resource type
        monthly_usage = defaultdict(lambda: defaultdict(float))
        
        for project_id, times in timeline.items():
            project = self.projects[project_id]
            duration = times['end_month'] - times['start_month']
            
            for month in range(times['start_month'], times['end_month']):
                for resource_type, total_fte_months in project.resource_requirements.items():
                    # Distribute evenly across project duration
                    monthly_fte = total_fte_months / duration if duration > 0 else 0
                    monthly_usage[month][resource_type] += monthly_fte
        
        # Calculate utilization percentages
        utilization_summary = {}
        
        if resource_constraints:
            for resource_type, capacity in resource_constraints.items():
                max_usage = max(
                    monthly_usage[m].get(resource_type, 0)
                    for m in range(max_month)
                )
                avg_usage = np.mean([
                    monthly_usage[m].get(resource_type, 0)
                    for m in range(max_month)
                ])
                
                utilization_summary[resource_type] = {
                    'capacity': capacity,
                    'peak_usage': max_usage,
                    'avg_usage': avg_usage,
                    'peak_utilization_pct': (max_usage / capacity * 100) if capacity > 0 else 0,
                    'avg_utilization_pct': (avg_usage / capacity * 100) if capacity > 0 else 0,
                    'is_overallocated': max_usage > capacity
                }
        
        return {
            'monthly_usage': dict(monthly_usage),
            'summary': utilization_summary
        }
    
    def get_sequence_gantt_data(self, timeline: Dict) -> List[Dict]:
        """
        Get Gantt chart data for visualization
        
        Args:
            timeline: Timeline from optimize_sequence()
        
        Returns:
            List of dictionaries for Gantt chart visualization
        """
        gantt_data = []
        
        for project_id, times in timeline.items():
            project = self.projects[project_id]
            
            gantt_data.append({
                'project_id': project_id,
                'start_month': times['start_month'],
                'end_month': times['end_month'],
                'duration': times['end_month'] - times['start_month'],
                'dependencies': project.dependencies,
                'priority_score': project.priority_score,
                'parallel_projects': times['parallel_projects']
            })
        
        return sorted(gantt_data, key=lambda x: x['start_month'])
