#!/usr/bin/env python3
"""
Demand Classifier - ML-Based Automatic Idea Categorization

Automatically classifies incoming project ideas/demands into categories based on text descriptions.
Uses TF-IDF + Logistic Regression for multi-class classification.

Categories:
- Digital Transformation
- Cost Reduction
- Market Expansion
- Innovation
- Compliance
- Infrastructure

Author: Portfolio ML
Version: 1.0.0
"""

import re
from typing import Dict, List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import numpy as np


class DemandClassifier:
    """
    ML-based classifier for automatic project demand categorization
    
    Uses TF-IDF features and Logistic Regression to classify ideas
    based on text descriptions into project categories, sub-types,
    and complexity levels.
    """
    
    def __init__(self):
        """Initialize the demand classifier with trained models"""
        self.categories = [
            'Digital Transformation',
            'Cost Reduction',
            'Market Expansion',
            'Innovation',
            'Compliance',
            'Infrastructure'
        ]
        
        self.sub_types = {
            'Digital Transformation': ['AI/ML', 'Process Automation', 'Cloud Migration', 'Data Analytics', 'Customer Experience'],
            'Cost Reduction': ['Process Optimization', 'Outsourcing', 'Consolidation', 'Energy Efficiency', 'Waste Reduction'],
            'Market Expansion': ['New Geography', 'New Product Line', 'New Customer Segment', 'Channel Expansion', 'Partnership'],
            'Innovation': ['R&D', 'Product Development', 'Service Innovation', 'Business Model Innovation', 'Technology Innovation'],
            'Compliance': ['Regulatory', 'Security', 'Privacy', 'Audit', 'Risk Management'],
            'Infrastructure': ['Hardware Upgrade', 'Network', 'Facilities', 'Software Upgrade', 'Maintenance']
        }
        
        # Initialize TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=200,
            ngram_range=(1, 2),
            stop_words='english',
            lowercase=True
        )
        
        # Initialize classifier
        self.classifier = LogisticRegression(
            max_iter=1000,
            multi_class='multinomial',
            random_state=42
        )
        
        # Train on synthetic training data
        self._train_model()
    
    def _train_model(self):
        """Train the classifier on synthetic training examples"""
        # Training data: (description, category, sub_type, complexity)
        training_data = [
            # Digital Transformation
            ("implement AI chatbot for customer support automated responses machine learning", "Digital Transformation", "AI/ML", "Medium"),
            ("deploy machine learning model for predictive maintenance using sensors data analytics", "Digital Transformation", "AI/ML", "High"),
            ("automate invoice processing using RPA robotic process automation reduce manual work", "Digital Transformation", "Process Automation", "Medium"),
            ("migrate legacy applications to cloud AWS Azure infrastructure modernization", "Digital Transformation", "Cloud Migration", "High"),
            ("build customer data platform CDP analytics reporting dashboard visualization", "Digital Transformation", "Data Analytics", "High"),
            ("redesign mobile app user interface improve customer experience UX design", "Digital Transformation", "Customer Experience", "Medium"),
            ("implement automated workflow approval system digital forms paperless", "Digital Transformation", "Process Automation", "Low"),
            ("develop AI-powered recommendation engine personalization e-commerce", "Digital Transformation", "AI/ML", "High"),
            
            # Cost Reduction
            ("optimize supply chain logistics reduce transportation costs efficiency", "Cost Reduction", "Process Optimization", "Medium"),
            ("consolidate data centers reduce operational expenses infrastructure savings", "Cost Reduction", "Consolidation", "High"),
            ("outsource IT help desk support reduce headcount costs service provider", "Cost Reduction", "Outsourcing", "Medium"),
            ("implement energy efficient lighting HVAC reduce utility bills sustainability", "Cost Reduction", "Energy Efficiency", "Low"),
            ("reduce waste in manufacturing lean six sigma process improvement", "Cost Reduction", "Waste Reduction", "Medium"),
            ("negotiate better vendor contracts procurement savings bulk purchasing", "Cost Reduction", "Process Optimization", "Low"),
            ("automate manual data entry reduce labor costs efficiency improvement", "Cost Reduction", "Process Optimization", "Medium"),
            
            # Market Expansion
            ("expand into Asian markets new geography international sales growth", "Market Expansion", "New Geography", "High"),
            ("launch new product line targeting millennial consumers market research", "Market Expansion", "New Product Line", "High"),
            ("target enterprise customers B2B expansion sales strategy upmarket", "Market Expansion", "New Customer Segment", "Medium"),
            ("establish online sales channel e-commerce digital storefront", "Market Expansion", "Channel Expansion", "Medium"),
            ("form strategic partnership with industry leader joint venture collaboration", "Market Expansion", "Partnership", "Medium"),
            ("open retail stores in major cities physical presence brick-and-mortar", "Market Expansion", "New Geography", "High"),
            
            # Innovation
            ("research and development new battery technology R&D lab prototype", "Innovation", "R&D", "High"),
            ("develop next generation product features innovation roadmap competitive advantage", "Innovation", "Product Development", "High"),
            ("create subscription service model recurring revenue business transformation", "Innovation", "Business Model Innovation", "Medium"),
            ("implement blockchain for supply chain traceability distributed ledger", "Innovation", "Technology Innovation", "High"),
            ("design innovative customer loyalty program gamification rewards", "Innovation", "Service Innovation", "Medium"),
            ("build innovation lab for rapid prototyping agile development MVPs", "Innovation", "R&D", "Medium"),
            
            # Compliance
            ("achieve GDPR compliance data privacy regulation European Union requirements", "Compliance", "Privacy", "High"),
            ("implement SOC2 security controls audit certification trust report", "Compliance", "Security", "High"),
            ("update policies for new financial regulations banking compliance regulatory", "Compliance", "Regulatory", "Medium"),
            ("enhance cybersecurity posture penetration testing vulnerability assessment", "Compliance", "Security", "Medium"),
            ("establish enterprise risk management framework governance controls", "Compliance", "Risk Management", "Medium"),
            ("prepare for ISO certification quality management system audit", "Compliance", "Audit", "Medium"),
            
            # Infrastructure
            ("upgrade network infrastructure fiber optic high-speed connectivity", "Infrastructure", "Network", "High"),
            ("replace aging servers hardware refresh data center equipment", "Infrastructure", "Hardware Upgrade", "High"),
            ("renovate office facilities HVAC electrical plumbing maintenance", "Infrastructure", "Facilities", "Medium"),
            ("upgrade ERP system SAP Oracle software modernization database", "Infrastructure", "Software Upgrade", "High"),
            ("preventive maintenance program equipment reliability asset management", "Infrastructure", "Maintenance", "Low"),
            ("install backup power generators UPS disaster recovery redundancy", "Infrastructure", "Hardware Upgrade", "Medium"),
        ]
        
        # Extract features and labels
        descriptions = [item[0] for item in training_data]
        categories = [item[1] for item in training_data]
        
        # Train TF-IDF vectorizer
        X_train = self.vectorizer.fit_transform(descriptions)
        
        # Train classifier
        self.classifier.fit(X_train, categories)
    
    def classify_idea(self, description: str, title: str = "") -> Dict:
        """
        Classify an idea based on its description
        
        Args:
            description: Text description of the idea/demand
            title: Optional title of the idea
            
        Returns:
            Dictionary with classification results:
            - category: Main project category
            - sub_type: Specific sub-category
            - complexity: Low/Medium/High
            - confidence: Classification confidence (0-1)
            - keywords: Key terms identified
        """
        # Combine title and description
        full_text = f"{title} {description}".strip()
        
        if not full_text:
            return {
                'category': 'Unknown',
                'sub_type': 'Unknown',
                'complexity': 'Medium',
                'confidence': 0.0,
                'keywords': [],
                'error': 'No text provided'
            }
        
        # Preprocess text
        clean_text = self._preprocess_text(full_text)
        
        # Extract features
        X = self.vectorizer.transform([clean_text])
        
        # Predict category
        category = self.classifier.predict(X)[0]
        
        # Get confidence (probability of predicted class)
        probabilities = self.classifier.predict_proba(X)[0]
        predicted_idx = self.categories.index(category)
        confidence = probabilities[predicted_idx]
        
        # Determine sub-type based on keywords
        sub_type = self._determine_sub_type(clean_text, category)
        
        # Estimate complexity
        complexity = self._estimate_complexity(clean_text)
        
        # Extract keywords
        keywords = self._extract_keywords(clean_text)
        
        return {
            'category': category,
            'sub_type': sub_type,
            'complexity': complexity,
            'confidence': float(confidence),
            'keywords': keywords[:5]  # Top 5 keywords
        }
    
    def _preprocess_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def _determine_sub_type(self, text: str, category: str) -> str:
        """Determine sub-type based on keyword matching"""
        # Keywords for each sub-type
        sub_type_keywords = {
            'Digital Transformation': {
                'AI/ML': ['ai', 'machine learning', 'ml', 'artificial intelligence', 'deep learning', 'neural', 'chatbot', 'prediction', 'predictive'],
                'Process Automation': ['automate', 'automation', 'rpa', 'robotic', 'workflow', 'automated', 'bot'],
                'Cloud Migration': ['cloud', 'aws', 'azure', 'gcp', 'migration', 'migrate', 'saas', 'infrastructure'],
                'Data Analytics': ['analytics', 'data', 'dashboard', 'reporting', 'bi', 'business intelligence', 'visualization', 'insights'],
                'Customer Experience': ['customer', 'cx', 'ux', 'user experience', 'mobile app', 'website', 'interface', 'design']
            },
            'Cost Reduction': {
                'Process Optimization': ['optimize', 'optimization', 'efficiency', 'streamline', 'lean', 'process', 'improve'],
                'Outsourcing': ['outsource', 'outsourcing', 'offshore', 'vendor', 'third party', 'service provider'],
                'Consolidation': ['consolidate', 'consolidation', 'merge', 'centralize', 'data center'],
                'Energy Efficiency': ['energy', 'utility', 'efficient', 'hvac', 'lighting', 'sustainability', 'green'],
                'Waste Reduction': ['waste', 'reduction', 'six sigma', 'manufacturing', 'scrap', 'defect']
            },
            'Market Expansion': {
                'New Geography': ['geography', 'international', 'global', 'market', 'region', 'country', 'asia', 'europe', 'expand'],
                'New Product Line': ['product line', 'new product', 'launch', 'offering', 'portfolio'],
                'New Customer Segment': ['customer segment', 'b2b', 'b2c', 'enterprise', 'consumer', 'target', 'demographic'],
                'Channel Expansion': ['channel', 'e commerce', 'online', 'digital', 'retail', 'distribution', 'sales channel'],
                'Partnership': ['partnership', 'partner', 'alliance', 'collaboration', 'joint venture', 'strategic']
            },
            'Innovation': {
                'R&D': ['r d', 'research', 'development', 'lab', 'laboratory', 'prototype', 'experiment'],
                'Product Development': ['product development', 'new features', 'roadmap', 'innovation', 'next generation'],
                'Service Innovation': ['service', 'customer service', 'loyalty', 'program', 'subscription', 'membership'],
                'Business Model Innovation': ['business model', 'revenue model', 'subscription', 'recurring', 'transformation'],
                'Technology Innovation': ['blockchain', 'iot', 'quantum', 'emerging technology', 'cutting edge', 'innovative tech']
            },
            'Compliance': {
                'Regulatory': ['regulatory', 'regulation', 'financial', 'banking', 'sox', 'compliance requirement'],
                'Security': ['security', 'cybersecurity', 'soc2', 'iso 27001', 'penetration', 'vulnerability'],
                'Privacy': ['privacy', 'gdpr', 'ccpa', 'data protection', 'personal data', 'pii'],
                'Audit': ['audit', 'certification', 'iso', 'quality', 'assessment', 'compliance audit'],
                'Risk Management': ['risk', 'risk management', 'governance', 'erm', 'enterprise risk', 'controls']
            },
            'Infrastructure': {
                'Hardware Upgrade': ['hardware', 'server', 'equipment', 'upgrade', 'replace', 'refresh'],
                'Network': ['network', 'networking', 'fiber', 'connectivity', 'bandwidth', 'router', 'switch'],
                'Facilities': ['facilities', 'facility', 'office', 'building', 'renovation', 'hvac', 'maintenance'],
                'Software Upgrade': ['software', 'erp', 'crm', 'sap', 'oracle', 'application', 'system upgrade'],
                'Maintenance': ['maintenance', 'preventive', 'repair', 'upkeep', 'asset management', 'reliability']
            }
        }
        
        if category not in sub_type_keywords:
            return 'General'
        
        # Score each sub-type based on keyword matches
        sub_type_scores = {}
        for sub_type, keywords in sub_type_keywords[category].items():
            score = sum(1 for keyword in keywords if keyword in text)
            sub_type_scores[sub_type] = score
        
        # Return sub-type with highest score
        if max(sub_type_scores.values()) > 0:
            return max(sub_type_scores, key=sub_type_scores.get)
        
        return 'General'
    
    def _estimate_complexity(self, text: str) -> str:
        """Estimate project complexity based on text indicators"""
        complexity_indicators = {
            'Low': ['simple', 'basic', 'minor', 'small', 'quick', 'straightforward', 'maintenance'],
            'Medium': ['moderate', 'standard', 'typical', 'normal', 'medium', 'regular'],
            'High': ['complex', 'large', 'major', 'enterprise', 'strategic', 'transformation', 
                    'migration', 'implementation', 'integration', 'multi', 'cross functional']
        }
        
        # Count indicators for each complexity level
        scores = {}
        for level, keywords in complexity_indicators.items():
            scores[level] = sum(1 for keyword in keywords if keyword in text)
        
        # Default to Medium if no clear indicators
        if max(scores.values()) == 0:
            return 'Medium'
        
        return max(scores, key=scores.get)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text"""
        # Get feature names and their importance
        feature_names = self.vectorizer.get_feature_names_out()
        
        # Transform text and get feature scores
        X = self.vectorizer.transform([text])
        
        # Get non-zero features and their scores
        feature_indices = X.nonzero()[1]
        feature_scores = [(feature_names[i], X[0, i]) for i in feature_indices]
        
        # Sort by score
        feature_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Return top keywords
        return [keyword for keyword, score in feature_scores[:10]]
    
    def classify_batch(self, ideas: List[Dict]) -> List[Dict]:
        """
        Classify multiple ideas in batch
        
        Args:
            ideas: List of dictionaries with 'description' and optional 'title'
            
        Returns:
            List of classification results
        """
        results = []
        for idea in ideas:
            description = idea.get('description', '')
            title = idea.get('title', '')
            classification = self.classify_idea(description, title)
            classification['original_idea'] = idea
            results.append(classification)
        
        return results


def main():
    """Demo: Classify sample ideas"""
    print("=" * 80)
    print("DEMAND CLASSIFIER - ML-BASED IDEA CATEGORIZATION")
    print("=" * 80)
    
    classifier = DemandClassifier()
    
    # Test cases
    test_ideas = [
        {
            'title': 'AI Customer Support Chatbot',
            'description': 'Implement AI-powered chatbot for customer service. Expected to reduce support costs by 40% and improve response time. Requires integration with existing CRM and 6-month implementation.'
        },
        {
            'title': 'Supply Chain Optimization',
            'description': 'Optimize logistics and supply chain operations to reduce transportation costs. Implement route optimization software and consolidate warehouses.'
        },
        {
            'title': 'European Market Entry',
            'description': 'Expand business into European markets with focus on Germany and France. Establish local partnerships and distribution channels.'
        },
        {
            'title': 'GDPR Compliance',
            'description': 'Ensure full compliance with GDPR data privacy regulations. Update data handling processes, implement consent management, and conduct privacy impact assessments.'
        },
        {
            'title': 'Data Center Upgrade',
            'description': 'Replace aging server infrastructure and upgrade network equipment. Improve reliability and performance of IT systems.'
        }
    ]
    
    for i, idea in enumerate(test_ideas, 1):
        print(f"\n{'─' * 80}")
        print(f"Idea {i}: {idea['title']}")
        print(f"{'─' * 80}")
        print(f"Description: {idea['description'][:100]}...")
        
        result = classifier.classify_idea(idea['description'], idea['title'])
        
        print(f"\n✅ Classification Results:")
        print(f"   Category: {result['category']}")
        print(f"   Sub-type: {result['sub_type']}")
        print(f"   Complexity: {result['complexity']}")
        print(f"   Confidence: {result['confidence']:.1%}")
        print(f"   Keywords: {', '.join(result['keywords'][:5])}")
    
    print(f"\n{'=' * 80}")
    print("Classification complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
