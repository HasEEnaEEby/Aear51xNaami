"""
Questionnaire Processor for Security Compliance Advisor
This module processes vendor security questionnaires and maps them to compliance frameworks.
"""

import os
import json
import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from pathlib import Path
import re

# Configure logging
logger = logging.getLogger(__name__)

class QuestionnaireProcessor:
    """Processes vendor security questionnaires for risk assessment"""
    
    def __init__(self, field_mappings_path: str = None):
        """
        Initialize the questionnaire processor
        
        Args:
            field_mappings_path: Path to field mappings file (optional)
        """
        self.field_mappings = {}
        
        # Default field mappings
        self.default_mappings = {
            "access_control": ["access", "authentication", "authorization", "privilege", "credential", "mfa", "2fa"],
            "data_protection": ["encryption", "data security", "confidential", "protect", "sensitive data", "data loss"],
            "vulnerability_management": ["vulnerability", "patch", "update", "scan", "remediate"],
            "incident_response": ["incident", "breach", "response", "event"],
            "network_security": ["network", "firewall", "traffic", "monitoring", "segmentation"],
            "physical_security": ["physical", "facility", "data center", "building", "access card"],
            "risk_management": ["risk", "assessment", "analysis", "threat", "impact"],
            "compliance": ["compliance", "regulation", "regulatory", "framework", "standard"],
            "third_party": ["vendor", "supplier", "third party", "third-party", "provider"],
            "security_policies": ["policy", "procedure", "standard", "guideline", "documentation"],
            "security_awareness": ["training", "awareness", "education", "phishing"],
            "asset_management": ["asset", "inventory", "classification", "ownership"],
            "bcdr": ["business continuity", "disaster recovery", "backup", "restore", "resilience"],
            "change_management": ["change", "configuration", "management", "deployment"],
            "cloud_security": ["cloud", "saas", "paas", "iaas", "aws", "azure", "gcp"]
        }
        
        # Load custom field mappings if provided
        if field_mappings_path and os.path.exists(field_mappings_path):
            try:
                with open(field_mappings_path, 'r', encoding='utf-8') as f:
                    custom_mappings = json.load(f)
                
                # Update default mappings with custom ones
                if isinstance(custom_mappings, dict):
                    self.field_mappings = {**self.default_mappings, **custom_mappings}
                    logger.info(f"Loaded custom field mappings from {field_mappings_path}")
            except Exception as e:
                logger.error(f"Error loading field mappings from {field_mappings_path}: {str(e)}")
                self.field_mappings = self.default_mappings
        else:
            self.field_mappings = self.default_mappings
    
    def process_questionnaire(self, questionnaire_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a questionnaire for risk analysis
        
        Args:
            questionnaire_data: Dictionary with questionnaire data
            
        Returns:
            Processed data with risk factors and compliance mappings
        """
        # Get the questions
        questions = questionnaire_data.get('questions', [])
        
        if not questions:
            logger.warning("No questions found in questionnaire data")
            return {
                'status': 'error',
                'message': 'No questions found in questionnaire data',
                'data': questionnaire_data
            }
        
        # Categorize questions by security domain
        categorized_questions = self._categorize_questions(questions)
        
        # Analyze responses
        response_analysis = self._analyze_responses(categorized_questions)
        
        # Calculate compliance scores for major frameworks
        compliance_scores = self._calculate_framework_compliance(categorized_questions)
        
        # Identify security gaps
        security_gaps = self._identify_security_gaps(categorized_questions, response_analysis)
        
        # Create processed data structure
        processed_data = {
            'status': 'success',
            'source_data': questionnaire_data,
            'categorized_questions': categorized_questions,
            'response_analysis': response_analysis,
            'framework_compliance': compliance_scores,
            'security_gaps': security_gaps,
            'metadata': {
                'num_questions': len(questions),
                'num_categorized': sum(len(qs) for qs in categorized_questions.values()),
                'num_negative_responses': response_analysis.get('negative_count', 0)
            }
        }
        
        return processed_data
    
    def _categorize_questions(self, questions: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Categorize questions by security domain
        
        Args:
            questions: List of question dictionaries
            
        Returns:
            Dictionary mapping security domains to lists of questions
        """
        categorized = {domain: [] for domain in self.field_mappings.keys()}
        categorized['uncategorized'] = []  # For questions that don't match any category
        
        for question in questions:
            # Get the question text
            question_text = question.get('question', '')
            
            if not question_text:
                # Try alternative fields that might contain the question
                for field in ['requirement', 'control', 'subcategory']:
                    if field in question and question[field]:
                        question_text = question[field]
                        break
            
            if not question_text:
                # If still no question text, use any available text field
                for key, value in question.items():
                    if isinstance(value, str) and len(value) > 10:
                        question_text = value
                        break
            
            # Skip if no usable text found
            if not question_text:
                continue
            
            # Convert question text to lowercase for matching
            question_text_lower = question_text.lower()
            
            # Match question to domains
            matched_domains = []
            
            for domain, keywords in self.field_mappings.items():
                for keyword in keywords:
                    if keyword.lower() in question_text_lower:
                        matched_domains.append((domain, len(keyword)))  # Track keyword length for better matching
            
            if matched_domains:
                # Sort by keyword length (longer keywords are more specific)
                matched_domains.sort(key=lambda x: x[1], reverse=True)
                primary_domain = matched_domains[0][0]
                categorized[primary_domain].append(question)
            else:
                categorized['uncategorized'].append(question)
                
                # Try to use category from the question if available
                if 'category' in question and question['category']:
                    category_text = question['category'].lower()
                    
                    for domain in self.field_mappings.keys():
                        # Convert domain name to readable format for comparison
                        domain_text = domain.replace('_', ' ')
                        
                        if domain_text in category_text or any(kw.lower() in category_text for kw in self.field_mappings[domain]):
                            # Move from uncategorized to this domain
                            categorized['uncategorized'].remove(question)
                            categorized[domain].append(question)
                            break
        
        return categorized
    
    def _analyze_responses(self, categorized_questions: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Analyze responses to identify risk areas
        
        Args:
            categorized_questions: Dictionary mapping domains to questions
            
        Returns:
            Analysis of responses by domain
        """
        response_analysis = {
            'total_count': 0,
            'positive_count': 0,
            'negative_count': 0,
            'na_count': 0,
            'domains': {}
        }
        
        for domain, questions in categorized_questions.items():
            domain_analysis = {
                'total': len(questions),
                'positive': 0,
                'negative': 0,
                'na': 0,
                'score': 0.0,
                'risk_level': 'Unknown'
            }
            
            for question in questions:
                answer = self._normalize_answer(question.get('answer', ''))
                
                if answer == 'positive':
                    domain_analysis['positive'] += 1
                elif answer == 'negative':
                    domain_analysis['negative'] += 1
                else:  # na or unknown
                    domain_analysis['na'] += 1
            
            # Update total counts
            response_analysis['total_count'] += domain_analysis['total']
            response_analysis['positive_count'] += domain_analysis['positive']
            response_analysis['negative_count'] += domain_analysis['negative']
            response_analysis['na_count'] += domain_analysis['na']
            
            # Calculate domain score (higher is better)
            denominator = domain_analysis['total'] - domain_analysis['na']
            if denominator > 0:
                domain_analysis['score'] = (domain_analysis['positive'] / denominator) * 100
            
            # Determine risk level
            if domain_analysis['score'] >= 80:
                domain_analysis['risk_level'] = 'Low'
            elif domain_analysis['score'] >= 60:
                domain_analysis['risk_level'] = 'Medium'
            elif domain_analysis['score'] > 0:
                domain_analysis['risk_level'] = 'High'
            
            response_analysis['domains'][domain] = domain_analysis
        
        # Calculate overall score
        denominator = response_analysis['total_count'] - response_analysis['na_count']
        if denominator > 0:
            response_analysis['overall_score'] = (response_analysis['positive_count'] / denominator) * 100
        else:
            response_analysis['overall_score'] = 0
            
        # Determine overall risk level
        if response_analysis['overall_score'] >= 80:
            response_analysis['overall_risk_level'] = 'Low'
        elif response_analysis['overall_score'] >= 60:
            response_analysis['overall_risk_level'] = 'Medium'
        else:
            response_analysis['overall_risk_level'] = 'High'
        
        return response_analysis
    
    def _normalize_answer(self, answer: Any) -> str:
        """
        Normalize answer to positive, negative, or na
        
        Args:
            answer: Answer value from questionnaire
            
        Returns:
            Normalized answer category
        """
        if not answer:
            return 'na'
        
        # Convert to string
        if not isinstance(answer, str):
            answer = str(answer)
        
        # Convert to lowercase
        answer_lower = answer.lower().strip()
        
        # Positive answers
        positive_indicators = [
            'yes', 'y', 'true', 't', 'implemented', 'complete', 'compliant', 
            'satisfied', 'in place', 'done', '1', 'comply', 'complies'
        ]
        
        # Negative answers
        negative_indicators = [
            'no', 'n', 'false', 'f', 'not implemented', 'incomplete', 'non-compliant',
            'not satisfied', 'not in place', 'todo', '0', 'does not comply', 'planned'
        ]
        
        # NA answers
        na_indicators = [
            'na', 'n/a', 'not applicable', 'n.a.', 'not relevant', 'not answered'
        ]
        
        # Check for exact match
        if answer_lower in positive_indicators:
            return 'positive'
        elif answer_lower in negative_indicators:
            return 'negative'
        elif answer_lower in na_indicators:
            return 'na'
        
        # Check for partial match
        for indicator in positive_indicators:
            if indicator in answer_lower:
                return 'positive'
                
        for indicator in negative_indicators:
            if indicator in answer_lower:
                return 'negative'
                
        for indicator in na_indicators:
            if indicator in answer_lower:
                return 'na'
        
        # Default to na for unknown answers
        return 'na'
    
    def _calculate_framework_compliance(self, categorized_questions: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Dict[str, Any]]:
        """
        Calculate compliance scores for major frameworks
        
        Args:
            categorized_questions: Dictionary mapping domains to questions
            
        Returns:
            Dictionary mapping framework IDs to compliance scores
        """
        # Define framework domain weighting
        framework_weights = {
            'nist_csf': {
                'access_control': 0.15,
                'data_protection': 0.15,
                'vulnerability_management': 0.15,
                'incident_response': 0.10,
                'network_security': 0.10,
                'physical_security': 0.05,
                'risk_management': 0.10,
                'security_policies': 0.05,
                'security_awareness': 0.05,
                'asset_management': 0.05,
                'bcdr': 0.05
            },
            'iso27001': {
                'access_control': 0.15,
                'data_protection': 0.10,
                'vulnerability_management': 0.10,
                'incident_response': 0.10,
                'network_security': 0.10,
                'physical_security': 0.05,
                'risk_management': 0.10,
                'security_policies': 0.10,
                'security_awareness': 0.05,
                'asset_management': 0.05,
                'bcdr': 0.05,
                'change_management': 0.05
            },
            'hipaa': {
                'access_control': 0.20,
                'data_protection': 0.20,
                'vulnerability_management': 0.10,
                'incident_response': 0.15,
                'network_security': 0.10,
                'physical_security': 0.10,
                'risk_management': 0.05,
                'security_policies': 0.05,
                'bcdr': 0.05
            },
            'pci_dss': {
                'access_control': 0.20,
                'data_protection': 0.20,
                'vulnerability_management': 0.15,
                'network_security': 0.15,
                'security_awareness': 0.10,
                'security_policies': 0.10,
                'change_management': 0.10
            },
            'gdpr': {
                'data_protection': 0.30,
                'access_control': 0.15,
                'incident_response': 0.15,
                'security_policies': 0.10,
                'third_party': 0.10,
                'risk_management': 0.10,
                'compliance': 0.10
            }
        }
        
        # Calculate compliance scores
        framework_compliance = {}
        
        for framework_id, domain_weights in framework_weights.items():
            # Initialize framework data
            framework_compliance[framework_id] = {
                'compliance_score': 0.0,
                'gap_areas': [],
                'domain_scores': {}
            }
            
            weighted_score = 0.0
            total_weight = 0.0
            
            for domain, weight in domain_weights.items():
                # Skip if domain not in categorized questions
                if domain not in categorized_questions:
                    continue
                
                questions = categorized_questions[domain]
                
                # Skip if no questions in this domain
                if not questions:
                    continue
            
                domain_score = 0.0
                positive_count = 0
                total_count = 0
                
                for question in questions:
                    answer = self._normalize_answer(question.get('answer', ''))
                    
                    if answer != 'na':
                        total_count += 1
                        
                        if answer == 'positive':
                            positive_count += 1
                
                # Calculate domain score
                if total_count > 0:
                    domain_score = (positive_count / total_count) * 100
                
                # Add to weighted score
                weighted_score += domain_score * weight
                total_weight += weight
                
                # Store domain score
                framework_compliance[framework_id]['domain_scores'][domain] = domain_score
                
                # Check for gap areas
                if domain_score < 60:
                    framework_compliance[framework_id]['gap_areas'].append({
                        'category': domain,
                        'score': domain_score,
                        'question_count': total_count
                    })
            
            # Calculate final compliance score
            if total_weight > 0:
                framework_compliance[framework_id]['compliance_score'] = weighted_score / total_weight
            
            # Sort gap areas by score (lowest first)
            framework_compliance[framework_id]['gap_areas'].sort(key=lambda x: x['score'])
        
        return framework_compliance
    
    def _identify_security_gaps(self, categorized_questions: Dict[str, List[Dict[str, Any]]], response_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Identify security gaps based on questionnaire responses
        
        Args:
            categorized_questions: Dictionary mapping domains to questions
            response_analysis: Analysis of responses by domain
            
        Returns:
            List of identified security gaps
        """
        security_gaps = []
        
        # Check for domains with high risk levels
        domain_analyses = response_analysis.get('domains', {})
        
        for domain, analysis in domain_analyses.items():
            # Skip uncategorized questions
            if domain == 'uncategorized':
                continue
                
            risk_level = analysis.get('risk_level')
            
            if risk_level in ['High', 'Medium']:
                # Find specific negative responses in this domain
                domain_questions = categorized_questions.get(domain, [])
                negative_responses = []
                
                for question in domain_questions:
                    answer = self._normalize_answer(question.get('answer', ''))
                    
                    if answer == 'negative':
                        negative_responses.append({
                            'question': question.get('question', ''),
                            'category': domain
                        })
                
                # Add gap if negative responses found
                if negative_responses:
                    security_gaps.append({
                        'category': domain,
                        'risk_level': risk_level,
                        'score': analysis.get('score', 0),
                        'negative_responses': negative_responses
                    })
        
        # Sort gaps by risk level and score
        security_gaps.sort(key=lambda x: (0 if x['risk_level'] == 'High' else 1, x['score']))
        
        return security_gaps