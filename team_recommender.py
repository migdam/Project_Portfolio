#!/usr/bin/env python3
"""
Team Recommender

AI-powered team composition recommendations with:
- Skill matching engine
- Historical performance analysis  
- Availability tracking and workload balancing
- Learning curve consideration
- Alternative team suggestions with tradeoffs
- Skill gap identification

Author: Portfolio ML
Version: 1.0.0
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np


class SkillLevel(Enum):
    """Skill proficiency levels"""
    EXPERT = "Expert"
    ADVANCED = "Advanced"
    INTERMEDIATE = "Intermediate"
    BASIC = "Basic"


class SeniorityLevel(Enum):
    """Team member seniority"""
    PRINCIPAL = "Principal"
    SENIOR = "Senior"
    MID_LEVEL = "Mid-Level"
    JUNIOR = "Junior"


@dataclass
class Skill:
    """Skill with proficiency level"""
    name: str
    level: SkillLevel
    years_experience: float


@dataclass
class Person:
    """Person with skills and availability"""
    person_id: str
    name: str
    role: str
    seniority: SeniorityLevel
    skills: List[Skill]
    location: str
    current_utilization: float  # 0-100%
    cost_per_month: float
    performance_score: float  # Historical performance 0-100
    project_history: List[str]  # Project IDs
    availability_start_month: int = 0


@dataclass
class TeamMember:
    """Recommended team member"""
    person: Person
    allocation: float  # FTE (0-1)
    rationale: str
    skill_match_score: float


@dataclass
class TeamRecommendation:
    """Complete team recommendation"""
    team_members: List[TeamMember]
    overall_skill_match: float  # 0-100
    total_cost: float
    predicted_performance: float  # 0-100
    risk_factors: List[str]
    strengths: List[str]
    skill_gaps: List[str]
    team_size_fte: float
    confidence: float  # 0-100


class TeamRecommender:
    """
    AI-powered team composition recommender
    
    Recommends optimal team composition based on:
    - Project requirements
    - Available resources
    - Historical performance patterns
    - Skill matching
    - Workload balancing
    """
    
    def __init__(self, historical_data: Optional[Dict] = None):
        """
        Initialize team recommender
        
        Args:
            historical_data: Optional historical project-team performance data
        """
        self.historical_data = historical_data or {}
        self.skill_matcher = SkillMatcher()
        self.performance_analyzer = PerformanceAnalyzer(historical_data)
    
    def recommend_team(
        self,
        project_requirements: Dict,
        available_resources: List[Person],
        optimization_objective: str = 'balanced'
    ) -> List[TeamRecommendation]:
        """
        Generate team recommendations
        
        Args:
            project_requirements: Dict with:
                - required_skills: List[Dict] - {skill: str, level: str}
                - duration_months: int
                - project_complexity: str (HIGH, MEDIUM, LOW)
                - project_type: str
                - budget_constraint: float (optional)
            available_resources: List of Person objects
            optimization_objective: 'cost', 'quality', 'balanced'
        
        Returns:
            List of TeamRecommendation objects (primary + alternatives)
        """
        # Extract requirements
        required_skills = project_requirements.get('required_skills', [])
        duration_months = project_requirements.get('duration_months', 12)
        complexity = project_requirements.get('project_complexity', 'MEDIUM')
        project_type = project_requirements.get('project_type', 'Standard')
        budget_constraint = project_requirements.get('budget_constraint')
        
        # Determine team size based on complexity
        target_team_size = self._estimate_team_size(complexity, duration_months, project_type)
        
        # Score all candidates against requirements
        candidate_scores = []
        for person in available_resources:
            skill_match = self.skill_matcher.calculate_skill_match(
                person.skills,
                required_skills
            )
            
            # Availability check
            if person.current_utilization > 85:
                availability_penalty = 0.5
            elif person.current_utilization > 70:
                availability_penalty = 0.8
            else:
                availability_penalty = 1.0
            
            # Performance score
            perf_score = person.performance_score / 100.0
            
            # Calculate composite score
            composite_score = (
                skill_match * 0.5 +
                perf_score * 0.3 +
                availability_penalty * 0.2
            )
            
            candidate_scores.append({
                'person': person,
                'skill_match': skill_match,
                'composite_score': composite_score,
                'availability_penalty': availability_penalty
            })
        
        # Sort by composite score
        candidate_scores.sort(key=lambda x: x['composite_score'], reverse=True)
        
        # Generate primary recommendation
        primary_team = self._build_team(
            candidate_scores,
            required_skills,
            target_team_size,
            duration_months,
            budget_constraint,
            optimization_objective
        )
        
        # Generate alternative recommendations
        alternatives = []
        
        # Alternative 1: Cost-optimized
        if optimization_objective != 'cost':
            alt_cost = self._build_team(
                candidate_scores,
                required_skills,
                target_team_size,
                duration_months,
                budget_constraint,
                'cost'
            )
            if alt_cost and alt_cost.team_members != primary_team.team_members:
                alternatives.append(alt_cost)
        
        # Alternative 2: Quality-optimized
        if optimization_objective != 'quality':
            alt_quality = self._build_team(
                candidate_scores,
                required_skills,
                target_team_size,
                duration_months,
                budget_constraint,
                'quality'
            )
            if alt_quality and alt_quality.team_members != primary_team.team_members:
                alternatives.append(alt_quality)
        
        return [primary_team] + alternatives
    
    def _estimate_team_size(
        self,
        complexity: str,
        duration_months: int,
        project_type: str
    ) -> float:
        """Estimate optimal team size in FTE"""
        
        # Base team size by complexity
        complexity_factors = {
            'HIGH': 8.0,
            'MEDIUM': 5.0,
            'LOW': 3.0
        }
        
        base_size = complexity_factors.get(complexity, 5.0)
        
        # Adjust for project type
        if 'Technology' in project_type or 'Digital' in project_type:
            base_size *= 1.2
        
        # Adjust for duration (longer projects may need smaller sustained teams)
        if duration_months > 18:
            base_size *= 0.9
        elif duration_months < 6:
            base_size *= 1.1
        
        return round(base_size, 1)
    
    def _build_team(
        self,
        candidate_scores: List[Dict],
        required_skills: List[Dict],
        target_team_size: float,
        duration_months: int,
        budget_constraint: Optional[float],
        optimization: str
    ) -> TeamRecommendation:
        """Build a team based on optimization objective"""
        
        team_members = []
        total_fte = 0.0
        covered_skills = set()
        total_cost = 0.0
        
        # Sort candidates based on optimization objective
        if optimization == 'cost':
            candidates = sorted(candidate_scores, key=lambda x: x['person'].cost_per_month)
        elif optimization == 'quality':
            candidates = sorted(candidate_scores, key=lambda x: x['person'].performance_score, reverse=True)
        else:  # balanced
            candidates = candidate_scores.copy()
        
        # Select team members
        for candidate in candidates:
            if total_fte >= target_team_size:
                break
            
            person = candidate['person']
            
            # Check if person adds value (new skills or critical role)
            person_skills = {skill.name for skill in person.skills}
            required_skill_names = {rs['skill'] for rs in required_skills}
            
            new_skills = person_skills & required_skill_names - covered_skills
            
            # Determine allocation
            remaining_capacity = 1.0 - (person.current_utilization / 100.0)
            needed_fte = min(remaining_capacity, target_team_size - total_fte)
            
            if needed_fte > 0.1:  # At least 10% allocation
                allocation = min(needed_fte, 1.0)
                
                member_cost = person.cost_per_month * allocation * duration_months
                
                # Check budget constraint
                if budget_constraint and (total_cost + member_cost) > budget_constraint:
                    continue
                
                # Add to team
                rationale = self._generate_rationale(person, new_skills, candidate['skill_match'])
                
                team_members.append(TeamMember(
                    person=person,
                    allocation=allocation,
                    rationale=rationale,
                    skill_match_score=candidate['skill_match'] * 100
                ))
                
                total_fte += allocation
                covered_skills.update(person_skills)
                total_cost += member_cost
        
        # Calculate team metrics
        overall_skill_match = self._calculate_team_skill_match(
            team_members,
            required_skills
        )
        
        predicted_performance = self._predict_team_performance(team_members)
        
        risk_factors = self._identify_risk_factors(
            team_members,
            required_skills,
            covered_skills
        )
        
        strengths = self._identify_strengths(team_members)
        
        skill_gaps = self._identify_skill_gaps(
            required_skills,
            covered_skills
        )
        
        confidence = self._calculate_confidence(
            overall_skill_match,
            len(skill_gaps),
            len(risk_factors)
        )
        
        return TeamRecommendation(
            team_members=team_members,
            overall_skill_match=overall_skill_match,
            total_cost=total_cost,
            predicted_performance=predicted_performance,
            risk_factors=risk_factors,
            strengths=strengths,
            skill_gaps=skill_gaps,
            team_size_fte=total_fte,
            confidence=confidence
        )
    
    def _generate_rationale(
        self,
        person: Person,
        new_skills: set,
        skill_match: float
    ) -> str:
        """Generate rationale for including person"""
        
        reasons = []
        
        if skill_match > 0.8:
            reasons.append(f"Strong skill match ({skill_match*100:.0f}%)")
        
        if person.performance_score > 85:
            reasons.append("Proven high performer")
        
        if new_skills:
            skills_str = ", ".join(list(new_skills)[:3])
            reasons.append(f"Brings: {skills_str}")
        
        if person.seniority in [SeniorityLevel.SENIOR, SeniorityLevel.PRINCIPAL]:
            reasons.append(f"{person.seniority.value} expertise")
        
        if person.current_utilization < 50:
            reasons.append("Good availability")
        
        if not reasons:
            reasons.append("Supports team composition")
        
        return "; ".join(reasons)
    
    def _calculate_team_skill_match(
        self,
        team_members: List[TeamMember],
        required_skills: List[Dict]
    ) -> float:
        """Calculate overall team skill match"""
        
        if not required_skills:
            return 100.0
        
        # Aggregate team skills
        team_skill_levels = {}
        for member in team_members:
            for skill in member.person.skills:
                skill_name = skill.name
                skill_value = self._skill_level_to_value(skill.level) * member.allocation
                
                if skill_name in team_skill_levels:
                    team_skill_levels[skill_name] = max(
                        team_skill_levels[skill_name],
                        skill_value
                    )
                else:
                    team_skill_levels[skill_name] = skill_value
        
        # Check each required skill
        total_score = 0.0
        for req_skill in required_skills:
            skill_name = req_skill['skill']
            required_level = req_skill.get('level', 'Intermediate')
            required_value = self._skill_level_to_value(
                SkillLevel[required_level.upper().replace('-', '_')]
            )
            
            team_value = team_skill_levels.get(skill_name, 0)
            
            # Score: 100% if met or exceeded, proportional if partial
            skill_score = min(team_value / required_value, 1.0) * 100
            total_score += skill_score
        
        return total_score / len(required_skills)
    
    def _skill_level_to_value(self, level: SkillLevel) -> float:
        """Convert skill level to numeric value"""
        level_values = {
            SkillLevel.BASIC: 1.0,
            SkillLevel.INTERMEDIATE: 2.0,
            SkillLevel.ADVANCED: 3.0,
            SkillLevel.EXPERT: 4.0
        }
        return level_values.get(level, 2.0)
    
    def _predict_team_performance(self, team_members: List[TeamMember]) -> float:
        """Predict team performance score"""
        
        if not team_members:
            return 50.0
        
        # Weighted average of individual performance scores
        total_weight = sum(m.allocation for m in team_members)
        weighted_performance = sum(
            m.person.performance_score * m.allocation
            for m in team_members
        )
        
        avg_performance = weighted_performance / total_weight if total_weight > 0 else 70.0
        
        # Team composition bonus
        seniority_levels = {m.person.seniority for m in team_members}
        if len(seniority_levels) >= 3:  # Good mix of seniority
            avg_performance *= 1.05
        
        # Team size penalty (too small or too large)
        total_fte = sum(m.allocation for m in team_members)
        if total_fte < 2:
            avg_performance *= 0.9  # Too small
        elif total_fte > 15:
            avg_performance *= 0.95  # Too large
        
        return min(avg_performance, 100.0)
    
    def _identify_risk_factors(
        self,
        team_members: List[TeamMember],
        required_skills: List[Dict],
        covered_skills: set
    ) -> List[str]:
        """Identify team risks"""
        
        risks = []
        
        # Check for overallocation
        for member in team_members:
            total_util = member.person.current_utilization + (member.allocation * 100)
            if total_util > 100:
                risks.append(f"{member.person.name} over-allocated ({total_util:.0f}%)")
            elif total_util > 90:
                risks.append(f"{member.person.name} near capacity ({total_util:.0f}%)")
        
        # Check for skill gaps
        required_skill_names = {rs['skill'] for rs in required_skills}
        missing_skills = required_skill_names - covered_skills
        if missing_skills:
            skills_str = ", ".join(list(missing_skills)[:3])
            risks.append(f"Skill gaps: {skills_str}")
        
        # Check for single points of failure
        critical_skills = [rs['skill'] for rs in required_skills if rs.get('critical', False)]
        for critical_skill in critical_skills:
            team_with_skill = [
                m for m in team_members
                if critical_skill in {s.name for s in m.person.skills}
            ]
            if len(team_with_skill) == 1:
                risks.append(f"Single expert for critical skill: {critical_skill}")
        
        # Check team size
        total_fte = sum(m.allocation for m in team_members)
        if total_fte < 2:
            risks.append("Team size too small (risk of delays)")
        elif total_fte > 12:
            risks.append("Team size large (coordination overhead)")
        
        # Check seniority balance
        senior_fte = sum(
            m.allocation for m in team_members
            if m.person.seniority in [SeniorityLevel.SENIOR, SeniorityLevel.PRINCIPAL]
        )
        if senior_fte < total_fte * 0.3:
            risks.append("Limited senior expertise")
        
        return risks
    
    def _identify_strengths(self, team_members: List[TeamMember]) -> List[str]:
        """Identify team strengths"""
        
        strengths = []
        
        # High performers
        high_performers = [
            m for m in team_members
            if m.person.performance_score > 85
        ]
        if len(high_performers) >= 2:
            strengths.append(f"{len(high_performers)} proven high performers")
        
        # Good availability
        available_members = [
            m for m in team_members
            if m.person.current_utilization < 50
        ]
        if len(available_members) >= len(team_members) * 0.5:
            strengths.append("Good team availability")
        
        # Diverse seniority
        seniority_levels = {m.person.seniority for m in team_members}
        if len(seniority_levels) >= 3:
            strengths.append("Balanced seniority mix")
        
        # Experience with similar projects
        similar_project_members = [
            m for m in team_members
            if len(m.person.project_history) >= 3
        ]
        if len(similar_project_members) >= len(team_members) * 0.6:
            strengths.append("Experienced team members")
        
        # Strong skill coverage
        total_fte = sum(m.allocation for m in team_members)
        if total_fte >= 3 and len(team_members) >= 3:
            strengths.append("Strong team composition")
        
        return strengths
    
    def _identify_skill_gaps(
        self,
        required_skills: List[Dict],
        covered_skills: set
    ) -> List[str]:
        """Identify skill gaps"""
        
        required_skill_names = {rs['skill'] for rs in required_skills}
        missing = required_skill_names - covered_skills
        
        return [
            f"{skill} ({next((rs.get('level', 'Intermediate') for rs in required_skills if rs['skill'] == skill), 'Intermediate')})"
            for skill in missing
        ]
    
    def _calculate_confidence(
        self,
        skill_match: float,
        skill_gap_count: int,
        risk_count: int
    ) -> float:
        """Calculate recommendation confidence"""
        
        confidence = 80.0  # Base confidence
        
        # Adjust for skill match
        if skill_match > 90:
            confidence += 15
        elif skill_match > 75:
            confidence += 5
        elif skill_match < 60:
            confidence -= 20
        
        # Penalize for gaps
        confidence -= skill_gap_count * 5
        
        # Penalize for risks
        confidence -= risk_count * 3
        
        return max(min(confidence, 100.0), 30.0)


class SkillMatcher:
    """Matches person skills to requirements"""
    
    def calculate_skill_match(
        self,
        person_skills: List[Skill],
        required_skills: List[Dict]
    ) -> float:
        """
        Calculate skill match score (0-1)
        
        Args:
            person_skills: List of Skill objects
            required_skills: List of dicts with 'skill' and 'level'
        
        Returns:
            Match score from 0 to 1
        """
        if not required_skills:
            return 0.5  # Neutral score if no requirements
        
        person_skill_dict = {
            skill.name: skill for skill in person_skills
        }
        
        total_score = 0.0
        for req_skill in required_skills:
            skill_name = req_skill['skill']
            required_level = req_skill.get('level', 'Intermediate')
            
            if skill_name in person_skill_dict:
                person_skill = person_skill_dict[skill_name]
                level_match = self._compare_skill_levels(
                    person_skill.level,
                    SkillLevel[required_level.upper().replace('-', '_')]
                )
                total_score += level_match
            # else: score 0 for missing skill
        
        return total_score / len(required_skills)
    
    def _compare_skill_levels(
        self,
        person_level: SkillLevel,
        required_level: SkillLevel
    ) -> float:
        """Compare skill levels and return match score"""
        
        level_order = [
            SkillLevel.BASIC,
            SkillLevel.INTERMEDIATE,
            SkillLevel.ADVANCED,
            SkillLevel.EXPERT
        ]
        
        person_idx = level_order.index(person_level)
        required_idx = level_order.index(required_level)
        
        if person_idx >= required_idx:
            return 1.0  # Meets or exceeds requirement
        elif person_idx == required_idx - 1:
            return 0.7  # One level below
        elif person_idx == required_idx - 2:
            return 0.4  # Two levels below
        else:
            return 0.1  # Too far below


class PerformanceAnalyzer:
    """Analyzes historical team performance patterns"""
    
    def __init__(self, historical_data: Dict):
        """
        Initialize with historical data
        
        Args:
            historical_data: Dict with project outcomes and team compositions
        """
        self.historical_data = historical_data
    
    def analyze_team_compatibility(
        self,
        team_members: List[Person]
    ) -> Dict:
        """Analyze team compatibility based on history"""
        
        # Check if team members have worked together
        worked_together = self._find_collaboration_history(team_members)
        
        # Analyze past project success
        avg_success_rate = self._calculate_avg_success_rate(team_members)
        
        return {
            'worked_together_before': worked_together,
            'collaboration_count': len(worked_together),
            'avg_success_rate': avg_success_rate,
            'compatibility_score': self._calculate_compatibility_score(
                len(worked_together),
                avg_success_rate
            )
        }
    
    def _find_collaboration_history(
        self,
        team_members: List[Person]
    ) -> List[str]:
        """Find projects where team members worked together"""
        
        if len(team_members) < 2:
            return []
        
        # Find common projects
        project_sets = [set(person.project_history) for person in team_members]
        common_projects = set.intersection(*project_sets)
        
        return list(common_projects)
    
    def _calculate_avg_success_rate(
        self,
        team_members: List[Person]
    ) -> float:
        """Calculate average success rate from history"""
        
        # Use performance scores as proxy for success rate
        if not team_members:
            return 70.0
        
        return sum(p.performance_score for p in team_members) / len(team_members)
    
    def _calculate_compatibility_score(
        self,
        collaboration_count: int,
        avg_success_rate: float
    ) -> float:
        """Calculate team compatibility score"""
        
        base_score = avg_success_rate
        
        # Bonus for prior collaboration
        collaboration_bonus = min(collaboration_count * 5, 15)
        
        return min(base_score + collaboration_bonus, 100.0)


# Demo usage
if __name__ == '__main__':
    
    # Sample people
    people = [
        Person(
            person_id='P001',
            name='Jane Smith',
            role='Tech Lead',
            seniority=SeniorityLevel.SENIOR,
            skills=[
                Skill('Python', SkillLevel.EXPERT, 8),
                Skill('Machine Learning', SkillLevel.ADVANCED, 6),
                Skill('System Architecture', SkillLevel.EXPERT, 10)
            ],
            location='US',
            current_utilization=40,
            cost_per_month=15000,
            performance_score=92,
            project_history=['PROJ-001', 'PROJ-005', 'PROJ-012']
        ),
        Person(
            person_id='P002',
            name='John Doe',
            role='Senior Engineer',
            seniority=SeniorityLevel.SENIOR,
            skills=[
                Skill('Python', SkillLevel.ADVANCED, 5),
                Skill('NLP', SkillLevel.EXPERT, 4),
                Skill('API Development', SkillLevel.ADVANCED, 6)
            ],
            location='US',
            current_utilization=60,
            cost_per_month=12000,
            performance_score=88,
            project_history=['PROJ-003', 'PROJ-008']
        ),
        Person(
            person_id='P003',
            name='Alice Chen',
            role='Engineer',
            seniority=SeniorityLevel.MID_LEVEL,
            skills=[
                Skill('Python', SkillLevel.ADVANCED, 3),
                Skill('React', SkillLevel.EXPERT, 4),
                Skill('UI/UX', SkillLevel.INTERMEDIATE, 3)
            ],
            location='APAC',
            current_utilization=30,
            cost_per_month=8000,
            performance_score=85,
            project_history=['PROJ-010']
        )
    ]
    
    # Project requirements
    project_reqs = {
        'required_skills': [
            {'skill': 'Python', 'level': 'Advanced'},
            {'skill': 'Machine Learning', 'level': 'Advanced'},
            {'skill': 'NLP', 'level': 'Intermediate'},
            {'skill': 'API Development', 'level': 'Intermediate'}
        ],
        'duration_months': 12,
        'project_complexity': 'HIGH',
        'project_type': 'Digital Technology'
    }
    
    # Get recommendations
    recommender = TeamRecommender()
    recommendations = recommender.recommend_team(
        project_reqs,
        people,
        optimization_objective='balanced'
    )
    
    # Display results
    print("🎯 TEAM RECOMMENDATIONS\n")
    print("=" * 80)
    
    for i, rec in enumerate(recommendations):
        print(f"\n{'PRIMARY RECOMMENDATION' if i == 0 else f'ALTERNATIVE {i}'}:")
        print(f"Skill Match: {rec.overall_skill_match:.1f}%")
        print(f"Team Size: {rec.team_size_fte:.1f} FTE")
        print(f"Total Cost: ${rec.total_cost:,.0f}")
        print(f"Predicted Performance: {rec.predicted_performance:.1f}/100")
        print(f"Confidence: {rec.confidence:.1f}%")
        
        print(f"\nTeam Members:")
        for member in rec.team_members:
            print(f"  • {member.person.name} ({member.person.role})")
            print(f"    Allocation: {member.allocation*100:.0f}% | Skill Match: {member.skill_match_score:.0f}%")
            print(f"    Rationale: {member.rationale}")
        
        if rec.strengths:
            print(f"\n✅ Strengths:")
            for strength in rec.strengths:
                print(f"  • {strength}")
        
        if rec.risk_factors:
            print(f"\n⚠️  Risk Factors:")
            for risk in rec.risk_factors:
                print(f"  • {risk}")
        
        if rec.skill_gaps:
            print(f"\n🔴 Skill Gaps:")
            for gap in rec.skill_gaps:
                print(f"  • {gap}")
        
        print("\n" + "=" * 80)
