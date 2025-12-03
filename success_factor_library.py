"""
Success Factor Library
Captures lessons learned and identifies success patterns for benefit realization
"""
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional
import json
import logging

logger = logging.getLogger(__name__)


class SuccessFactorLibrary:
    """
    Manages library of success factors and lessons learned:
    - Captures lessons from post-implementation reviews
    - Extracts success patterns from completed projects
    - Matches similar historical projects
    - Recommends best practices based on patterns
    """
    
    def __init__(self, db_path: str = "data/benefit_tracking.db"):
        """Initialize library with database connection"""
        self.db_path = db_path
    
    def capture_lesson(
        self,
        project_id: str,
        lesson_type: str,
        lesson_text: str,
        lesson_category: str,
        impact_level: str = "Medium",
        benefit_impact_pct: Optional[float] = None,
        captured_by: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict:
        """
        Capture a lesson learned from a project
        
        Args:
            project_id: Project identifier
            lesson_type: WhatWorked, WhatDidnt, Recommendation, RiskLearned
            lesson_text: Description of the lesson
            lesson_category: Planning, Execution, ChangeManagement, Technical, etc.
            impact_level: High, Medium, Low
            benefit_impact_pct: Estimated % impact on benefit realization
            captured_by: Who recorded the lesson
            tags: Optional list of tags
        
        Returns:
            Dict with status and lesson_id
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            tags_json = json.dumps(tags) if tags else None
            
            cursor.execute("""
                INSERT INTO project_lessons (
                    project_id, lesson_type, lesson_category, lesson_text,
                    impact_level, benefit_impact_pct, captured_date, captured_by, tags
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                project_id, lesson_type, lesson_category, lesson_text,
                impact_level, benefit_impact_pct, datetime.now().strftime('%Y-%m-%d'),
                captured_by, tags_json
            ))
            
            lesson_id = cursor.lastrowid
            conn.commit()
            
            return {
                'status': 'SUCCESS',
                'lesson_id': lesson_id,
                'project_id': project_id,
                'message': 'Lesson captured successfully'
            }
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error capturing lesson: {e}")
            return {
                'status': 'ERROR',
                'message': str(e)
            }
        finally:
            conn.close()
    
    def extract_success_patterns(
        self,
        min_success_rate: float = 90.0,
        min_sample_size: int = 3
    ) -> Dict:
        """
        Extract success patterns from high-performing projects
        
        Args:
            min_success_rate: Minimum realization rate to consider (default 90%)
            min_sample_size: Minimum number of projects to form a pattern
        
        Returns:
            Dict with identified patterns
        """
        conn = sqlite3.connect(self.db_path)
        
        # Get high-performing projects
        query = """
            SELECT 
                v.project_id,
                v.benefit_category,
                v.realization_rate
            FROM v_benefit_variance v
            WHERE v.realization_rate >= ?
        """
        
        high_performers = pd.read_sql_query(query, conn, params=[min_success_rate])
        
        if len(high_performers) < min_sample_size:
            conn.close()
            return {
                'status': 'INSUFFICIENT_DATA',
                'message': f'Need at least {min_sample_size} high performers, found {len(high_performers)}'
            }
        
        # Get lessons from these projects
        lesson_query = """
            SELECT 
                project_id,
                lesson_type,
                lesson_category,
                lesson_text,
                impact_level,
                benefit_impact_pct,
                tags
            FROM project_lessons
            WHERE project_id IN ({})
                AND lesson_type = 'WhatWorked'
        """.format(','.join(['?'] * len(high_performers)))
        
        lessons = pd.read_sql_query(
            lesson_query, 
            conn, 
            params=high_performers['project_id'].tolist()
        )
        
        conn.close()
        
        # Group by category and aggregate
        patterns = []
        
        if not lessons.empty:
            for category in lessons['lesson_category'].unique():
                category_lessons = lessons[lessons['lesson_category'] == category]
                
                # Extract common themes
                high_impact = category_lessons[category_lessons['impact_level'] == 'High']
                
                pattern = {
                    'pattern_category': category,
                    'project_count': len(category_lessons),
                    'avg_realization_rate': round(high_performers['realization_rate'].mean(), 1),
                    'key_lessons': category_lessons['lesson_text'].tolist()[:5],  # Top 5
                    'high_impact_factors': high_impact['lesson_text'].tolist()
                }
                
                patterns.append(pattern)
        
        # Create pattern summary
        pattern_summary = {
            'status': 'SUCCESS',
            'high_performer_count': len(high_performers),
            'avg_success_rate': round(high_performers['realization_rate'].mean(), 1),
            'lesson_count': len(lessons),
            'patterns_identified': len(patterns),
            'patterns': sorted(patterns, key=lambda x: x['project_count'], reverse=True)
        }
        
        return pattern_summary
    
    def match_similar_projects(
        self,
        new_project: Dict,
        top_n: int = 5
    ) -> Dict:
        """
        Find historical projects similar to a new project
        
        Args:
            new_project: Dict with project characteristics
                        {project_id, benefit_categories, budget, complexity, etc.}
            top_n: Number of similar projects to return
        
        Returns:
            Dict with similar projects and their lessons
        """
        conn = sqlite3.connect(self.db_path)
        
        # Get all completed projects with benefit data
        query = """
            SELECT DISTINCT
                v.project_id,
                v.benefit_category,
                AVG(v.realization_rate) as avg_realization_rate,
                COUNT(DISTINCT v.benefit_category) as category_count
            FROM v_benefit_variance v
            GROUP BY v.project_id
            HAVING AVG(v.realization_rate) > 0
        """
        
        historical = pd.read_sql_query(query, conn)
        
        if historical.empty:
            conn.close()
            return {
                'status': 'NO_DATA',
                'message': 'No historical projects available'
            }
        
        # Simple similarity: match by benefit categories
        new_categories = set(new_project.get('benefit_categories', []))
        
        similarities = []
        for _, proj in historical.iterrows():
            # Get categories for this project
            proj_query = """
                SELECT DISTINCT benefit_category
                FROM v_benefit_variance
                WHERE project_id = ?
            """
            proj_cats = pd.read_sql_query(proj_query, conn, params=[proj['project_id']])
            proj_categories = set(proj_cats['benefit_category'].tolist())
            
            # Calculate Jaccard similarity
            if new_categories and proj_categories:
                intersection = len(new_categories.intersection(proj_categories))
                union = len(new_categories.union(proj_categories))
                similarity = intersection / union if union > 0 else 0
            else:
                similarity = 0
            
            similarities.append({
                'project_id': proj['project_id'],
                'similarity_score': round(similarity, 3),
                'avg_realization_rate': round(proj['avg_realization_rate'], 1),
                'matching_categories': list(new_categories.intersection(proj_categories))
            })
        
        # Sort by similarity
        similarities = sorted(similarities, key=lambda x: (x['similarity_score'], x['avg_realization_rate']), reverse=True)
        top_matches = similarities[:top_n]
        
        # Get lessons from similar projects
        for match in top_matches:
            lesson_query = """
                SELECT lesson_type, lesson_text, impact_level
                FROM project_lessons
                WHERE project_id = ?
                ORDER BY 
                    CASE impact_level 
                        WHEN 'High' THEN 1 
                        WHEN 'Medium' THEN 2 
                        ELSE 3 
                    END
                LIMIT 3
            """
            lessons = pd.read_sql_query(lesson_query, conn, params=[match['project_id']])
            match['lessons'] = lessons.to_dict('records') if not lessons.empty else []
        
        conn.close()
        
        return {
            'status': 'SUCCESS',
            'new_project_id': new_project.get('project_id', 'Unknown'),
            'similar_projects_found': len(top_matches),
            'matches': top_matches
        }
    
    def recommend_best_practices(
        self,
        benefit_category: str,
        min_confidence: float = 0.7
    ) -> Dict:
        """
        Recommend best practices for a specific benefit category
        
        Args:
            benefit_category: Benefit category to get recommendations for
            min_confidence: Minimum confidence level for recommendations
        
        Returns:
            Dict with recommended practices
        """
        conn = sqlite3.connect(self.db_path)
        
        # Get successful projects in this category
        query = """
            SELECT DISTINCT
                v.project_id,
                v.realization_rate
            FROM v_benefit_variance v
            WHERE v.benefit_category = ?
                AND v.realization_rate >= 90
        """
        
        successful = pd.read_sql_query(query, conn, params=[benefit_category])
        
        if successful.empty:
            conn.close()
            return {
                'status': 'NO_DATA',
                'message': f'No successful projects found for {benefit_category}'
            }
        
        # Get lessons from successful projects
        lesson_query = """
            SELECT 
                lesson_text,
                lesson_category,
                impact_level,
                COUNT(*) as frequency
            FROM project_lessons
            WHERE project_id IN ({})
                AND lesson_type = 'WhatWorked'
            GROUP BY lesson_text, lesson_category, impact_level
            ORDER BY frequency DESC, impact_level ASC
        """.format(','.join(['?'] * len(successful)))
        
        lessons = pd.read_sql_query(lesson_query, conn, params=successful['project_id'].tolist())
        conn.close()
        
        if lessons.empty:
            return {
                'status': 'NO_LESSONS',
                'message': f'No lessons captured for {benefit_category} successes'
            }
        
        # Calculate confidence (frequency / total projects)
        total_projects = len(successful)
        lessons['confidence'] = lessons['frequency'] / total_projects
        
        # Filter by confidence
        high_confidence = lessons[lessons['confidence'] >= min_confidence]
        
        recommendations = []
        for _, lesson in high_confidence.iterrows():
            recommendations.append({
                'practice': lesson['lesson_text'],
                'category': lesson['lesson_category'],
                'impact_level': lesson['impact_level'],
                'confidence': round(lesson['confidence'], 2),
                'evidence_count': int(lesson['frequency']),
                'recommendation': f"Apply this practice (seen in {int(lesson['frequency'])}/{total_projects} successful projects)"
            })
        
        # Also include medium confidence if high confidence list is small
        if len(recommendations) < 3:
            medium_confidence = lessons[(lessons['confidence'] >= 0.4) & (lessons['confidence'] < min_confidence)]
            for _, lesson in medium_confidence.head(3).iterrows():
                recommendations.append({
                    'practice': lesson['lesson_text'],
                    'category': lesson['lesson_category'],
                    'impact_level': lesson['impact_level'],
                    'confidence': round(lesson['confidence'], 2),
                    'evidence_count': int(lesson['frequency']),
                    'recommendation': f"Consider this practice (moderate evidence: {int(lesson['frequency'])}/{total_projects} projects)"
                })
        
        return {
            'status': 'SUCCESS',
            'benefit_category': benefit_category,
            'successful_projects': total_projects,
            'recommendation_count': len(recommendations),
            'recommendations': recommendations
        }
    
    def get_lessons_by_project(self, project_id: str) -> Dict:
        """Get all lessons for a specific project"""
        conn = sqlite3.connect(self.db_path)
        
        query = """
            SELECT *
            FROM project_lessons
            WHERE project_id = ?
            ORDER BY captured_date DESC
        """
        
        lessons = pd.read_sql_query(query, conn, params=[project_id])
        conn.close()
        
        if lessons.empty:
            return {
                'status': 'NO_DATA',
                'message': f'No lessons found for {project_id}'
            }
        
        return {
            'status': 'SUCCESS',
            'project_id': project_id,
            'lesson_count': len(lessons),
            'lessons': lessons.to_dict('records')
        }


