"""
Enhanced Risk Scoring Model for Security Compliance Advisor
This module provides advanced risk scoring with explainable results and recommendations.
"""

import numpy as np
import pandas as pd
from datetime import datetime
import json
import os
from pathlib import Path
import logging
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class RiskScoringModel:
    """
    Advanced risk scoring model that processes questionnaire data and provides
    explainable risk assessments, compliance mappings, and prioritized recommendations.
    """
    
    # Risk weights by category
    RISK_CATEGORY_WEIGHTS = {
        "Data Protection": 0.20,
        "Access Control": 0.18,
        "Vulnerability Management": 0.15,
        "Network Security": 0.12,
        "Authentication": 0.10,
        "Encryption": 0.10,
        "Incident Response": 0.08,
        "Business Continuity": 0.07
    }
    
    # Framework priority weights - which frameworks matter most
    FRAMEWORK_WEIGHTS = {
        "iso27001": 0.20,
        "nist_csf": 0.18,
        "pci_dss": 0.15,
        "gdpr": 0.15,
        "hipaa": 0.12,
        "ccpa": 0.08,
        "cis": 0.07,
        "hitrust": 0.05
    }
    
    # Risk impact levels
    RISK_IMPACT_LEVELS = {
        "Critical": 1.0,
        "High": 0.8,
        "Medium": 0.5,
        "Low": 0.2,
        "Negligible": 0.1
    }
    
    def __init__(self, policy_dir: str = None):
        """
        Initialize the risk scoring model
        
        Args:
            policy_dir: Directory containing policy JSON files
        """
        self.policy_dir = policy_dir or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                                    "data", "policies")
        self.policies = {}
        self.control_mappings = {}
        self.load_policies()
        self.load_control_mappings()
    
    def load_policies(self):
        """Load policy files from the policies directory"""
        try:
            # Try to load the combined file first
            all_policies_path = os.path.join(self.policy_dir, "all_policies_with_embeddings.json")
            if os.path.exists(all_policies_path):
                with open(all_policies_path, 'r') as f:
                    self.policies = json.load(f)
                logger.info(f"Loaded {len(self.policies)} policies from combined file")
                return
                
            # If combined file doesn't exist, load individual framework files
            separate_dir = os.path.join(self.policy_dir, "Seperate policies json")
            if os.path.exists(separate_dir):
                for filename in os.listdir(separate_dir):
                    if filename.endswith(".json"):
                        framework = filename.split(".")[0].lower()
                        with open(os.path.join(separate_dir, filename), 'r') as f:
                            framework_policies = json.load(f)
                            self.policies[framework] = framework_policies
                logger.info(f"Loaded policies for {len(self.policies)} frameworks from separate files")
            
        except Exception as e:
            logger.error(f"Error loading policy files: {str(e)}")
            self.policies = {}
    
    def load_control_mappings(self):
        """Load control mappings between different frameworks"""
        try:
            mappings_dir = os.path.join(os.path.dirname(self.policy_dir), "mappings")
            if os.path.exists(mappings_dir):
                for filename in os.listdir(mappings_dir):
                    if filename.endswith(".json") and "mapping" in filename.lower():
                        with open(os.path.join(mappings_dir, filename), 'r') as f:
                            mapping_data = json.load(f)
                            # Extract the frameworks from the filename
                            frameworks = filename.replace("_mapping.json", "").split("_to_")
                            if len(frameworks) == 2:
                                source, target = frameworks
                                self.control_mappings[(source, target)] = mapping_data
                logger.info(f"Loaded {len(self.control_mappings)} control mappings")
        except Exception as e:
            logger.error(f"Error loading control mappings: {str(e)}")
            self.control_mappings = {}
    
    def categorize_question(self, question: Dict[str, Any]) -> str:
        """
        Categorize a question into one of the risk categories
        
        Args:
            question: Dictionary containing question data
            
        Returns:
            Category name as string
        """
        # Extract keywords from the question text
        question_text = question.get('question', '').lower()
        
        # Simple keyword-based categorization
        categories = {
            "Data Protection": ["data", "protection", "privacy", "gdpr", "personal", "information", "dpa", "pii", "confidential"],
            "Access Control": ["access", "permission", "privilege", "authorization", "rbac", "role-based", "least privilege"],
            "Vulnerability Management": ["vulnerability", "patch", "update", "scan", "assessment", "penetration test", "pentest"],
            "Network Security": ["network", "firewall", "intrusion", "ids", "ips", "segmentation", "dmz", "perimeter"],
            "Authentication": ["authentication", "password", "mfa", "multi-factor", "identity", "login", "credential"],
            "Encryption": ["encrypt", "cryptograph", "cipher", "key management", "tls", "ssl", "https"],
            "Incident Response": ["incident", "response", "breach", "alert", "detect", "siem", "security event"],
            "Business Continuity": ["continuity", "disaster", "recovery", "backup", "bcp", "drp", "resilience"]
        }
        
        # Check if the question explicitly specifies a category
        if 'category' in question:
            category = question['category'].lower()
            for cat_name, keywords in categories.items():
                if any(kw.lower() in category for kw in keywords):
                    return cat_name
        
        # Otherwise, check the question text
        matched_categories = []
        for cat_name, keywords in categories.items():
            for keyword in keywords:
                if keyword.lower() in question_text:
                    matched_categories.append((cat_name, keywords.index(keyword)))
        
        if matched_categories:
            # Sort by the keyword index (to prioritize more important keywords)
            matched_categories.sort(key=lambda x: x[1])
            return matched_categories[0][0]
        
        # Default to "Other" if no matches
        return "Other"
    
    def calculate_question_score(self, question: Dict[str, Any]) -> Tuple[float, str, str]:
        """
        Calculate a risk score for a single question
        
        Args:
            question: Dictionary containing question data
            
        Returns:
            Tuple of (score, explanation, finding_level)
        """
        answer = question.get('answer', '').lower()
        question_text = question.get('question', '')
        
        # Default to medium risk if no answer
        if not answer:
            return 0.5, "No answer provided", "Medium"
        
        # Analyze positive and negative indicators in the answer
        positive_indicators = ["yes", "implemented", "complete", "compliant", "secured", "encrypted", "monitored", "regularly", "always"]
        negative_indicators = ["no", "not implemented", "partial", "in progress", "planned", "sometimes", "never", "none", "n/a"]
        
        # Count positive and negative indicators
        positive_count = sum(1 for ind in positive_indicators if ind in answer)
        negative_count = sum(1 for ind in negative_indicators if ind in answer)
        
        explanation = ""
        
        # Check for special cases like "yes but" or "no but"
        if "yes" in answer and any(qualifier in answer for qualifier in ["but", "however", "although", "partially"]):
            score = 0.7
            explanation = "Partial implementation indicated"
            finding_level = "Medium"
        elif "no" in answer and any(qualifier in answer for qualifier in ["but", "however", "although", "planned"]):
            score = 0.3
            explanation = "Implementation planned but not complete"
            finding_level = "High"
        # Calculate score based on indicators
        elif positive_count > negative_count:
            score = 0.8 + (min(positive_count, 3) * 0.05)  # Max bonus of 0.15
            explanation = "Positive implementation evidence found"
            finding_level = "Low"
        elif negative_count > positive_count:
            score = 0.4 - (min(negative_count, 4) * 0.1)  # Max penalty of 0.4
            explanation = "Significant control gaps identified"
            finding_level = "High"
        else:
            # Neutral or unclear response
            score = 0.5
            explanation = "Ambiguous or unclear implementation status"
            finding_level = "Medium"
        
        # Determine if the question is security-critical
        critical_keywords = ["encryption", "authentication", "access control", "privileged", "administrator", 
                           "sensitive data", "personal data", "backup", "patch", "vulnerability", "firewall"]
        
        is_critical = any(keyword in question_text.lower() for keyword in critical_keywords)
        
        # Apply criticality adjustment
        if is_critical and score < 0.7:
            penalty = 0.1 if score > 0.3 else 0.05
            score -= penalty
            explanation += " (Critical security control)"
            if finding_level != "Critical":
                finding_level = "High" if finding_level == "Medium" else "Critical"
        
        # Ensure score is between 0 and 1
        score = max(0.0, min(1.0, score))
        
        return score, explanation, finding_level
    
    def map_to_frameworks(self, question: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Map a question to relevant framework controls
        
        Args:
            question: Dictionary containing question data
            
        Returns:
            Dictionary mapping framework names to lists of control IDs
        """
        question_text = question.get('question', '').lower()
        
        # Framework mapping results
        mappings = {}
        
        # Simple keyword-based mapping
        framework_keywords = {
            "iso27001": ["iso", "27001", "iso27001", "information security management", "isms"],
            "nist_csf": ["nist", "cybersecurity framework", "csf", "identify", "protect", "detect", "respond", "recover"],
            "pci_dss": ["pci", "dss", "payment", "card", "cardholder", "credit card"],
            "gdpr": ["gdpr", "eu", "personal data", "data subject", "processor", "controller", "dpia"],
            "hipaa": ["hipaa", "health", "phi", "protected health information", "covered entity"],
            "ccpa": ["ccpa", "california", "consumer privacy", "personal information", "opt-out"],
            "cis": ["cis", "critical security controls", "top 20", "benchmarks"],
            "hitrust": ["hitrust", "csf", "health", "trust"]
        }
        
        # Check framework keywords in question text
        for framework, keywords in framework_keywords.items():
            if any(keyword in question_text for keyword in keywords):
                mappings[framework] = ["auto-mapped"]
        
        # More sophisticated mapping using the policy files and embeddings would go here
        # This is a placeholder for more advanced mapping logic
        
        return mappings
    
    def assess_risk(self, questionnaire_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive risk assessment on questionnaire data
        
        Args:
            questionnaire_data: Processed questionnaire data
            
        Returns:
            Assessment results including risk scores, findings, and compliance status
        """
        # Extract questions
        if 'questions' not in questionnaire_data:
            return {
                'error': 'No questions found in questionnaire data',
                'risk_score': 0.5,  # Default medium risk
                'timestamp': datetime.now().isoformat(),
                'findings': []  # Add empty findings list to avoid KeyError
            }
        
        questions = questionnaire_data['questions']
        
        # Initialize assessment data
        assessment = {
            'timestamp': datetime.now().isoformat(),
            'overall_risk_score': 0,
            'risk_by_category': {},
            'findings': [],  # Ensure findings list exists
            'framework_compliance': {},
            'risk_details': {},
            'meta': {
                'num_questions': len(questions),
                'num_answered': sum(1 for q in questions if q.get('answer')),
                'source_format': questionnaire_data.get('metadata', {}).get('format', 'unknown')
            }
        }
        
        # Process each question
        category_scores = {}
        framework_controls = {}
        
        for i, question in enumerate(questions):
            # Skip questions without text
            if not question.get('question'):
                continue
                
            # Get category
            category = question.get('category') if question.get('category') else self.categorize_question(question)
            
            # Calculate question score
            score, explanation, finding_level = self.calculate_question_score(question)
            
            # Map to frameworks
            framework_mappings = self.map_to_frameworks(question)
            
            # Store the question assessment
            question_assessment = {
                'question_id': i,
                'question_text': question.get('question', ''),
                'answer': question.get('answer', ''),
                'category': category,
                'score': score,
                'explanation': explanation,
                'finding_level': finding_level,
                'framework_mappings': framework_mappings
            }
            
            # Add to findings if score is low enough
            if score < 0.6:
                finding = {
                    'id': f"F{i+1}",
                    'question_id': i,
                    'category': category,
                    'question_text': question.get('question', ''),
                    'level': finding_level,
                    'title': f"Risk in {category}: {question.get('question', '')[:60]}...",
                    'description': f"Question: {question.get('question', '')}\nAnswer: {question.get('answer', '')}\nExplanation: {explanation}",
                    'score_impact': 1.0 - score
                }
                assessment['findings'].append(finding)
            
            # Add to category scores
            if category not in category_scores:
                category_scores[category] = []
            category_scores[category].append(score)
            
            # Add to framework mappings
            for framework, controls in framework_mappings.items():
                if framework not in framework_controls:
                    framework_controls[framework] = {'mapped_controls': set(), 'scores': []}
                framework_controls[framework]['mapped_controls'].update(controls)
                framework_controls[framework]['scores'].append(score)
            
            # Store in risk details
            if category not in assessment['risk_details']:
                assessment['risk_details'][category] = []
            assessment['risk_details'][category].append(question_assessment)
        
        # Calculate overall category scores
        for category, scores in category_scores.items():
            avg_score = sum(scores) / len(scores) if scores else 0.5
            assessment['risk_by_category'][category] = {
                'score': avg_score,
                'num_questions': len(scores),
                'risk_level': self._get_risk_level(avg_score)
            }
        
        # Calculate framework compliance
        for framework, data in framework_controls.items():
            avg_score = sum(data['scores']) / len(data['scores']) if data['scores'] else 0.5
            assessment['framework_compliance'][framework] = {
                'compliance_score': avg_score * 100,  # Convert to percentage
                'num_controls_mapped': len(data['mapped_controls']),
                'mapped_controls': list(data['mapped_controls']),
                'compliance_level': self._get_compliance_level(avg_score)
            }
        
        # Calculate weighted overall risk score
        if category_scores:
            weighted_sum = 0
            total_weight = 0
            
            for category, scores in category_scores.items():
                category_avg = sum(scores) / len(scores) if scores else 0.5
                weight = self.RISK_CATEGORY_WEIGHTS.get(category, 0.05)  # Default weight for unknown categories
                weighted_sum += category_avg * weight
                total_weight += weight
            
            overall_score = weighted_sum / total_weight if total_weight > 0 else 0.5
            assessment['overall_risk_score'] = overall_score
            assessment['risk_level'] = self._get_risk_level(overall_score)
        else:
            assessment['overall_risk_score'] = 0.5
            assessment['risk_level'] = "Medium"
        
        # Generate advanced explanations
        assessment['key_factors'] = self._generate_key_factors(assessment)
        
        # Sort findings by impact
        if assessment['findings']:
            assessment['findings'].sort(key=lambda x: x['score_impact'], reverse=True)
        
        # Generate recommendations based on findings
        assessment['recommendations'] = self.generate_recommendations(assessment)
        
        return assessment

    def _get_risk_level(self, score: float) -> str:
        """Determine risk level from score"""
        if score >= 0.8:
            return "Low"
        elif score >= 0.6:
            return "Medium-Low"
        elif score >= 0.4:
            return "Medium"
        elif score >= 0.2:
            return "High"
        else:
            return "Critical"
    
    def _get_compliance_level(self, score: float) -> str:
        """Determine compliance level from score"""
        if score >= 0.9:
            return "Fully Compliant"
        elif score >= 0.75:
            return "Substantially Compliant"
        elif score >= 0.5:
            return "Partially Compliant"
        elif score >= 0.25:
            return "Minimally Compliant"
        else:
            return "Non-Compliant"
    
    def _generate_key_factors(self, assessment: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Generate key factors that influenced the risk score
        
        Args:
            assessment: Assessment results
            
        Returns:
            Dictionary with positive and negative factors
        """
        positive_factors = []
        negative_factors = []
        
        # Extract top performing categories
        top_categories = sorted(assessment['risk_by_category'].items(), 
                              key=lambda x: x[1]['score'], reverse=True)[:3]
        
        for category, data in top_categories:
            if data['score'] >= 0.7:
                positive_factors.append(f"Strong {category} controls ({data['score']:.0%} score)")
        
        # Extract worst performing categories
        bottom_categories = sorted(assessment['risk_by_category'].items(), 
                                key=lambda x: x[1]['score'])[:3]
        
        for category, data in bottom_categories:
            if data['score'] <= 0.6:
                negative_factors.append(f"Weak {category} controls ({data['score']:.0%} score)")
        
        # Extract specific findings
        critical_findings = [f for f in assessment['findings'] if f['level'] in ["Critical", "High"]]
        for finding in critical_findings[:3]:  # Top 3 critical findings
            negative_factors.append(f"{finding['level']} risk: {finding['title']}")
        
        # Add framework compliance factors
        compliant_frameworks = []
        non_compliant_frameworks = []
        
        for framework, data in assessment['framework_compliance'].items():
            if data['compliance_score'] >= 80:
                framework_name = {
                    'iso27001': 'ISO 27001',
                    'nist_csf': 'NIST CSF',
                    'pci_dss': 'PCI DSS',
                    'gdpr': 'GDPR',
                    'hipaa': 'HIPAA',
                    'ccpa': 'CCPA',
                    'cis': 'CIS Controls',
                    'hitrust': 'HITRUST CSF'
                }.get(framework, framework)
                compliant_frameworks.append(framework_name)
            elif data['compliance_score'] <= 50:
                framework_name = {
                    'iso27001': 'ISO 27001',
                    'nist_csf': 'NIST CSF',
                    'pci_dss': 'PCI DSS',
                    'gdpr': 'GDPR',
                    'hipaa': 'HIPAA',
                    'ccpa': 'CCPA',
                    'cis': 'CIS Controls',
                    'hitrust': 'HITRUST CSF'
                }.get(framework, framework)
                non_compliant_frameworks.append(framework_name)
        
        if compliant_frameworks:
            positive_factors.append(f"Good compliance with {', '.join(compliant_frameworks)}")
        
        if non_compliant_frameworks:
            negative_factors.append(f"Poor compliance with {', '.join(non_compliant_frameworks)}")
        
        return {
            'positive_factors': positive_factors,
            'negative_factors': negative_factors
        }
    
    def generate_recommendations(self, assessment: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate prioritized recommendations based on assessment findings
        
        Args:
            assessment: Assessment results
            
        Returns:
            List of recommendation objects
        """
        recommendations = []
        
        # Check if findings exist in the assessment
        if 'findings' not in assessment or not assessment['findings']:
            risk_by_category = assessment.get('risk_by_category', {})
            
            for category, data in risk_by_category.items():
                score = data.get('score', 0)
                if score < 0.7: 
                    priority = "High" if score < 0.5 else "Medium"
                    
                    recommendation = {
                        'id': f"R{len(recommendations)+1}",
                        'finding_id': "G1", 
                        'category': category,
                        'priority': priority,
                        'title': f"Improve {category} Controls",
                        'description': f"Enhance your {category} security controls to improve overall security posture.",
                        'detailed_actions': self._generate_detailed_actions(category, priority, "")
                    }
                    
                    recommendations.append(recommendation)
            
            # If no risk categories with low scores, generate generic recommendations
            if not recommendations:
                general_categories = ["Data Protection", "Access Control", "Vulnerability Management", 
                                    "Authentication", "Incident Response"]
                
                for i, category in enumerate(general_categories):
                    general_rec = {
                        'id': f"R{i+1}",
                        'finding_id': "G1",
                        'category': category,
                        'priority': "Medium",
                        'title': f"General {category} Improvements",
                        'description': f"Consider strengthening your {category} controls as a general security enhancement.",
                        'detailed_actions': self._generate_detailed_actions(category, "Medium", "")
                    }
                    recommendations.append(general_rec)
            
            return recommendations[:5]  # Return top 5 recommendations
        
        # Process each finding to generate recommendations if findings exist
        for finding in assessment['findings']:
            category = finding['category']
            level = finding['level']
            description = finding['description']
            
            # Generate recommendation based on finding
            if level in ["Critical", "High"]:
                priority = "High"
            elif level == "Medium":
                priority = "Medium"
            else:
                priority = "Low"
            
            # Standard recommendations by category
            recommendation_templates = {
                "Data Protection": {
                    "High": "Implement robust data protection controls including encryption of sensitive data at rest and in transit, data classification, and access restrictions.",
                    "Medium": "Review and enhance your data protection practices, focusing on proper data classification and handling procedures.",
                    "Low": "Continue to monitor and periodically review your data protection controls."
                },
                "Access Control": {
                    "High": "Establish strict access control policies based on least privilege principles, implement multi-factor authentication, and regular access reviews.",
                    "Medium": "Strengthen access control mechanisms with more granular permissions and improved monitoring.",
                    "Low": "Maintain and regularly review access control procedures."
                },
                "Vulnerability Management": {
                    "High": "Implement a comprehensive vulnerability management program including regular scanning, prioritized patching, and penetration testing.",
                    "Medium": "Enhance vulnerability scanning frequency and improve patch management timeframes.",
                    "Low": "Continue regular vulnerability assessments and ensure timely patching."
                },
                "Network Security": {
                    "High": "Strengthen network security with proper segmentation, advanced firewall rules, intrusion detection/prevention, and enhanced monitoring.",
                    "Medium": "Review network security architecture and improve monitoring capabilities.",
                    "Low": "Maintain network security controls and stay current with best practices."
                },
                "Authentication": {
                    "High": "Implement multi-factor authentication across all systems, particularly for privileged accounts and remote access.",
                    "Medium": "Strengthen authentication mechanisms and password policies.",
                    "Low": "Regularly review authentication controls for improvement opportunities."
                },
                "Encryption": {
                    "High": "Deploy strong encryption for all sensitive data, both at rest and in transit, with proper key management procedures.",
                    "Medium": "Expand encryption coverage and review key management practices.",
                    "Low": "Ensure encryption protocols remain up to date with current standards."
                },
                "Incident Response": {
                    "High": "Develop a formal incident response plan with defined roles, regular testing, and integration with detection systems.",
                    "Medium": "Enhance incident response procedures and conduct more frequent testing.",
                    "Low": "Continue to test and refine incident response capabilities."
                },
                "Business Continuity": {
                    "High": "Establish comprehensive business continuity and disaster recovery plans with regular testing and documentation.",
                    "Medium": "Improve business continuity planning and testing frequency.",
                    "Low": "Maintain and periodically review business continuity arrangements."
                }
            }
            
            # Get recommendation template
            if category in recommendation_templates and priority in recommendation_templates[category]:
                recommendation_text = recommendation_templates[category][priority]
            else:
                recommendation_text = f"Address the identified {priority} priority {category} issues to improve security posture."
            
            # Create recommendation object
            recommendation = {
                'id': f"R{len(recommendations)+1}",
                'finding_id': finding['id'],
                'category': category,
                'priority': priority,
                'title': f"Improve {category} Controls",
                'description': recommendation_text,
                'detailed_actions': self._generate_detailed_actions(category, priority, description)
            }
            
            recommendations.append(recommendation)
        
        # Deduplicate recommendations by category and priority
        unique_recommendations = {}
        for rec in recommendations:
            key = f"{rec['category']}_{rec['priority']}"
            if key not in unique_recommendations or rec['priority'] == "High":
                unique_recommendations[key] = rec
        
        # Add general recommendations if needed
        if len(unique_recommendations) < 3:
            general_categories = ["Data Protection", "Access Control", "Vulnerability Management", 
                                "Authentication", "Incident Response"]
            
            for category in general_categories:
                key = f"{category}_Medium"
                if key not in unique_recommendations and len(unique_recommendations) < 5:
                    general_rec = {
                        'id': f"R{len(unique_recommendations)+1}",
                        'finding_id': "G1",
                        'category': category,
                        'priority': "Medium",
                        'title': f"General {category} Improvements",
                        'description': f"Consider strengthening your {category} controls as a general security enhancement.",
                        'detailed_actions': self._generate_detailed_actions(category, "Medium", "")
                    }
                    unique_recommendations[key] = general_rec
        
        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        sorted_recommendations = sorted(unique_recommendations.values(), 
                                      key=lambda x: priority_order.get(x['priority'], 3))
        
        return sorted_recommendations
    
    def _generate_detailed_actions(self, category: str, priority: str, finding_description: str) -> List[str]:
        """
        Generate detailed actions for a recommendation
        
        Args:
            category: Risk category
            priority: Recommendation priority
            finding_description: Original finding description
            
        Returns:
            List of specific action items
        """
        # Standard actions by category
        standard_actions = {
            "Data Protection": [
                "Inventory and classify all sensitive data",
                "Implement encryption for sensitive data at rest",
                "Ensure secure transfer methods are used for all sensitive data",
                "Develop and enforce data retention and disposal policies",
                "Implement data loss prevention (DLP) technologies"
            ],
            "Access Control": [
                "Implement role-based access control (RBAC)",
                "Enforce least privilege access principles",
                "Conduct quarterly access reviews",
                "Implement privileged access management (PAM)",
                "Automate provisioning and deprovisioning processes"
            ],
            "Vulnerability Management": [
                "Perform regular vulnerability scanning of all systems",
                "Implement a risk-based patching strategy",
                "Conduct annual penetration testing",
                "Maintain an up-to-date asset inventory",
                "Implement a secure development lifecycle"
            ],
            "Network Security": [
                "Implement network segmentation",
                "Deploy next-generation firewalls",
                "Implement intrusion detection/prevention systems",
                "Monitor network traffic for anomalies",
                "Secure remote access with VPN and multi-factor authentication"
            ],
            "Authentication": [
                "Implement multi-factor authentication for all users",
                "Enforce strong password policies",
                "Consider passwordless authentication methods",
                "Implement single sign-on (SSO) where appropriate",
                "Regularly audit authentication logs"
            ],
            "Encryption": [
                "Enforce TLS 1.2+ for all communications",
                "Implement proper key management procedures",
                "Use strong encryption algorithms (AES-256)",
                "Encrypt all sensitive data at rest",
                "Regularly rotate encryption keys"
            ],
            "Incident Response": [
                "Develop a formal incident response plan",
                "Define clear roles and responsibilities",
                "Conduct regular tabletop exercises",
                "Implement security information and event management (SIEM)",
                "Establish relationships with external incident response experts"
            ],
            "Business Continuity": [
                "Develop business continuity and disaster recovery plans",
                "Identify critical systems and recovery time objectives",
                "Implement redundant systems for critical infrastructure",
                "Regularly test backup and recovery procedures",
                "Document and communicate recovery procedures"
            ]
        }
        
        if category in standard_actions:
            actions = standard_actions[category]
            
            if priority == "High":
                return actions[:5] 
            elif priority == "Medium":
                return actions[:3] 
            else:
                return actions[:2]  
        else:
            return ["Conduct a detailed assessment of current controls",
                    "Develop an improvement plan based on industry best practices",
                    "Implement enhanced security monitoring"]