# Demo and testing
if __name__ == "__main__":
    print("=" * 80)
    print("Success Factor Library - Demo")
    print("=" * 80)
    
    library = SuccessFactorLibrary(db_path="data/benefit_tracking_demo.db")
    
    print("\n📝 Capturing Lessons Learned")
    lesson1 = library.capture_lesson(
        project_id="PROJ-AI-2024-001",
        lesson_type="WhatWorked",
        lesson_text="Pilot phase with real users validated assumptions before full rollout",
        lesson_category="Planning",
        impact_level="High",
        benefit_impact_pct=15.0,
        captured_by="PM_Team",
        tags=["pilot", "validation", "user_feedback"]
    )
    print(f"   Status: {lesson1['status']}")
    print(f"   Lesson ID: {lesson1.get('lesson_id', 'N/A')}")
    
    lesson2 = library.capture_lesson(
        project_id="PROJ-AI-2024-001",
        lesson_type="WhatWorked",
        lesson_text="Dedicated change management resource improved adoption rate",
        lesson_category="ChangeManagement",
        impact_level="High",
        benefit_impact_pct=20.0,
        captured_by="PM_Team",
        tags=["change_management", "adoption"]
    )
    
    print("\n🔍 Extracting Success Patterns")
    patterns = library.extract_success_patterns(min_success_rate=100.0, min_sample_size=1)
    print(f"   Status: {patterns['status']}")
    if patterns['status'] == 'SUCCESS':
        print(f"   High Performers: {patterns['high_performer_count']}")
        print(f"   Avg Success Rate: {patterns['avg_success_rate']}%")
        print(f"   Lessons Captured: {patterns['lesson_count']}")
        print(f"   Patterns Identified: {patterns['patterns_identified']}")
    elif patterns.get('message'):
        print(f"   Message: {patterns['message']}")
    
    print("\n🎯 Matching Similar Projects")
    new_project = {
        'project_id': 'PROJ-NEW-001',
        'benefit_categories': ['CostSavings', 'Productivity']
    }
    matches = library.match_similar_projects(new_project, top_n=3)
    print(f"   Status: {matches['status']}")
    if matches['status'] == 'SUCCESS':
        print(f"   Similar Projects Found: {matches['similar_projects_found']}")
        for match in matches['matches'][:2]:
            print(f"\n   Project: {match['project_id']}")
            print(f"   Similarity: {match['similarity_score']:.1%}")
            print(f"   Realization Rate: {match['avg_realization_rate']:.1f}%")
            if match['lessons']:
                print(f"   Key Lessons:")
                for lesson in match['lessons'][:2]:
                    print(f"      • {lesson['lesson_text']}")
    
    print("\n💡 Recommending Best Practices")
    recommendations = library.recommend_best_practices(
        benefit_category="CostSavings",
        min_confidence=0.5
    )
    print(f"   Status: {recommendations['status']}")
    if recommendations['status'] == 'SUCCESS':
        print(f"   Category: {recommendations['benefit_category']}")
        print(f"   Evidence Base: {recommendations['successful_projects']} projects")
        print(f"   Recommendations: {recommendations['recommendation_count']}")
        for rec in recommendations['recommendations'][:3]:
            print(f"\n   • {rec['practice']}")
            print(f"     Confidence: {rec['confidence']:.0%} ({rec['evidence_count']} projects)")
            print(f"     {rec['recommendation']}")
    elif recommendations.get('message'):
        print(f"   Message: {recommendations['message']}")
    
    print("\n✅ Demo completed successfully!")
